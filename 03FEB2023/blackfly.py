import matplotlib.pyplot as plt
import glob
import os
import time
import numpy as np
from scipy.optimize import curve_fit
import kicklib as klib
from threading import Thread

def gauss(x,h,w,x0,o):
    return o + np.abs(h)*np.exp(-(x-x0)**2/w**2)
  
#class roidialog(QDialog):
  #def __init__(self,dims,center):
    #self.dims=dims
    #self.center=center
    


class blackfly():
  def __init__(self):
    self.thepath='/home/lab/picshare/*.pgm'
    self.fitflag=True#False #True#
    self.lowpassflag=True#False#True#
    print(f'Note: blackfly.py\'s low-pass filter is currently set to {self.lowpassflag}')
    #self.roi=[680,1080,850,1450]
    #self.dims=[self.roi[1]-self.roi[0], self.roi[3]-self.roi[2]]
    self.dims = [500, 500]#[400,600] # y/rows, x/cols
    self.center= [800,1050]#[880,1150] # y/rows, x/cols
    self.roi=[int(self.center[i]+a*self.dims[i]) for i in range(2) for a in [-0.5, 0.5]]
    self.data=np.zeros((3,self.dims[0],self.dims[1]))
    
    self.ODpeak = []
    self.Natoms = []
    
    
  #==============================================================================================================
  
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
    print(a)
    return a
    
  #==============================================================================================================
  
  def shoot(self,nshots):
    fs=self.findfiles()
    for f in fs:
      os.remove(f)
    
  #==============================================================================================================
  def show2(self,nshots,BGimages,nBG):
    t1=Thread(target=self.show2,args=[nshots,BGimages,nBG])
    t1.start()
    t1.join()
    return BGimages
  
  
  def show(self,nshots,BGimages,nBG):  
    def roundstr(x,n):
        if not n:
            return str(int(round(x,0)))
        else:
            return str(round(x,n))
    fs=[]
    i=0
    while (len(fs)<nshots) and (i<10):
      fs=self.findfiles()
      i=i+1
      time.sleep(0.5)
    if i>9:
      return None
    
    if nshots==3:
      BGimages=self.plot_fringeremoval(fs,nshots,BGimages,nBG)
    elif nshots==2:
    
      pic2=self.readfile(fs[-1])
      pic=self.readfile(fs[-2])
      
      self.data[0,:,:]=pic[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
      self.data[1,:,:]=pic2[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
      
      
      
      if self.lowpassflag:
        cutout=klib.filter_mask2(self.data[0,:,:])
      else:
        cutout=self.data[0,:,:]
      
      if self.lowpassflag:
        cutout212=klib.filter_mask2(self.data[1,:,:])
      else:
        cutout212=self.data[1,:,:]
      
      
      BGimages[:,:,nBG%BGimages.shape[2]] = cutout212
      
      #mydiff=klib.removefringe(cutout,cutout212,klib.prepare_BGmask())
      mydiff=cutout.astype(int)-cutout212.astype(int)
      #mydiff=-np.log(cutout.astype(int)/cutout212.astype(int))
      #plt.ion()
      print('Made it to blackfly pre-plot debug!')
      plt.imshow(mydiff)
      if self.fitflag:
          height,wx,wy=self.gaussfit(mydiff)
          if sum([x is None for x in [height,wx,wy]])>0:
              plt.title("Fits failed")
          else:
              plt.title("Width = {}x, {}y; N_est = {}".format(roundstr(wx,0),roundstr(wy,0),roundstr(wx*wy*height/1000,0)))#,roundstr(wy*py[0]/1000,0)))
      else:
          print('Gaussian fits currently disabled - see \'self.fitflag\' in blackfly.py')
      
      plt.xlabel('X (pixels)')
      plt.ylabel('Y (pixels)')
      plt.show()
      
    #if nshots==3:
      #cutout=[]
      #for i in range(nshots)#i, pic in enumerate([pAtom,pRef,BG]):
      #  pic=self.readfile(fs[i-nshots]) # patom = fs[-3]; pRef=fs[-2]; no-light background BG = fs[-1]
      #  cutout.append(pic[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]])
      #  self.data[i,:,:]=cutout[i,:,:]
        
      #mydiff=-np.log((cutout[0,:,:] - cutout[2,:,:])/(cutout[1,:,:] - cutout[2,:,:]))
      
      #print('Made it to blackfly pre-plot debug!')
      #plt.imshow(mydiff)
      #try:
      #    height,wx,wy=self.gaussfit(mydiff)
      #    plt.title("Width = {}x, {}y; N_est = {}".format(roundstr(wx,0),roundstr(wy,0),roundstr(wx*wy*height/1000,0)))#,roundstr(wy*py[0]/1000,0)))
      #except:
      #    plt.title=("Fits failed")
      #plt.xlabel('X (pixels)')
      #plt.ylabel('Y (pixels)')
      #plt.show()
    return BGimages
  
  def plot_fringeremoval(self,fs,nshots,BGimages,nBG):
      print('start fringe removal...')
      def roundstr(x,n):
          if not n:
              return str(int(round(x,0)))
          else:
              return str(round(x,n))
      #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= 
      # Cutout stores the cropped region of each photo
      cutout=np.zeros([nshots,self.dims[0]-2*self.lowpassflag,self.dims[1]-2*self.lowpassflag])
      for i in range(nshots):#i, pic in enumerate([pAtom,pRef,BG]):
          pic = self.readfile(fs[i-nshots]) # patom = fs[-3]; pRef=fs[-2]; no-light background BG = fs[-1]
          pic_crop = pic[self.roi[0]:self.roi[1],self.roi[2]:self.roi[3]]
          self.data[i,:,:] = pic_crop
          
          if self.lowpassflag:
              cutout[i,:,:]=klib.filter_mask2(pic_crop)
          
      pic0=np.zeros(self.dims)
      if nshots==3:
          pic0 = cutout[2,:,:]
      #print(BGimages)
      #print(cutout[0,:,:]-pic0)
      #print(cutout[1,:,:]-pic0)
      BGimages[:,:,nBG%BGimages.shape[2]]=cutout[1,:,:]-pic0
      # Both of these assume mydiff = optical density = -ln(atom_pic / reference_pic)
      # 3-pic case just takes an extra 'no-light' image and subtracts that from both atom and ref pics.
      N_atoms = 0
      if nBG>10 and nshots==3:
          finalindex=min(BGimages.shape[2]-1,nBG)
          bgmask = klib.prepare_bgmask(dims=[self.dims[0]-2*self.lowpassflag,self.dims[1]-2*self.lowpassflag])
          
          BGset = np.zeros([self.dims[0]-2*self.lowpassflag, self.dims[1]-2*self.lowpassflag, finalindex])
          for i in range(finalindex):
            BGset[:, :, i] = BGimages[:,:,i] + .1
          
          mydiff,optrefimage,tel = klib.removefringe(cutout[0,:,:]-pic0+.1,BGset,bgmask)
      
      elif nshots>1:
          top = np.abs(cutout[0,:,:] - pic0)
          bottom = np.abs(cutout[1,:,:] - pic0)
          norm_ratio = np.mean(bottom[:10,:10])/np.mean(top[:10,:10])
          #norm_ratio = np.mean(np.amin(bottom,axis=0)) / np.mean(np.amin(top,axis=0))
          mydiff = -np.log(norm_ratio*(top + .1)/(bottom + .1))
          
      A_of_px=((1e-3)/131)**2
      Rb_crosssection = 1.3e-13 # See Ian Wenas' MSc thesis from 2007, pg65
      N_atoms = A_of_px * np.sum(mydiff) / Rb_crosssection
          #I don't think the following stuff is necessary if we just do this pic0 thing
          #if nshots==2:
          #    mydiff=-np.log(cutout[0,:,:].astype(int)/cutout[1,:,:].astype(int))
          #elif nshots==3:  
          #    mydiff=-np.log((cutout[0,:,:] - pic0)/(cutout[1,:,:] - pic0))
          
      #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=    
      self.ODpeak.append(np.amax(mydiff))
      self.Natoms.append(N_atoms)
      
      print('Made it to blackfly pre-plot debug!')
      plt.imshow(mydiff)
      plt.colorbar()
      
      if self.fitflag:
          #try:
          prefix = ''
          height,wx,wy=self.gaussfit(mydiff)
          
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
          #except:
          #    plt.title=("Fits failed")
      else:
          print('Gaussian fits currently disabled - see \'self.fitflag\' in blackfly.py')
      plt.xlabel('X (pixels)')
      plt.ylabel('Y (pixels)')
      plt.show()
      
      return BGimages
      
      #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
      
  def gaussfit(self,pic):
    # initialising fitting results and initial estimates of fit parameters
    height=0; width=[0,0]
    width_est = 100
    height_est = 100
    print("Trying Gaussfit")
    # Quick lambda function for <x> = int x * h(x) * dx / int h(x) dx
    #   with heights 'h' given by 'vec' 
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
        integral= np.sum(pic,axis)#This sums along columns
        height_est=np.max(integral)
        offset_est=integral[-1] # Only using [-1] rather than [0] because sometimes the cloud overlaps with top/left borders
        # Prepares initial estimates for gaussian fit
        com_pos = com_calc(integral)
        pguess = [height_est,width_est,com_pos,offset_est]
        print(f'Axis = {axis}; [h, w, mean, y0] guess = {pguess}')
        try:
            p,cv = curve_fit(gauss,np.arange(integral.shape[0]),integral,p0=pguess)
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
    
    return height,width[0],width[1]#px[0],wx,wy #height, gaussian width in x,y directions
    
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
  plt.show()
    
