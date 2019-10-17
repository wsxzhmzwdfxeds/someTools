import pandas as pd
import paramiko as pk
# import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
import sys
import json

pk.util.log_to_file("paramiko.log")
# plt.rcdefaults()
# pd.set_option('display.max_columns', 100)
# pd.set_option('display.max_rows', 100)
# pd.set_option('display.width', 1000)
# pd.set_option('display.height', 1000)

class sysStat(object):
    def __init__(self):
        self.s1mple = dict()
        self.ssh = pk.SSHClient()
        self.ssh.set_missing_host_key_policy(pk.AutoAddPolicy())

    def _connect(self, hostname, user="root", port=22, passwd=None):
        self.hostIP = hostname
        # self.passwd = args[0] if args else None
        self.passwd = passwd
        if self.passwd:
            try:
                self.ssh.connect(self.hostIP, port=port, username=user, password=self.passwd, timeout=10)
            except Exception as e:
                print "password or port err!!"
                return e
        else:
            try:
                self.ssh.connect(self.hostIP, port=port, username=user, key_filename='../docs/id_rsa', timeout=10)
            except Exception as e:
                print "can't access with ssh public key!!"
                return e

        self.sftp = self.ssh.open_sftp()

    def _cmd(self, cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=10, get_pty=True)
            stdin.close()
            return stdout.read(), stderr.read()
            self.ssh.close()
        except Exception as e:
            print("error !")

    def _cpu_info(self):
        self.sftp.get("/proc/cpuinfo", "../sysinfo/cpuinfo")
        CPUinfo = OrderedDict()
        procinfo = OrderedDict()
        nprocs = 0
        ret = []
        with open("../sysinfo/cpuinfo") as f:
            for line in f:
                if not line.strip():
                    CPUinfo['proc%s' % nprocs] = procinfo
                    nprocs = nprocs + 1
                    procinfo = OrderedDict()
                else:
                    if len(line.split(":")) == 2:
                        procinfo[line.split(":")[0].strip()] = line.split(':')[1].strip()
                    else:
                        procinfo[line.split(":")[0].strip()] = ''
        for processor in CPUinfo.keys():
            ret.append(CPUinfo[processor]["model name"])
        return pd.DataFrame(ret, columns=["CPU"])

    def _load_stat(self):
        loadavg = {}
        self.sftp.get("/proc/loadavg", "../sysinfo/loadavg")
        f= open("../sysinfo/loadavg")
        con = f.read().split()
        f.close()
        loadavg['lavg_1'] = con[0]
        loadavg['lavg_5'] = con[1]
        loadavg['lavg_15'] = con[2]
        loadavg['nr'] = con[3]
        loadavg['last_pid'] = con[4]
        return "loadavg",loadavg['lavg_15']

    def _mem_info(self):
        meminfo = OrderedDict()
        self.sftp.get("/proc/meminfo", "sysStat/sysinfo/meminfo")
        with open('sysStat/sysinfo/meminfo') as f:
            for line in f:
                meminfo[line.split(':')[0]] = line.split(':')[1].strip()
        total = meminfo['MemTotal']
        free = meminfo['MemFree']
        precent = 1 - int(free.split()[0])/float(int(total.split()[0]))
        return pd.DataFrame([[self.hostIP, total, free, precent]], columns=["hostIP",
                                                                   "TotalMem",
                                                                   "FreeMem",
                                                                   "precent"]).set_index('hostIP')

    def getCpu(self):
        self.sftp.get("/proc/cpuinfo", "../sysinfo/cpuinfo")
        num = 0
        with open('../sysinfo/cpuinfo') as fd:
            for line in fd:
                if line.startswith('processor'):
                    num += 1
                if line.startswith('model name'):
                    cpu_model = line.split(':')[1].strip().split()
                    cpu_model = cpu_model[0] + ' ' + cpu_model[2] + ' ' + cpu_model[-1]
        return {'cpu_cores': num, 'cpu_model': cpu_model}

    def getMemory(self):
        self.sftp.get("/proc/meminfo", "../sysinfo/meminfo")
        with open('../sysinfo/meminfo') as fd:
            for line in fd:
                if line.startswith('MemTotal'):
                    mem = int(line.split()[1].strip())
                    break
        mem = '%.f' % (mem / 1024.0) + ' MB'
        return {'Memory': mem}

    def getOsVersion(self):
        self.sftp.get("/etc/redhat-release", "../sysinfo/redhat-release")
        with open("../sysinfo/redhat-release") as fd:
            for line in fd:
                osVer = line.strip()
        klVer, _ = self._cmd('uname -r')
        return {'OSVersion': osVer, 'KLVersion': klVer.strip()}

    def setDisk(self):
        diskInfo, _ = self._cmd('fdisk -l')
        try:
            with open('../sysinfo/disk', 'w') as fd:
                fd.write(diskInfo)
        except IOError:
            print "IOError"
        else:
            fd.close()

    def formatDisk(self, device, size, disdic):
        disdic[device.split("/")[2][:-1]] = size + ' GB'

    def getDisk(self):
        disInfo = dict()
        self.setDisk()
        with open('../sysinfo/disk') as fd:
            for line in fd:
                if line.startswith('Disk') and line.strip().endswith('sectors'):
                    if line.split()[1].find("mapper") == -1:
                        self.formatDisk(line.split()[1], line.split()[2], disInfo)
        return disInfo

    def gather(self):
        self.s1mple[self.hostIP] = {}
        self.s1mple[self.hostIP]["OS"] = self.getOsVersion()
        self.s1mple[self.hostIP]["CPU"] = self.getCpu()
        self.s1mple[self.hostIP].update((self.getMemory()))
        self.s1mple[self.hostIP]["DISK"] = self.getDisk()
        print self.hostIP + ' gather success'
        return self.s1mple

servers = sysStat()


class Yc_info(object):
    def __init__(self):
        self.col = []
        for i in range(15, 48):
            self.col.append(i)

    def _all_mem_info(self):
        data = pd.DataFrame()
        for i in range(15, 48):
            server = sysStat("10.19.248.%d" % i)
            data = data.append(server._mem_info())
        return data

    def _plt_mem_info(self):
        self._all_mem_info()['precent'].plot(kind='bar', figsize=(15, 20))
        plt.show()

    def _label_fucked(self):
        fucked = []
        data = self._all_mem_info().sort_values(by=['precent'])
        for i in range(0, 10):
            fucked.append(data.index[i])
        return fucked

class sys_performance(object):
    def __init__(self, hostIP, *args):
        self.ret = []
        self.s = sysStat(hostIP, *args)

    def _perfom(self):
        self.ret.append(self.s._cmd("uptime")[0])
        self.ret.append(self.s._cmd("dmesg|tail")[0])
        self.ret.append(self.s._cmd("vmstat 1")[0])