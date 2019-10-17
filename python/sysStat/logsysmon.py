import os
import argparse
import re
from time import sleep, strftime, time
# import requests
import json


parser = argparse.ArgumentParser()
parser.add_argument("--procdir", type=str, help="Where the proc dir located.", default="/proc")
parser.add_argument("--target", type=str, help="The target node the mon is running on.", default="mytest")
parser.add_argument("--interval", type=int, help="Chcek interval.", default=60)
parser.add_argument("--containersdir", type=str, help="docker data dir", default="/opt/containers")
parser.add_argument("--netstat", type=str, help="Where the netstat file located.", default="/proc/net/netstat")

args = parser.parse_args()
proc_dir = args.procdir
target = "-".join(args.target.split("."))

interval = args.interval
MAX_BAD_PROCESS = 128
containers = args.containersdir
netstat = args.netstat
LOG_DIR = "/var/log/sysmon"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def report(errors):
    # save to log file
    errors['timestamp'] = int(time())
    errors['target'] = target
    log_filename = "%s/%s-%s" % (LOG_DIR, target, strftime("%Y-%m"))
    with open(log_filename, "aw") as f:
        f.write(json.dumps(errors) + "\n")


def collect_netstats():
    tcp_headers = None
    tcp_values = None
    ip_headers = None
    ip_values = None
    with open(netstat, "r") as f:
        for l in f:
            if "TcpExt:" in l:
                if tcp_headers is None:
                    tcp_headers = l.split()[1:]
                else:
                    tcp_values = l.split()[1:]
            if "IpExt:" in l:
                if ip_headers is None:
                    ip_headers = l.split()[1:]
                else:
                    ip_values = l.split()[1:]

    r = {}
    if tcp_headers and tcp_values:
        for n, v in zip(tcp_headers, tcp_values):
            r[n] = int(v)
    if ip_headers and ip_values:
        for n, v in zip(ip_headers, ip_values):
            r[n] = int(v)
    return r


def calc_memory():
    total = 0
    mem_available = 0
    mem_slab = 0
    with open("/proc/meminfo", 'r') as f:
        for l in f:
            p = l.split()
            if len(p) < 2:
                continue
            tag = p[0]
            s = int(p[1])
            if "MemTotal" in tag:
                total = s
            if "MemAvailable" in tag:
                mem_available = s
            if "Slab" in tag:
                mem_slab = s
    avail_percent = 0
    mem_slab_percent = 0
    if total != 0:
        avail_percent = mem_available * 100 / total
        mem_slab_percent = mem_slab * 100 / total
    return avail_percent, mem_slab_percent


def checkit():
    prefix = strftime("%Y-%m-%d %H:%M")
    # count docker containers
    try:
        cc = len(os.listdir(containers))
    except:
        cc = 0
    # count dead and zombie process
    pids = [pid for pid in os.listdir(proc_dir) if pid.isdigit()]
    deads = 0
    zombies = 0
    ec = 0
    errors = []
    for pid in pids:
        try:
            s = open(os.path.join(proc_dir, pid, 'stat'), 'r').read()
            v = re.split("\s+", s)
            if len(v) < 3:
                continue
            state = v[2]
            ppid = v[3]
            if state not in ['D', 'Z']:
                continue
            name = v[1]
            # read parent process cgroup
            cgroup_location = "NA"
            s = open(os.path.join(proc_dir, ppid, 'cgroup'), 'r').read()
            for l in s.split("\n"):
                if "memory" in l:
                    cgroup_location = l.split(":")[2]
            if (name, state, cgroup_location) not in errors:
                errors.append((name, state, cgroup_location))
            if state == 'D':
                deads += 1
            else:
                zombies += 1
            ec += 1
            # only collect
            if ec > MAX_BAD_PROCESS:
                break
        except IOError:  # proc has already terminated
            continue
    for n, s, c in errors:
        print(prefix, n, s, c)
    # calc available memory and allocated slab
    avail_percent, mem_slab_percent = calc_memory()
    r = collect_netstats()
    r.update({
        "deadprocess": deads,
        "zombieprocess": zombies,
        "containers": cc,
        "availablememory": avail_percent,
        "slabmemory": mem_slab_percent,
    })
    return r


def main():
    while True:
        report(checkit())
        sleep(interval)


if __name__ == "__main__":
    main()

