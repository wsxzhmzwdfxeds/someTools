"""
This script use mtr to test package loss for sending traffic in a single channel.
"""
from k8sclient.keywords import (
    list_ready_nodes,
    get_pod_ip,
    wait_for_pod_state,
    RUNNING,
    SUCCEEDED,
    tail_pod_logs,
    delete_pod,
    remove_pod,
    NOT_FOUND,
    register_cluster,
    switch_cluster,
    cleanup_pods,
    cleanup_services,
)
from k8sclient.Components import PodBuilder, ServicePort, ServiceBuilder
import re
import time
import sys

packet_type = '--tcp'
interval = 1

if len(sys.argv) > 1:
    interval = sys.argv[1]
if len(sys.argv) > 2:
    packet_type = sys.argv[2]

server_args = "mtr -rwc 30 " + packet_type + " -i " + str(interval)
namespace = "health-check"
image = "127.0.0.1:29006/tools/package-loss:1.0"
nodes = sorted(list_ready_nodes())
glimit = {'cpu': '0', 'memory': '0'}
grequest = {'cpu': '0', 'memory': '0'}
reports = []
report_css = """<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
tr:nth-child(even) {background: #CCC}
tr:nth-child(odd) {background: #FFF}
</style>
"""
report_title = r"""<H1>Pod to Pod network package loss and latency, single connection. (ms)</H1>
<br>
CPU limit: <b>no limit</b>
<br>
Memory Limit: <b>no limit</b>
<br>
MTR cmd: <b>%s</b>
<br>
<br>
""" % server_args


def save_report():
    ths = ['Loss%', 'Snt', 'Last', 'Avg', 'Best', 'Wrst', 'stDev']
    with open("/usr/share/nginx/html/report.html", "w") as f:
        f.write(report_css)
        f.write(report_title)
        f.write("<dl><dt><b>package lost and latecy</b></dt>\n")
        f.write("<br>\n")
        for report in reports:
            report.pop(0)
            temp_var = report.pop(0)
            title = temp_var.split()[1]
            f.write("<dd>{}</dd>\n".format(title))
            f.write("<dd>\n")
            f.write("<table><tr><th>MTR</th>\n")
            for th in ths:
                f.write("<th>{}</th>\n".format(th))
            f.write("</tr>\n")
            for items in report:
                f.write("<tr>\n")
                items = items.split()[1:]
                for item in items:
                    f.write("<td>{}</td>\n".format(item))
                f.write("</tr>\n")
            f.write("</table>\n")
            f.write("</dd>\n")
            f.write("<br>\n")
        f.write("</dl>\n")


def deploy(node):
    node_mark = "-".join(node.split("."))
    args = server_args + ' ' + node
    for i in nodes:
        if i == node:
            continue
        pod_name = ("%s--%s" % ("-".join(i.split(".")), node_mark))
        pod = PodBuilder(
            pod_name,
            namespace,
        ).set_node(
            i
        ).add_container(
            pod_name,
            image=image,
            args=args,
            requests=grequest,
            limits=glimit,
        )
        try:
            for n in xrange(2):
                pod.deploy()
                wait_for_pod_state(namespace, pod_name, timeout=600, expect_status=SUCCEEDED)
                time.sleep(20)
                logs = tail_pod_logs(namespace, pod_name, lines=20).strip()
                print logs
                if logs:
                    reports.append(logs.splitlines())
                    break
                remove_pod(namespace, pod_name)
        except:
            print 'create pod error!!'
        finally:
            remove_pod(namespace, pod_name)


def cleanup():
    cleanup_pods(namespace=namespace)


cleanup()
# deploy(nodes[0])
for node in nodes:
    deploy(node)
save_report()
