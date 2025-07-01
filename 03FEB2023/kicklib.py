# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 11:39:20 2014
piclib.py
@author: maarten
"""
import numpy as np

def addpics(filenames):
    #[y s]=addpics(filenames) 
    # Adds the pictures in filenames, and returns a 2D array y and a scalefactor
    # s, which is the velocity of one pixel
    y=None#np.zeros([512,512]); # We want to avoid committing to [512,512], so set y's size later.
    #n=0
    for filename in filenames:
        t1,t2=getpic(filename,0);
        if y:
          y+=t1
        else:
          y=np.array(t1)# This lets us assume the dimensions of the first image, 
                        # rather than committing to a certain number of pixels
    y=y/len(filenames)# This is the *average* of all pictures in file set 'filenames'
    s=t2
    return y,s

def typeofrun(folder, mat_only = False):
    from glob import glob
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits
    
    if (mat_only):
         npics = np.size(glob(folder+'/*.mat'));
         return "number", np.linspace(0, npics, npics), npics
    else:
        file1 = folder+ '/Data_0.fit'
        file2 = folder+ '/Data_1.fit'
        try:
            t1 = pyfits.open(file1)
            npics = np.size(glob(folder+'/*.fit'));
        except:
            file1=file1[0:4]+'/'+file1
            file2=file2[0:4]+'/'+file2
            #print(file1)
            t1 = pyfits.open(file1)
            folder=folder[0:4]+'/'+folder
            npics = np.size(glob(folder+'/*.fit'));
        k1 = t1[0].header
        t2 = pyfits.open(file2);
        k2 = t2[0].header;
        
        npts = np.size(k1);
        ultJJ = []
        #outStr = '';
        #otherStuff = 0;
        vals = np.zeros(npics);
        changeCount = 1;
        
        changeStr = '';
        for jj in range(13,(npts-1)):
            val1 = k1[jj];
            val2 = k2[jj];
            
            if(val1 != val2):
                ultJJ.append(jj);
                t3=list(k1.keys())
                #print(t3)
                changeStr = changeStr+t3[jj];
                changeCount = changeCount+1;
        
        if(changeCount > 2):
            print('Something else changed')
            print(changeStr)
        
        #print len(ultJJ)
        if (len(ultJJ) != 1):
            print('Something weird here, assuming dummy')
            outStr='dummy'
            vals=range(npics)
            #return
        else:
            outStr = changeStr
            t1.close()
            t2.close()
            vals=np.zeros(npics)
            for kk in range(npics):
                myFile = folder+'/Data_'+str(kk)+'.fit'
                tt = pyfits.open(myFile)
                key = tt[0].header
                vals[kk]=key[ultJJ[0]]
                tt.close()

        return outStr,vals,npics



def getpic(filename,dopic, mat_only = False):
    import matplotlib.pyplot as plt
    from scipy.io import loadmat
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits
      
    # Here follows a big muckaround to check/load the appropriate files.
    # May only be historically relevant; might want to check whether this continues to be necessary.
    try:
        matname=filename[0:-3]+'mat';
        tmp=loadmat(matname);
        out=tmp['a1'];
        if (mat_only):
            return out, 1
        hdulist=pyfits.open(filename);
        if (dopic):
            print('Found matfile')
    except:
        try:
            matname=matname[0:4]+'/'+matname;
            tmp=loadmat(matname);
            out=tmp['a1']
            fn2=filename[0:4]+'/'+filename;
            hdulist=pyfits.open(fn2);
            if (dopic):
                print('Found matfile')
        except:
            try:
                hdulist=pyfits.open(filename)
                print("Trying impo", filename)
                a=hdulist[0].data
                if (dopic):
                   print("found fits file",filename)
            except FileNotFoundError:
                print("Why are we here")+l
                try:
                    fn2=filename[0:4]+'/'+filename;
                    hdulist=pyfits.open(fn2);
                    a=hdulist[0].data
                    if (dopic):
                        print("found fits file here",fn2)
                except:
                    print('I really cannot find this file')
                    return -1,-1  
            t1=(a[0,:,:]-a[2,:,:])/(a[1,:,:]-a[2,:,:]);
            out=-np.log(t1)
    if (filename.find('/20')>=0): 
        ts=filename[5:17]
    elif (filename.find('Dylan/') >= 0):
        ts=filename[6:18]
    else:
        ts=filename[0:12];
    # Here ends the muckaround.    
        
    prihdr=hdulist[0].header
    # Expansion time: (in seconds)
    exptime=prihdr[13];
    exptime=exptime/1e6;
    ts2=int(ts);
    if (ts2<200809010000):
        exptime=exptime+2.85e-3
    #onepixel=1.85e-6; %This was the calibration using the mask
    #onepixel=5.44e-6; % This is the calibration using how big is two photon recoils in the QKR
    onepixel=2.129e-6;
#    onepixel=1.93e-6;
    #exptime
    scale=onepixel/exptime;
    hdulist.close()
    if (dopic):
        plt.figure();
        if (dopic==1):
            """imshow was previously colormesh"""
            plt.imshow(out);
        if (dopic==2):
            out=filter_mask(out)
            plt.imshow(out)
        plt.show()
    return out,scale
        
def removefringe(foregrounds,backgrounds,bgmask):#fringeremoval1(foregrounds,backgrounds,bgmask):
    # Previously named 'fringeremoval1' - This is 'the good one'.
    
    # NOTE: foregrounds and backgrounds are expected to come in the shape [npix_rows, npix_cols, nimages]
    #           THIS MAY REQUIRE SOME REARRANGEMENT
    
    # I've removed the alternatives that were included in the original file located on data2
    # This is honestly looking pretty lean already, so I haven't fiddled or tried to optimise. - Alex S
    #
    #   Ah, so I think I've figured out where the basic approach comes from.
    # Source: 'Detection of small atom numbers through image processing'
    #           C. F. Ockeloen, A. F. Tauschinsky, R. J. C. Spreeuw, and S. Whitlock
    #           Phys. Rev. A (2010)
    #           https://journals.aps.org/pra/pdf/10.1103/PhysRevA.82.061606
    # Code also included in C Ockeloen's MSc
    #   'Probing fluctuations in a lattice of mesoscopic atomic ensembles'
    #   https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.465.9350&rep=rep1&type=pdf
    #
    # NOTE: This is all from 2010; more recent possibilities might be worth investigating.
    # Relevant review: https://iopscience.iop.org/article/10.1088/1674-1056/ac3758/pdf
    # Also see: https://aip.scitation.org/doi/full/10.1063/1.5040669?journalCode=apl
    #           https://journals.aps.org/prapplied/pdf/10.1103/PhysRevApplied.14.034006
    #           https://journals.aps.org/prapplied/pdf/10.1103/PhysRevApplied.14.014011
    import time
    t=time.time()
    k=np.nonzero(bgmask.flatten()) # finds indices of non-zero bgmask elements
    nk=np.size(k) # number of non-zero elements in bgmask
    #
    sx,sy=foregrounds.shape # x,y in pixels + number of pics saved
    nimgs=1 # PREVIOUSLY: sx,sy,nimgs = foregrounds.shape#<- necessary if handing a stack of foregrounds
    # Below, we flatten each image in foreground, background; each column corresponds to single image;
    # Note that we then only end up working on pixels indicated by the bg mask vector 'k'.
    R=backgrounds.reshape([sx*sy,backgrounds.shape[2]])#nimgs]) 
    A=foregrounds.reshape([sx*sy,nimgs])
    #
    # This pulls out only the pixels from each image that correspond to the applied mask. 
    # I'm honestly not sure if the reshape is necessary here.
    indices=np.isin(list(range(sx*sy)), k, assume_unique=True)
    #indices = [i in list(k) for i in range(sx*sy)]
    Rk=R[indices,:]#.reshape([nk,nimgs])
    b=np.dot(np.transpose(Rk),Rk)
    # Initialise optimal reference images, each pixel set to 0.
    O1=np.zeros([sx*sy,nimgs])
    
    for j in range(nimgs):
        Akj=A[indices,j].reshape(nk) #extract background-mask pixels from foreground shots, shape into column vec for upcoming dot product
        c=np.dot(np.transpose(Rk),Akj) # image j corresponds to c_j = dot(Rkj, Akj)
        # sol contains the weights for which each reference image in background basis R 
        #       contributes to each pixel
        sol=np.linalg.solve(b,c) #basically finding sol that satisfies sol_k b_jk = c_j
        O1[:,j]=np.dot(R,sol) # This returns the 'optimal' reference image O1 for each foreground image
    #    
    if nimgs>1:
      odimages=np.reshape(-np.log(A/O1),[sx,sy,nimgs]) # D = -ln(A/R_optimal) gives the optical density D
    else:
      odimages=np.reshape(-np.log(A/O1),[sx,sy])
    oprefs=np.reshape(O1,[sx,sy,nimgs]) 
    elapsed=time.time()-t
    
    # Finally we return the optical density for each image (odimages), the 'optimal' reference image (oprefs) and the time taken
    return odimages,oprefs,elapsed
      
def saveimages(ids,pics):
    from scipy.io import savemat
    for i,fn in enumerate(ids):
        matname=fn[0:-3]+'mat';
        print(matname)
        a={}
        a['a1']=pics[:,:,i]
        savemat(matname,a);

def filter_mask(z):
    f=0.1*np.ones([3,3]); f[1,1]*=2 # f is the mask for 'averaging' the pixels around pixel i,j (extra weighting for central pixel) 
    # Everything from here should handle any form of f you like; go wild with masking!
    out=np.zeros([z.shape[0]-f.shape[0]+1,z.shape[1]-f.shape[1]+1])
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
                    # I've rewritten this to be agnostic re: the size of f in x or y
                    out[i,j]+=np.size(f)*np.mean(np.multiply(f,z[i:i+f.shape[0],j:j+f.shape[1]])) # np.size(f)*mean(matrix) is just a quick way of writing sum(sum(...))
    return out
  
def filter_mask2(z):
    # This is muuuuuch faster than filter_mask in the specific case of the 1-pixel pyramid averaging we're doing.
    
    #f=0.1*np.ones([3,3]); f[1,1]*=2 # f is the mask for 'averaging' the pixels around pixel i,j (extra weighting for central pixel) 
    na=z.shape[0];nb=z.shape[1]
    out=np.zeros([na-2,nb-2])
    for i in [-1,0,1]:
        for j in [-1,0,1]:
                    out+=0.1*(1+(i==j and not i))*z[1+i:na-1+i,1+j:nb-1+j]
    return out 

def prepare_bgmask(dims=[512,512],bgcor=50):
    bgmask=np.zeros(dims)
    bgmask[0:(bgcor),0:(bgcor)]=1
    bgmask[0:(bgcor),-bgcor:]=1
    bgmask[-bgcor:,0:(bgcor)]=1
    bgmask[-bgcor:,-bgcor:]=1
    return bgmask

def perform_FR(atomfiles,reffiles=[],maxrefs=50,bunchsize=-1):
  # This is the updating version, to handle different amounts of atom pictures and reference pictures.
  # Probably a good idea to use this in place of getallpics(), even when using same files for both.
  # If you give this only atomfiles, it will gather reference images from the same files.
    import numpy as np
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits
    if bunchsize<1:
      bunchsize=len(atomfiles)
    if len(reffiles)>maxrefs:
      print(f'Too many reference files provided! Truncating to first {maxrefs} files.')
      reffiles=reffiles[:maxrefs]
    
    idatom=[]
    idBG=[]
    foregrounds = None#np.zeros([512,512,bunchsize])
    backgrounds = None#np.zeros([512,512,bunchsize])
    origpics = None#np.zeros([512,512,bunchsize])
    bgmask = None#prepare_bgmask()
    pics = None
    
    for i,f in enumerate(reffiles):
      with pyfits.open(f) as hdl:
        a=hdl[0].data
        if not backgrounds:
          dims=[a.shape[1],a.shape[2]]
          foregrounds = np.zeros([dims[0],dims[1],len(atomsfiles)])
          backgrounds=np.zeros([dims[0],dims[1],len(reffiles)])
          origpics = np.zeros([dims[0],dims[1],len(atomsfiles)])
          bgmask = prepare_bgmask(dims=dims)
        backgrounds[:,:,i]=a[1,:,:]-a[2,:,:]
        idBG = f
      
    #npics=0
    j=-1 # initialising so that if no atom files are provided, nothing happens.
    jpic=-1 # initialising so that if no atom files are provided, nothing happens.
    for j,fa in enumerate(atomfiles):
      jpic=j%bunchsize
      with pyfits.open(fa) as hdl:
        a=hdl[0].data
      if not backgrounds:
        dims=[a.shape[1],a.shape[2]]
        foregrounds = np.zeros([dims[0],dims[1],len(atomsfiles)])
        backgrounds=np.zeros([dims[0],dims[1],len(atomsfiles)])
        origpics = np.zeros([dims[0],dims[1],len(atomsfiles)])
        bgmask = prepare_bgmask(dims=dims)
      
      # If its a 3-image file, we want to remove the data from the 'no light' image
      # The 'no light' image is labelled pic0
      # If it doesn't exist, we effectively skip the step by subtracting 0s instead.
      if a.shape[0]==2:    
        pic0 = a[2,:,:]
      else:
        pic0=np.zeros(dims)
        
      foregrounds[:,:,jpic]=a[0,:,:]-pic0
      if not reffiles:
        backgrounds[:,:,jpic]=origBG=a[1,:,:]-pic0
      else:
        origBG=a[1,:,:]-pic0
          
      origpics[:,:,jpic]=-np.log(foregrounds[:,:,jpic]/origBG)
      idatom.append(fa)
            
      if not (j+1)%bunchsize:
        print('Converting')
        pics,optrefimages,tel = removefringe(foregrounds,backgrounds,bgmask)
        print('Saving, elapsed time',tel)
        saveimages(idatom,pics)
        idatom=[]
    if jpic > -1:
      print('Converting last', jpic+1)
      fg2=foregrounds[:,:,:jpic+1]
      pics,optrefimages,tel = removefringe(fg2,backgrounds,bgmask) 
      print('Saving, elapsed time',tel)
      saveimages(idatom,pics)
    print('Total pics adjusted: ',j+1)
    return pics,origpics,jpic+1

def getallpics(basename,bunchsize):
    import numpy as np
    from glob import glob
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits  
      
    listofdirs=glob(basename+'*');
    
    npics=0;
    id1=[]
    foregrounds=None#np.zeros([512,512,bunchsize])
    backgrounds=None#np.zeros([512,512,bunchsize])
    origpics=None#np.zeros([512,512,bunchsize])
    bgmask = None#prepare_bgmask()
    
    for currentdir in listofdirs:
      
        print(currentdir)
        listofiles=glob(currentdir+'/*.fit');
        
        for fn in listofiles:
            filename=fn
            print(npics, filename)
            hdl=pyfits.open(filename);
            a=hdl[0].data
            
            if not foregrounds:
                dims = [a.shape[1],a.shape[2]]
                foregrounds = np.zeros([dims[0],dims[1],bunchsize])
                backgrounds = np.zeros([dims[0],dims[1],bunchsize])
                origpics = np.zeros([dims[0],dims[1],bunchsize])
                bgmask = prepare_bgmask(dims=dims)
                
            foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:];
            backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:];
            origpics[:,:,npics]=-np.log(foregrounds[:,:,npics]/backgrounds[:,:,npics])
            id1.append(filename)
            npics=npics+1
            
            if (npics==(bunchsize)):
                print('Converting')
                pics,optrefimages,tel = removefringe( foregrounds,backgrounds,bgmask);
                print('Saving, elapsed time',tel)
                saveimages(id1,pics)
                npics=0
                id1=[]
                
    print('Converting last', npics)
    fg2=foregrounds[:,:,:npics]
    bg2=backgrounds[:,:,:npics]
    pics,optrefimages,tel = removefringe(fg2,bg2,bgmask) 
    print('Saving, elapsed time',tel)
    saveimages(id1,pics)
    return pics,origpics,npics

# - - - - - - - - - - - - - - - - - - - - - - - - \
# =|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
# =|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
# - - - - - - - - - - - - - - - - - - - - - - - - /

def filtertest(runs,n):
  from time import perf_counter
  
  tic = perf_counter()
  for i in range(runs):
      a = np.random.rand(n,n)
      filter_mask(a)
  toc = perf_counter()
  print(f'Filter_mask completed 100 runs in {toc-tic} seconds')
  
  tic = perf_counter()
  for i in range(runs):
      a = np.random.rand(n,n)
      filter_mask2(a)
  toc = perf_counter()
  print(f'Filter_mask2 completed 100 runs in {toc-tic} seconds')
  
def filtertest2(runs,n):
  from time import perf_counter
  
  tic = perf_counter()
  diff=0
  for i in range(runs):
      a = np.random.rand(n,n)
      b=filter_mask(a)
      c=filter_mask2(a)
      diff+=np.array_equal(b,c)
  toc = perf_counter()
  print(f'Filter_mask completed {runs} runs in {toc-tic} seconds; difference = {diff}')