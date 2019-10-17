from otsdb_client import client

class OpenTSDB(object):
    def __init__(self, server='10.19.248.200', port=30142):
        self.server = server
        self.port = port
        self.c = client.Connection(server = self.server,
                              port = self.port)

    def query_io(self):
        io_list = {}
        for host in range(12, 48):
            io = self.c.query(queries=[{'m': 'diskio_bytes_Total',
                               'aggr': 'sum',
                               'tags': {'host': '10.19.248.%d' % host, 'container_name':'/'},
                               'rate': True,
                               }
                               ],
                     start='1h-ago',
                     end='now',)['results'][0]['values']
            io_list['10.19.248.%d' % host] = (sum(io) / float(len(io)))

        items = io_list.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()

        return [backitems[i][1] for i in range(0, len(backitems))]

    def query_mem(self):
        io_list = {}
        for host in range(12, 48):
            io = self.c.query(queries=[{'m': 'memory_working_set',
                               'aggr': 'sum',
                               'tags': {'host': '10.19.248.%d' % host, 'container_name':'/'},
                               'rate': False,
                               }
                               ],
                     start='1h-ago',
                     end='now',)['results'][0]['values']
            io_list['10.19.248.%d' % host] = (sum(io) / float(len(io)))

        items = io_list.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()

        return [backitems[i][1] for i in range(0, len(backitems))]

    def query_cpu(self):
        io_list = {}
        for host in range(12, 48):
            io = self.c.query(queries=[{'m': 'cpu_total',
                               'aggr': 'sum',
                               'tags': {'host': '10.19.248.%d' % host, 'container_name':'/'},
                               'rate': True,
                               }
                               ],
                     start='1h-ago',
                     end='now',)['results'][0]['values']
            io_list['10.19.248.%d' % host] = (sum(io) / float(len(io)))

        items = io_list.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()

        return [backitems[i][1] for i in range(0, len(backitems))]

    def query_network_rcv(self):
        io_list = {}
        for host in range(12, 48):
            io = self.c.query(queries=[{'m': 'network_rcv_bytes',
                               'aggr': 'sum',
                               'tags': {'host': '10.19.248.%d' % host, 'container_name':'/'},
                               'rate': True,
                               }
                               ],
                     start='1h-ago',
                     end='now',)['results'][0]['values']
            io_list['10.19.248.%d' % host] = (sum(io) / float(len(io)))

        items = io_list.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()

        return [backitems[i][1] for i in range(0, len(backitems))]


    def query_network_snd(self):
        io_list = {}
        for host in range(12, 48):
            io = self.c.query(queries=[{'m': 'network_snd_bytes',
                               'aggr': 'sum',
                               'tags': {'host': '10.19.248.%d' % host, 'container_name':'/'},
                               'rate': True,
                               }
                               ],
                     start='1h-ago',
                     end='now',)['results'][0]['values']
            io_list['10.19.248.%d' % host] = (sum(io) / float(len(io)))

        items = io_list.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()

        return [backitems[i][1] for i in range(0, len(backitems))]