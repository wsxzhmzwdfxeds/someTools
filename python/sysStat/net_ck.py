import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict
from sysStat import sysStat
plt.rcdefaults()
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)
pd.set_option('display.height', 1000)

class Net_ping(object):
    def __init__(self, hostIp, passwd, prefix, first, last):
        self.hostIp = hostIp
        self.Ips = self._get_ip(prefix, first, last)
        self.s = sysStat(hostIp, passwd)

    def _run(self):
        self.avg = []
        for ip in self.Ips:
            msg =  self._ping(ip)
            self.avg.append(msg.splitlines()[-1].split("/")[4])
        return {self.hostIp:self.avg},self.Ips

    def _ping(self, ip):
        return self.s._cmd('ping %s -c 10' % ip)[0]

    def _get_ip(self, prefix, first, last):
        ip_list = []
        for i in range (first, last+1):
            ip_list.append(prefix+'%d' % i)
        return ip_list