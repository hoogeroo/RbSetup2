import pylablib as pll
from pylablib.devices import PrincetonInstruments
import matplotlib.pyplot as plt
import numpy as np
import time
from astropy.io import fits

def shoot(cam,N,triggered=True):
    cam.setup_acquisition(mode="sequence", nframes=N)
    cam.set_exposure(0.01) # 10 ms I suppose
    if triggered:
        cam.set_trigger_mode("ext")
        time.sleep(0.01)
    cam.start_acquisition()

def read(cam,N):
    out=np.zeros((N,512,512))
    for i in range(N):
        print("waiting for frame ",i)
        cam.wait_for_frame()
        frame=cam.read_oldest_image()
        out[i,:,:]=np.array(frame)
    cam.stop_acquisition()
    return out
    
def save(data):
    hdu=fits.PrimaryHDU(data)
    #hdul=fits.HDUList([hdu])
    fn = f'X:\\temp.fits'
    hdu.writeto(fn)
    print("Written to ", fn)
	
def run(cam):	
    cam.setup_acquisition(mode="sequence", nframes=12)  # could be combined with start_acquisition, or kept separate
    cam.start_acquisition()
    i=0
    plt.figure()
    while i<12:  # acquisition loop
        plt.subplot(3,4,i+1)
        cam.wait_for_frame()  # wait for the next available frame
        frame = cam.read_oldest_image()  # get the oldest image which hasn't been read yet
		# ... process frame ...
		#if time_to_stop:
		#	break
        #print(frame)
        npframe=np.array(frame)
        plt.imshow(npframe)
        i=i+1
  
    cam.stop_acquisition()
	
if __name__=="__main__":
    cam1=PrincetonInstruments.PicamCamera()
    #shoot(cam1,3,triggered=False) #camera 1 (big camera), take 3 pictures, triggered = false
    shoot (cam1,3,triggered=True)   
    data=read(cam1,3)
    save(data)
    for i in range(3):
        plt.subplot(3,1,i+1)
        plt.imshow(data[i,:,:])
    #run(cam1)
    plt.show()
    cam1.close()
    