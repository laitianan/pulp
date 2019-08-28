# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 15:33:59 2019

@author: tianan.lai
"""

import sys,argparse
def parse_args():
    
    if len(sys.argv) == 1:
        sys.argv.append('-h')   
    parser = argparse.ArgumentParser()
    parser.add_argument('-quit', help="y表示终止计算",choices=['y', 'n'],default='n')
    args = vars(parser.parse_args())
    return args

def kill():
    import os,signal
    out=os.popen("ps aux | grep pulp/solverdir").read()
    for line in out.splitlines():
        try:
            pid = int(line.split()[1])
            os.kill(pid,signal.SIGKILL)
        except Exception as e:
            print(e)
            pass

if __name__=="__main__":
    args=parse_args()
    q=args['quit']
    if q=='y':
        kill()
        