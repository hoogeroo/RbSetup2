import glob
import os
import time
import copy
import socket
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit
from threading import Thread

import kicklib as klib
import kicklib1 as kl1

IP_BFCAM = '10.103.154.4'
PORT_BFCAM = 65432

def gauss(x,h,w,x0,o):
    return o + np.abs(h)*np.exp(-(x-x0)**2/w**2)
  
def gauss_2d(xy, h, wx, wy, x0, y0, o): #, theta):
    x, y = xy
    xo = float(x0)
    yo = float(y0)    
    a = wx**-2 # (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = 0 # -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = wy**-2 # (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = o + h*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                            + c*((y-yo)**2)))
    return g.ravel()
  
#class roidialog(QDialog):
  #def __init__(self,dims,center):
    #self.dims=dims
    #self.center=center
    


class blackfly():
  def __init__(self):
    self.thepath='/home/lab/picshare/*'
    #self.fitflag=True#False #True#
    self.lowpassflag=True#False#True#
    self.fringeflag=False
    self.contourflag = False
    self.surf_flag = False
    print(f'Note: blackfly.py\'s low-pass filter is currently set to {self.lowpassflag}')
    #self.roi=[680,1080,850,1450]
    #self.dims=[self.roi[1]-self.roi[0], self.roi[3]-self.roi[2]]
    self.dims = [550,550]#[1000, 1000]#[400,600] # y/rows, x/cols
    self.center= [675,1100]#[880,1150] # y/rows, x/cols
    self.roi=self.get_roi()#[int(self.center[i]+a*self.dims[i]) for i in range(2) for a in [-0.5, 0.5]]
    self.data=np.zeros((3,self.dims[0],self.dims[1])) # Moved this into the 'show' method, should forcibly update if aspect ratio changes!
    #Moved this back here as we get a crash when we try to save with no data
    self.OD_fig = []
    
    self.ODpeak = []
    self.Natoms = []
    #self.data= np.zeros(self.dims)
    self.server = None # when we connect to other computer/bfcam 'server', we place the socket here
    self.connected = False
    self.stream_on = False
    self.conn()
    if self.connected:
      self.change_roi()
    
    self.usefits = True# set to False for old readfiles() function; True loads array directly from readfits()
  
  def get_roi(self, center=None, sidelengths=None): # center and sidelengths both lists of two numbers - [Y/row,X/col] center, [Ly/rows, Lx/cols] sidelengths
    if not center:
      center = self.center
    if not sidelengths:
      sidelengths = self.dims
    roi = [int(center[i]+a*sidelengths[i]) for i in range(2) for a in [-0.5, 0.5]]
    #print(roi)
    return roi
  
  #=============================================================================================================
  # SERVER STUFF
  def conn(self):
    s = socket.socket()
    s.settimeout(2)
    try:
      s.connect((IP_BFCAM, PORT_BFCAM))
      self.server = s
      self.connected = True
    except:
      self.connected = False
  
  def exit_server(self):
    self.server.send('EXIT'.encode())
    self.disconn()
  
  def disconn(self):
    #self.exit_server()
    try:
      self.server.close()
    except:
      print("not connected to blackfly")
      pass
    self.server = None
    self.connected = False
    self.stream_on = False
    
  def change_roi(self):
    roivals = ''
    for val in self.roi:
      roivals += f',{str(val)}' 
    if self.connected:
      self.server.send(f'ROI{roivals}'.encode())
    
  def take_pics(self):
    self.remove_old_photos()
    if self.connected:
      self.server.send('TAKE_PICS'.encode())
    
  def start_stream(self):
    self.stream_on = True
    if self.connected:
      self.server.send('CYCLE'.encode())
    
  def end_stream(self):
    self.stream_on = False
    if self.connected:
      self.server.send('STOP_CYCLE'.encode())
    
  def req_fluo(self):
    if self.connected:
      self.server.send('FLUO'.encode())
      result = self.server.recv(100)
      nums = self.find_floats(result.decode()) # Only necessary if the buffer we receive potentially has a mixture of strings and floats
    else:
      nums=0
    if type(nums) is list:
      nums = float(nums[0])
    #print(f'Fluorescence: {nums}\nRescaled Fluo: {10000*nums/65536}')
    return 10000*nums/65536 # As 0 <= nums <= 2^(16)-1, this returns a float between 0 and <10000
    
  def find_floats(self,s):
    floats = re.findall(r"[-+]?(?:\d*\.*\d+)", s.strip())
    return floats
    
  
    
    
  #=============================================================================================================
  
  def readfits(self,filename):
    import astropy.io.fits as fits
    succeeded = False
    reattempt = 0
    n_attempts = 10
    while not succeeded and reattempt<n_attempts:
      try:
        with open(filename, 'rb') as file:
          fitsfile = fits.open(file)
          data = fitsfile[0].data # This is a [3, nx, ny] array from the camera output!
        succeeded = True
      except Exception as e:
        reattempt+=1
        print(f'{e}\nAttempts so far:{reattempt}')
        time.sleep(1)
        
    if not succeeded:
      print(f'MAX FILE READ ATTEMPTS EXCEEDED (Max attempts: {n_attempts})\n ')
      return False
        
    return data
  
  def readfile(self,filename):
    success=0
    while not success:
      trycounter=0
      try:
        trycounter+=1
        a=plt.imread(filename)
        success+=1
      except:
        time.sleep(0.1)
      if trycounter>5 and not success:
        print("Trouble reading file:", filename,"\n")
        a=0    
    return(a)
    
  #==============================================================================================================
  
  def findfiles(self):
    a=sorted(glob.glob(self.thepath))
    #print(a)
    return a
    
  #==============================================================================================================
  
  def remove_old_photos(self):
    # Find files at path (picshare, where we save photos) with particular format (*.pgm) using glob
    fs = sorted(glob.glob(self.thepath))#self.findfiles()
    # Remove files
    for f in fs:
      os.remove(f)
    
  #==============================================================================================================
  def show2(self,nshots,BGimages,nBG):
    t1=Thread(target=self.show2,args=[nshots,BGimages,nBG])
    t1.start()
    t1.join()
    return BGimages
  
  
  def show(self,nshots,BGimages,nBG):
    self.data=np.zeros((3,self.dims[0],self.dims[1]))
    def roundstr(x,n):
        if not n:
            return str(int(round(x,0)))
        else:
            return str(round(x,n))
    fs=[]
    i=0
    n_tries = 11
    if self.usefits:
      nfiles = 1
    else:
      nfiles = nshots
    filesfound=False
    while i < n_tries:
      fs=self.findfiles()
      if len(fs) == nfiles:
        filesfound = True
        break
      i=i+1
      time.sleep(1)
      
    if not filesfound:
      print(f'Not enough files in picshare!\n Needed {nfiles}, found {len(fs)} (self.usefits = {self.usefits})')
      return None
    
    if nshots==3:
      BGimages=self.plot_fringeremoval(fs,nshots,BGimages,nBG)
    elif nshots==2:
      self.plotFluo(fs)
    return BGimages
      
  def plotFluo(fs):    
      pic2=self.readfile(fs[-1])
      pic=self.readfile(fs[-2])
      
      self.data[0,:,:]=pic[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
      self.data[1,:,:]=pic2[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
      mydiff=(self.data[0,:,:]-self.data[1,:,:]).astype(np.float32)
      if self.lowpassflag:
        cutout=klib.filter_mask2(mydiff)
      else:
        cutout=mydiff
      
      print('Made it to blackfly pre-plot debug!')
      
      fig = plt.figure()
      plt.imshow(cutout)
      if self.contourflag:#self.fitflag:
          height,wx,wy=self.gaussfit(cutout)
          if sum([x is None for x in [height,wx,wy]])>0:
              plt.title("Fits failed")
          else:
              plt.title("Width = {}x, {}y; N_est = {}".format(roundstr(wx,0),roundstr(wy,0),roundstr(wx*wy*height/1000,0)))#,roundstr(wy*py[0]/1000,0)))
      else:
          print('Gaussian fits currently disabled - see \'self.fitflag\' in blackfly.py')
      
      plt.xlabel('X (pixels)')
      plt.ylabel('Y (pixels)')
      self.OD_fig = fig
      #plt.draw() # Apparently this is preferred over show() for gui applications
      plt.show()
     
  
  def plot_fringeremoval(self,fs,nshots,BGimages,nBG):
      print('start fringe removal...')
      def roundstr(x,n):
          if not n:
              return str(int(round(x,0)))
          else:
              return str(round(x,n))
            
      pic_offset = 512 #0.1#Need this to avoid division-by-zero or similar wacky issues
      # Trying this without and only add at the last moment.
      # Choice of 64 is due to blackfly pixels ranging 0 -> 2^16 -1 (65535), but only having a bit depth of 2^10 (64)
      
      #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= 
      # Cutout stores the cropped region of each photo
      cutout=np.zeros([nshots,self.dims[0]-2*self.lowpassflag,self.dims[1]-2*self.lowpassflag])
      
      pic_nocrop = [[] for shot in range(nshots)]
      
      if not self.usefits:
          print("Not Usefits")
          for i in range(nshots):#i, pic in enumerate([pAtom,pRef,BG]):
              pic = self.readfile(fs[i-nshots]) # patom = fs[-3]; pRef=fs[-2]; no-light background BG = fs[-1]
              pic_crop = pic[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
              pic_nocrop[i] = pic
              self.data[i,:,:] = pic_crop
              # we don't want to lowpass before we fit!
              #if self.lowpassflag:
              #    cutout[i,:,:]=klib.filter_mask2(pic_crop)
      else:
          print("Yes Usefits")
          data = self.readfits(fs[0])
          #if self.lowpassflag:
          #    cutout=np.zeros([nshots,data.shape[1]-2*self.lowpassflag,data.shape[2]-2*self.lowpassflag])
          #    for i in range(nshots):
          #        cutout[i,:,:] = klib.filter_mask2(data[i,:,:])
          #else:
          cutout = data
          self.data = data
          
      pic0=np.zeros(self.dims)
      pic0 = cutout[2,:,:]
      tempBG=np.zeros(self.dims) # initialising as default floats
      #print(BGimages)
      #print(cutout[0,:,:]-pic0)
      #print(cutout[1,:,:]-pic0)
      tempBG = cutout[1,:,:]-pic0+pic_offset
      print("tempBG is ",type(tempBG))
      #tempBG[cutout[1,:,:] < pic0] = 0 # Running into issues where we get 'wraparound' of data due to noise
                                       # Wraparound in this case means that, since data is uint8, all numbers are modulus 256 (so something like 0 - 1 = 255)  
      #should now be floats
      BG_resetflag = False
      if (BGimages.shape[0] != tempBG.shape[0]) or (BGimages.shape[1] != tempBG.shape[1]):
          maxshots = BGimages.shape[2]
          BGimages = np.zeros((tempBG.shape[0],tempBG.shape[1], maxshots))
          BG_resetflag = True
          nBG = 0
      BGimages[:,:,nBG%BGimages.shape[2]] = tempBG#cutout[1,:,:]-pic0
      # Both of these assume mydiff = optical density = -ln(atom_pic / reference_pic)
      # 3-pic case just takes an extra 'no-light' image and subtracts that from both atom and ref pics.
      tempFG = np.zeros(self.dims)
      tempFG = cutout[0,:,:]-pic0+pic_offset
      #tempFG[cutout[0,:,:] < pic0] = 0 # Running into issues where we get 'wraparound' of data due to noise
                                       # Wraparound in this case means that, since data is uint8, all numbers are modulus 256 (so something like 0 - 1 = 255)  

      N_atoms = 0
      if (nBG>2) and self.fringeflag:
          BGshape = BGimages.shape
          finalindex=min(BGshape[2]-1,nBG)
          bgmask = klib.prepare_bgmask(dims=self.dims)#=[self.dims[0]-2*self.lowpassflag,self.dims[1]-2*self.lowpassflag])
          BGset = np.zeros([BGshape[0], BGshape[1], finalindex])
          for i in range(finalindex):
            BGset[:, :, i] = BGimages[:,:,i]
          
          mydiff,optrefimage,tel = klib.removefringe(tempFG,BGset,bgmask)
          #mydiff,optrefimage,tel = kl1.fringeremoval1(tempFG + pic_offset,BGset,bgmask)
      else:
        mydiff=-np.log(tempFG/tempBG)
        print('Not using BG subtraction', nBG)
      N_max=np.max(mydiff)  
      self.fitsuccess=False
      try:
          fitparams = self.gaussfit(mydiff, contourflag=self.contourflag)
          #height,wx,wy, contourdata=self.gaussfit(mydiff, contourflag=self.contourflag)
          self.ODpeak.append(fitparams[0])
          self.fitsuccess = True
      except:
          #height = 0; wx =0; wy=0
          #contourdata = 0
          fitparams = np.zeros([4,1])
          self.ODpeak.append(np.amax(mydiff))
          
      A_of_px=((1e-3)/131)**2
      Rb_crosssection = 1.3e-13 # See Ian Wenas' MSc thesis from 2007, pg65
      N_atoms = A_of_px * np.sum(mydiff) / Rb_crosssection
      if self.fitsuccess:
        N_atoms_corrected = A_of_px * np.sum(mydiff - fitparams[-1]*np.ones(mydiff.shape)) / Rb_crosssection # This sets the gauss-fit offset to be the 'zero' point. only works with a good fit
      
      if N_atoms > 0:
          power = np.floor(np.log10(N_atoms)/3)
          N_est = roundstr(N_atoms*10**(-3*power),1)
          try:
            print(f'Number of atoms = {N_est} x 10^{int(3*power)}')
          except:
            print('Trouble with atom number')
          #self.parent.CW.textout.append(QString(f'Number of atoms = {N_est} x 10^{int(3*power)}'))
      else:
          print(f'Number of atoms estimate failed - N_atoms = {N_atoms}')
          
      if self.fitsuccess and N_atoms_corrected > 0:
          power = np.floor(np.log10(N_atoms_corrected)/3)
          N_est = roundstr(N_atoms_corrected*10**(-3*power),1)
          try:
            print(f'Zeroed at gaussfit offset: Number of atoms = {N_est} x 10^{int(3*power)}')
          except:
            print('Trouble with atom number again')
      elif self.fitsuccess:
          print(f'Zeroed at gaussfit offset: Number of atoms estimate failed - N_atoms = {N_atoms_corrected}')    
      
      self.Natoms.append(N_atoms)
      
      self.OD_data = mydiff
      self.fitparams = fitparams
      print('Made it to blackfly pre-plot debug!')
      #self.main_plot(mydiff, fitparams)#height, wx, wy, contourdata)
      
      return BGimages, BG_resetflag, N_atoms, N_max
      
      #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
  
  def main_plot(self, mydiff, fitparams): #, height, wx, wy, contourdata):
    height, wx, wy, contourdata = fitparams
    plt.ion()
    N_atoms = self.Natoms[-1]
    
    plt.figure()
    plt.imshow(mydiff, cmap = cm.inferno)
    plt.colorbar()
    
    
    if self.fitsuccess:#self.fitflag and fitsuccess:
        try:
          prefix = ''
          #height,wx,wy, contourdata=self.gaussfit(mydiff, contourflag=True) # assuming already done to produce fitsuccess=True
          
          # For gaussian, assume particle number ~ int Gauss dx dy = w_x * w_y * height
          if N_atoms:
            if N_atoms < 0:
              print(f'N_atoms = {N_atoms} < 0; using Gaussian fit instead\n(N_atoms = h * w_x * w_y)')
              try:
                N_atoms = height*wx*wy
                widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
              except:
                N_atoms = 0
                widthtext = 'Fits failed: 0x, 0y;'
              
            if N_atoms > 0:
              power = np.floor(np.log10(N_atoms)/3)
              N_est = roundstr(N_atoms*10**(-3*power),1)
              try:
                widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
              except:
                widthtext = 'Fits failed: 0x, 0y;'
              print(f'N of Atoms: {N_est} x 10^{int(3*power)}')
            else:
              print('Gaussian fit also failed; setting N_atoms = 0')
              N_est = 0; power = 0
              widthtext = 'Fits failed: 0x, 0y;'
          else:
            try:
              power = 1
              N_est = roundstr(wx*wy*height/1000,0)
              widthtext = f'{roundstr(wx,0)}x, {roundstr(wy,0)}y;'
            except:
              N_est = 0; power = 0
              widthtext = 'Fits failed: 0x, 0y;'
          plt.title(f"{widthtext} N_est = {N_est}x10^{int(3*power)}")#,roundstr(wy*py[0]/1000,0)))
        except Exception as e:
            plt.title=(f"Fits failed; Exception: {e}")
    else:
        if N_atoms > 0:
            power = np.floor(np.log10(N_atoms)/3)
            N_est = roundstr(N_atoms*10**(-3*power),1)
            print(f'N of Atoms: {N_est} x 10^{int(3*power)}')
        print('Gaussian fits currently disabled - see \'self.fitflag\' in blackfly.py')
        
    if contourdata and self.contourflag:
      print('Plotting contours...')
      plt.contour(contourdata[0][0],contourdata[0][1], contourdata[1], 8)
      
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    self.OD_fig = plt.gcf()#fig
    
    #plt.draw() # Apparently this is preferred over show() for gui applications
    #plt.show()
    #plt.pause(0.001)
    

    # Make data.
    #X = np.arange(-5, 5, 0.25)
    #Y = np.arange(-5, 5, 0.25)
    #X, Y = np.meshgrid(X, Y)
    #R = np.sqrt(X**2 + Y**2)
    #Z = np.sin(R)

    # Plot the surface.
    if self.surf_flag:
        ax = plt.figure().add_subplot(projection='3d')
        surf = ax.plot_surface(contourdata[0][0],contourdata[0][1], mydiff, cmap=cm.coolwarm,
                              linewidth=0, antialiased=False)
        ax.contour(contourdata[0][0],contourdata[0][1], contourdata[1], 8)
        plt.colorbar(surf, shrink=0.5, aspect=5)
    
        #plt.draw() # Apparently this is preferred over show() for gui applications
        plt.show()

  
  def gaussfit(self,pic, fittype = '2d',contourflag=False):
    # initialising fitting results and initial estimates of fit parameters
    height=0; width=[0,0]
    width_est = 100
    try:
      height_est = np.max(pic)
    except:
      height_est = 3
    print("Trying Gaussfit")
    # Quick lambda function for <x> = int x * h(x) * dx / int h(x) dx
    #   with heights 'h' given by 'vec' 
    
    if fittype == '1d':
        com_calc = lambda vec: np.sum(vec[i]*i for i in range(len(vec))) / np.sum(vec) 
        
        for axis in range(2):
            # Just been rethinking this
            # Using np.sum is essentially integrating out y for axis=0, x for axis=1
            # which will give something proportional [since int exp(-(x^2+y^2)/(2sig^2)) dy = int exp(-y^2/2sig^2) dy * exp(-x^2/2sig^2) ]
            # But it might be more 'accurate' to use the max values at each y value/x value instead 
            #(using maxes would effectively fit to the 'silhouette' of the gaussian)
            #
            #In order to use maxes, we need:
            # Generally: maxvec = np.amax(pic,axis=axis)
            # for axis=0, this gives vec of max's of each column (so max y at each x);
            # for axis=1, this gives vec of max's of each row (so max x at each y)
            integral= np.mean(pic,axis)#This sums along columns
            if np.max(integral) > 0: height_est = np.max(integral)
            offset_est=np.amin([integral[0], integral[-1]]) # Only using [-1] rather than [0] because sometimes the cloud overlaps with top/left borders
            # Prepares initial estimates for gaussian fit
            com_pos = com_calc(integral)
            pguess = [height_est,width_est,com_pos,offset_est]
            print(f'Axis = {axis}; [h, w, mean, y0] guess = {pguess}')
            try:
                p,cv = curve_fit(gauss,np.arange(integral.shape[0]),integral,p0=pguess, bounds = [[0,0,0,-2000], [1000,1000,1000,2000]])
                print(f'Axis = {axis}; [h, w, mean, y0] optimal = {p}')
            except Exception as e:
                print(f'Axis = {axis}; Gaussfit failed, exception = {e}')
                p=[None]*4
            #p=pguess
            #plt.figure()
            #plt.plot(range(integral.shape[0]),integral,range(integral.shape[0]),gauss(range(integral.shape[0]),*p))
            # Inserts fitted widths/heights into relevant variables
            # Note: the max height should be the same along both axes, so we only take the x fit value.
            if p[1]==None:
              width[axis]=None
            else:
              width[axis]=np.abs(p[1])
              
            if not axis:
              height=p[0]
    
    elif fittype == '2d':
        #com_calc = lambda mat: np.sum([mat[i][j]*np.array([i,j]) for i in range(mat.shape[0]) for j in range(mat.shape[1])]) / np.sum(mat) 
        def com_calc(mat):
            vecs = [mat[i][j]*np.array([i,j]) for i in range(mat.shape[0]) for j in range(mat.shape[1])]
            com = [0,0]
            for vec in vecs: com += vec
            com *= 1/np.sum(mat)
            return com
            
        compic = copy.copy(pic)
        compic[np.isnan(compic)] = 0
        compic[compic<0] = 0
        #print(compic)
        try:
            com_pos = com_calc(compic)
        except:
            com_pos = [self.dims[0]/2, self.dims[1]/2]
        if (np.sum(np.isnan(com_pos))>0) or (com_pos[0] is None):
            com_pos = [self.dims[0]/2, self.dims[1]/2]
        print(com_pos)
        
        offset_est=np.amin(pic)
        
        if offset_est is None or np.isnan(offset_est):
          offset_est = 0
        
        pguess = [height_est, width_est, width_est, com_pos[0], com_pos[1], offset_est]
        
        print(f'2D fit; [h, wx, wy, x0, y0, o] guess = {pguess}')
        try:
            xy = np.meshgrid(np.arange(pic.shape[0]), np.arange(pic.shape[1]))
            p,cv = curve_fit(gauss_2d, xy, pic.ravel(), p0=pguess, bounds = [[0,0,0,0,0,-10], [1000,1000,1000,1000,1000,10]])
            print(f'2D fit; [h, wx, wy, x0, y0, o] optimal = {p}')
        except Exception as e:
            print(f'2D fit;  Gaussfit failed, exception = {e}')
            p=[None]*6
        
        height = p[0]; width = [p[1], p[2]]
        
        if self.contourflag:
          contourdata = [xy,\
            gauss_2d(xy, p[0], p[1], p[2], p[3], p[4], p[5]).reshape(xy[0].shape)]
    #com_calc = lambda vec: np.sum(vec[i]*i for i in range(len(vec))) / np.sum(vec) 
    #widthest = 100
    #offsetest=0
    #heightest=10
    
    #xcom = com_calc(xdir)#np.sum(xdir[i]*i for i in range(len(xdir)))/np.sum(xdir)      
    #pguessx=[heightest,widthest,xcom,offsetest] # order is height, width, mean, z-offset
    #px,cvx=curve_fit(gauss,np.arange(xdir.shape[0]),xdir,p0=pguessx)
    #wx=np.abs(px[1])
    
    #ycom = com_calc(ydir)#np.sum(ydir[i]*i for i in range(len(ydir)))/np.sum(ydir)
    #pguessy=[heightest,widthest,ycom,offsetest]
    #py,cvy=curve_fit(gauss,np.arange(ydir.shape[0]),ydir,p0=pguessy)      
    #wy=np.abs(py[1])
    if self.contourflag:
        results = [height,width[0],width[1], contourdata]
    else:
        results = [height,width[0],width[1], 0]
    return results#px[0],wx,wy #height, gaussian width in x,y directions
    
#==============================================================================================================
  
   
  
if __name__=='__main__':
  bcam=blackfly()
  files=bcam.findfiles()
  pic2=bcam.readfile(files[-1])
  pic1=bcam.readfile(files[-2])
  cutout=pic1[bcam.roi[0]:bcam.roi[1],bcam.roi[2]:bcam.roi[3]]
  cutout2=pic2[bcam.roi[0]:bcam.roi[1],bcam.roi[2]:bcam.roi[3]]
  mydiff=cutout.astype(int)-cutout2.astype(int)
  #plt.ion()
  plt.imshow(mydiff)
  #plt.draw() # Apparently this is preferred over show() for gui applications
  plt.show()
    
