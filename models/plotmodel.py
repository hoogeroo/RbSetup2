#!/usr/local/anaconda3/bin/python
import numpy as np
import matplotlib.pyplot as plt
import sys
myid=sys.argv[1]
fn=myid+'/'+myid+"_data.csv"
a=np.genfromtxt(fn,skip_header=1,delimiter=',')
plt.scatter(a[:,0],a[:,1])
plt.show()

