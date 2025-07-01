import socket
import os
import astropy.io.fits as fits
import time
import numpy as np


TCPIP='10.103.154.4'
PORT= 54321
BUFFER_SIZE = 512
TMPFITS= '/home/rabi/temp1/kuroTemp/temp.fit'

class camera():
    def __init__(self):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TCPIP,PORT))
            ml='alive?'
            s.send(ml.encode())
            #a=s.recv(5)
            s.close()
            print("camera connected")
        except:
            print('Camera connect failed')

    def shoot(self,nframes):
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((TCPIP,PORT))
        ml='acquire'+str(nframes)
        s.send(ml.encode())

    def read(self):
        t=0
        while not (os.path.exists(TMPFITS)):
            time.sleep(0.1)
            t=t+1
            if (t>100): break
        hdu=fits.open(TMPFITS)
        imgdata=hdu[0].data
        outdata=np.array(imgdata)
        hdu.close()
        os.remove(TMPFITS)
        return outdata
    def plot(self,data,npics):
        import matplotlib.pyplot as plt
        realdata=data[0,:,:]
        if (npics==1):
            plt.imshow(realdata)#, cmap=cm.jet, aspect='auto')
            plt.show()

if __name__=='__main__':
    #import DAQ
    #EDRE=DAQ.EDRE_Interface()
    cam=camera()
    cam.shoot(1)
    time.sleep(0.1)
    #EDRE.writeChannel(0,19,5000000)
    time.sleep(0.01)
    #EDRE.writeChannel(0,19,0)
    a=cam.read()
    cam.plot(a,1)
    print(a.shape)

