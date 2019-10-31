import re
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")

(options, args) = parser.parse_args()

filename = options.filename
p = re.compile(".*Memory cgroup stats for /kubepods.*/pod([^/]+)/.*")

pods = []
with open(filename) as f:
    for l in f:
        m = p.match(l)
        if not m:
            continue
        if m.group(1) not in pods:
            pods.append(m.group(1))

for p in pods:
    print p

