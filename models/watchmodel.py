#!/usr/local/anaconda3/bin/python
import numpy as np
import matplotlib.pyplot as plt
import sys
import pyinotify.adapters

def main():
    i=pyinotify.adapters.Inotify()
    myid=sys.argv[1]
    i.add_watch(myid)
    for event in i.event_gen(yield_nones=False,timeout=1):
       print(event)

def doplot():
    fn=myid+'/'+myid+"_data.csv"
    a=np.genfromtxt(fn,skip_header=1,delimiter=',')
    plt.scatter(a[:,0],a[:,1])
    plt.show()
    plt.scatter(a[:,4],a[:,1])
    plt.show()

if __name__=='__main__':
    main()
