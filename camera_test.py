import socket
import os
import astropy.io.fits as fits
import time
import numpy as np


TCPIP='10.103.154.4'
PORT= 54321
BUFFER_SIZE = 512
TMPFITS= '/home/lab/zdrive/kuroTemp/temp.fit'

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
            self.BGpics=np.zeros((512,512,50))
            self.BGindex=0
            self.nBGs=0
            self.BGmask=np.zeros((512,512),dtype='int')
            self.BGmask[0:50,0:50]=1
            self.BGmask[0:50,(512-50):512]=1
            self.BGmask[(512-50):512,0:50]=1
            self.BGmask[(512-50):512,(512-50):512]=1
            self.Natoms=[]
            self.ODpeak=[]
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
        #os.remove(TMPFITS)
        return outdata
    
    def getNatoms_otf(self,odimage,npts=512):
        #onepixel=25e-6*2.0/3.0
        onepixel=16e-6 * 2.0/3.0
        A_of_px=onepixel**2
        Rb_crosssection = 1.3e-13 # See Ian Wenas' MSc thesis from 2007, pg65
        N_atoms = round(A_of_px * np.sum(odimage) / Rb_crosssection, 2)
        n = float(N_atoms)
        keys = ['K', 'M', 'B', 'T']
        count = 0
        for div in range(0, len(keys)):
          n = n/1000
          count += 1
          if n < 1000:
            break
        N_atoms = str(round(n, 2)) + keys[count - 1]
        NMax = round(np.max(odimage), 2)
        return N_atoms,NMax, n
    
    def getNatoms(self,Sdata,ns=3,co=50,npts=512):
        # ns is the number of shots, normally 3 for absorption measurements, co is size of the corner part that we use for background subtraction, 
        # and np is the number of pixels
        #ns=Sdata.shape[0]
        #co=50
        #np=512
        #print('NS is ',ns,ns.shape)
        if ns==3:
            thedata=-np.log((Sdata[0,:,:]-Sdata[2,:,:])/(Sdata[1,:,:]-Sdata[2,:,:]))
            one=np.mean(thedata[0:co,0:co])
            two=np.mean(thedata[npts-co:npts,0:co])
            three=np.mean(thedata[0:co,npts-co:npts])
            four=np.mean(thedata[npts-co:npts,npts-co:npts])
            print(four)
            BG=np.mean(np.array([one,two,three,four]))
            thedata=thedata-BG
            onepixel=16e-6*2.0/3.0
            A_of_px=onepixel**2
            Rb_crosssection = 1.3e-13 # See Ian Wenas' MSc thesis from 2007, pg65
            N_atoms = round(A_of_px * np.sum(thedata) / Rb_crosssection, 2)
            n = float(N_atoms)
            keys = ['K', 'M', 'B', 'T']
            count = 0
            for div in range(0, len(keys)):
              n = n/1000
              count += 1
              if n < 1000:
                break
            N_atoms = str(round(n, 2)) + keys[count - 1]
            NMax = round(np.max(thedata), 2)
            return N_atoms,NMax
        else: 
            return 0
        
    def plot(self,data,npics):
        import matplotlib.pyplot as plt
        realdata=data[0,:,:]
        if (npics==1):
            plt.imshow(realdata)#, cmap=cm.jet, aspect='auto')
            plt.show()

if __name__=='__main__':
    import DAQ
    EDRE=DAQ.EDRE_Interface()
    cam=camera()
    cam.shoot(1)
    time.sleep(0.1)
    EDRE.writeChannel(0,19,5000000)
    time.sleep(0.01)
    EDRE.writeChannel(0,19,0)
    a=cam.read()
    cam.plot(a,1)
    print(a.shape)
    
