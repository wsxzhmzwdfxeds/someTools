from otsdb_client import client
import os,time,logging
import datetime
import multiprocessing
logger = logging.getLogger("lag")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
logger.setLevel(logging.INFO)

class ping_lag(object):
    def __init__(self):
        self.std_client = client.Connection('10.19.140.200', 29430)
        self.ip_list = ['10.19.140.4','10.19.140.7','10.19.140.9','10.19.140.12','10.19.140.15']
        for i in range(140,160):
            self.ip_list.append('10.19.137.%d' % i)

    def _run(self):
        pool = multiprocessing.Pool(processes=5)
        for ip in self.ip_list:
            ping_str = os.popen("ping %s -c 5" % ip).read()
            logger.info(ping_str)
            try:
                avg_lag = ping_str.splitlines()[-1].split('/')[4]
            except IndexError as e:
                logger.exception("index error")
            else:
                pool.apply_async(self._to_std(avg_lag, self._get_ip(), ip),(ip,))
        pool.close()
        pool.join()

    def _to_std(self, value, from_ip, to_ip):
        now = datetime.datetime.now()
        logger.info("%s : from %s to %s , and the value is %s" % (now,from_ip,to_ip,value))
        self.std_client.put(metric='icy_lag', values=[value],tags={"from":from_ip,"to":to_ip})

    def _get_ip(self):
        return os.popen('echo $HOST_IP').read().strip()

if __name__ == '__main__':
    pl = ping_lag()
    while True:
        pl._run()
        time.sleep(600)
        logger.info("waiting for 10min")