import argparse
parser = argparse.ArgumentParser(description='process parse')
parser.add_argument('integers', metavar='N', type=int, nargs='+',help='an integer for accumulator')
parser.add_argument('--sum',dest='accumulate',action='store_const',const=sum,default=max,help='sum the ingeters default find the max')
args = parser.parse_args()
print(args.accumulate(args.integers))
proc_dir = args.procdir
print proc_dir