import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import kicklib
import pyinotify

fn='/home/lab/picshare/temp.fits'

def roundstr(x,n):
    if not n:
        return str(int(round(x,0)))
    else:
        return str(round(x,n))

class ModHandler(pyinotify.ProcessEvent):
    # evt has useful properties, including pathname
    def process_IN_CLOSE_WRITE(self, evt):
        #data=[]
        plt.close('all')
        with open(fn,'rb') as file:
          a = fits.open(file)
          data = a[0].data
          
        FG = data[0,:,:]
        BG = data[1,:,:]
        empty = data[2,:,:]

        #mask = np.ones(FG.shape, dtype=int)
        #mask[10:FG.shape[0]-10, 10:FG.shape[1]-10] = 0
        #topnorm = np.mean(FG[mask]); botnorm = np.mean(BG[mask])
        #ratio = botnorm/topnorm

        plt.figure()
        #plt.imshow(FG*ratio, cmap = cm.inferno)
        plt.imshow(FG-BG, cmap = cm.inferno)
        plt.colorbar()
        plt.title('Subtracted')
        plt.show()





handler = ModHandler()

plt.ion()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(fn, pyinotify.IN_CLOSE_WRITE)
notifier.loop()