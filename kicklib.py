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
            plt.imshow(out,cmap="inferno");
        if (dopic==2):
            out=filter_mask(out)
            plt.imshow(out)
        plt.show()
    return out,scale

def fringeremoval1(foregrounds,backgrounds,bgmask):
    import time
    #import numpy as np
    #from scipy.linalg import lu
    t=time.time()
    k=np.nonzero(bgmask.flatten())
    nk=np.size(k)
    sx,sy,nimgs=foregrounds.shape
    R=backgrounds.reshape([sx*sy,nimgs]).astype(float)
    A=foregrounds.reshape([sx*sy,nimgs]).astype(float)
    O1=np.zeros([sx*sy,nimgs])
    Rk=R[k,:].reshape([nk,nimgs])

    #p,l,u=lu(np.dot(np.transpose(Rk),Rk))
    #pp=np.nonzero(p)[1]
    b=np.dot(np.transpose(Rk),Rk)

    for j in range(nimgs):
        Akj=A[k,j].reshape(nk)
        c=np.dot(np.transpose(Rk),Akj)
        sol=np.linalg.solve(b,c)
        O1[:,j]=np.dot(R,sol)
        print(np.sum(sol))

    odimages=np.reshape(-np.log(A/O1),[sx,sy,nimgs])
    oprefs=np.reshape(O1,[sx,sy,nimgs])
    elapsed=time.time()-t
    return odimages,oprefs,elapsed

def PCAremove_otf(FG, backgrounds,bgmask, n_components=None, variance_threshold=0.95):
    """
    PCA removal function "On the Fly" - processes one foreground against multiple backgrounds
    Similar to fringeremoval_otf but using PCA instead of linear least squares
    
    Parameters:
    -----------
    FG : np.array, shape [npix_rows, npix_cols]
        Single foreground image (with atoms)
    backgrounds : np.array, shape [npix_rows, npix_cols, nimages] 
        Stack of background/reference images (without atoms)
    bgmask : np.array, shape [npix_rows, npix_cols]
        Boolean mask indicating background regions for PCA analysis
    n_components : int, optional
        Number of principal components to remove. If None, uses variance_threshold
    variance_threshold : float, default=0.95
        Remove components that explain this fraction of variance
        
    Returns:
    --------
    odimage : np.array, shape [npix_rows, npix_cols]
        Optical density image after PCA noise removal
    opref : np.array, shape [npix_rows, npix_cols]
        Estimated noise/reference image that was removed
    """
    from sklearn.decomposition import PCA
    
    # Get dimensions
    k = np.nonzero(bgmask.flatten())
    nk = np.size(k)
    sx, sy, nimgs = backgrounds.shape
    
    print(f'PCA OTF: Processing 1 foreground against {nimgs} backgrounds')
    print(f'Using {nk} background pixels for PCA analysis')
    
    # Reshape images - each row is an image, each column is a pixel
    bg_flat = backgrounds.reshape([nimgs, sx*sy]).astype(float)  # Shape: [nimgs, npixels]
    bg_mean_flat = np.mean(bg_flat, axis=0)  # Mean background pixel values
    fg_flat = FG.reshape([sx*sy]).astype(float)  # Shape: [npixels]
    bg_flat -= bg_mean_flat  # Center background data
    fg_flat -= bg_mean_flat  # Center foreground data
    
    # Extract background mask pixels for PCA training
    #bg_masked = bg_flat[:, k]  # Shape: [nimgs, nk]
    #fg_masked = fg[k]     # Shape: [nk]
    
    # Combine foreground and background for comprehensive PCA
    # Add foreground as additional "training" sample
    #combined_flat = np.vstack([bg_flat, fg_flat.reshape(1, -1)])  # Shape: [nimgs+1, nk]
    
    # Determine number of components
    if n_components is None:
        pca_temp = PCA()
        pca_temp.fit(bg_flat)
        cumvar = np.cumsum(pca_temp.explained_variance_ratio_)
        n_components = np.where(cumvar >= variance_threshold)[0][0] + 1
        print(f"Auto-selected {n_components} components (explains {cumvar[n_components-1]:.3f} of variance)")
    
    # Fit PCA with determined number of components
    pca = PCA(n_components=n_components, svd_solver='randomized')
    pca.fit(bg_flat)
    
    print(f"PCA variance explained by {n_components} components: {np.sum(pca.explained_variance_ratio_):.3f}")
    
    fg_proj = pca.inverse_transform(pca.transform(fg_flat[None, :]))[0]  # Project foreground onto PCA space and back to pixel space
    opref = fg_proj.reshape([sx, sy]) + bg_mean_flat.reshape([sx, sy])  # Reshape back to image
    opref[opref <= 0] = np.min(bg_mean_flat[bg_mean_flat>0])  # Avoid log(0) or negative values

    odimage = -np.log(FG / opref)  # Calculate optical density image
    
    return odimage, opref
   

def fringeremoval_otf(FG,backgrounds,bgmask):
    import matplotlib.pyplot as plt
    # This version just does one fringeremove "On the fly"
    # It takes one foreground but any number of backgrounds and a background mask
    k=np.nonzero(bgmask.flatten())
    nk=np.size(k)
    sx,sy,nimgs=backgrounds.shape
    plt.figure()
    plt.subplot(3,3,1)
    plt.imshow(FG,cmap='inferno')
    plt.subplot(3,3,2)
    plt.imshow(backgrounds[:,:,0])
    R=backgrounds.reshape([sx*sy,nimgs]).astype(float)
    plt.subplot(3,3,3)
    plt.imshow(R[:,1].reshape([sx,sy]))
    A=FG.reshape([sx*sy]).astype(float)
    O1=np.zeros([sx*sy])
    Rk=R[k,:].reshape([nk,nimgs])
    b=np.dot(np.transpose(Rk),Rk)
    print(f'Rk = {np.shape(Rk)}')
    print(f'A = {np.size(A)}')
    print(f'b = {b}')
    # print(backgrounds)
    # for j in range(nimgs)
    # Discard the for loop as we only have one foreground
    Ak=A[k].reshape(nk)
    c=np.dot(np.transpose(Rk),Ak)
    print(c)
    print(f'nk = {nk}, sx = {sx}, sy = {sy}, nimgs = {nimgs}')
    print(f'b= {np.shape(b)}, c = {np.shape(c)}')
    try:
    #if True:
      sol=np.linalg.solve(b,c)
      O1=np.dot(R,sol)
      print(f'Ol = {np.size(O1)}')
      print('Sol is ', sol, np.sum(sol))
      odimage=np.reshape(-np.log(A/O1),[sx,sy])
      opref=np.reshape(O1,[sx,sy])
      print('Fringe reduction success!')
    #else:
    except:
      BG=backgrounds[:,:,-1]
      odimage=np.reshape(-np.log(A/R[:,-1]),[sx,sy])
      opref=BG
      print('Fringe reduction Failed!')
      pass
    #plt.subplot(3,3,4)
    #plt.imshow(opref,cmap='inferno')
    #plt.subplot(3,3,5)
    #plt.imshow(odimage,cmap='inferno')
    #plt.subplot(3,3,6)
    #plt.imshow(R[:,-1].reshape([sx,sy]))
    #plt.show()
    #elapsed=time.time()-t
    return odimage,opref

def removefringe(foregrounds,backgrounds,bgmask):#fringeremoval1(foregrounds,backgrounds,bgmask):
    # This one is at the moOlment disused in favour of fringeremoval1
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
    print(foregrounds.shape)
    sx,sy,nimgs=foregrounds.shape # x,y in pixels + number of pics saved
    # nimgs=1 # PREVIOUSLY: sx,sy,nimgs = foregrounds.shape#<- necessary if handing a stack of foregrounds
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
        try:
          sol=np.linalg.solve(b,c) #basically finding sol that satisfies sol_k b_jk = c_j
          O1[:,j]=np.dot(R,sol) # This returns the 'optimal' reference image O1 for each foreground image
        except:
          print('FRINGE SOLUTION FAILED - very likely singular. Unlucky.')
          break
    #should do DC update here

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
    for i,fn in enumerate(iOlds):
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

def prepare_bgmask(dims=[512,512],bgcor=100):
  # Comparing background images at the corners - each square uses (bgcor)x(bgcor) pixels
    bgmask = np.full(dims, 0.0)
    bgmask[0:(bgcor),0:(bgcor)] = 1.0
    bgmask[0:(bgcor),-bgcor:] = 1.0
    bgmask[-bgcor:,0:(bgcor)] = 1.0
    bgmask[-bgcor:,-bgcor:] = 1.0
    return bgmask

def perform_FR(atomfiles,reffiles=[],maxrefs=50,bunchsize=-1):
  for fn in listofiles:
    filename=fn
    print(npics, filename)
    try:
      hdl=pyfits.open(filename)
      a=hdl[0].data
      foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:]
      backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:]
      npics+=1
    except:
      print("Failed here")
      pass
    #npi
  # This is the updated version, to handle different amounts of atom pictures and reference pictures.
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
        pics,optrefimages,tel = fringeremoval1( foregrounds,backgrounds,bgmask);
        #pics,optrefimages,tel = removefringe(foregrounds,backgrounds,bgmask)
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

def getsomepics(basename):
    import numpy as np
    from glob import glob
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits

    listofdirs=glob(basename+'*');
    bunchsize=200
    npics=0;
    id1=[]
    foregrounds=np.zeros([512,512,bunchsize])
    backgrounds=np.zeros([512,512,bunchsize])
    #origpics=None#np.zeros([512,512,bunchsize])
    #bgmask = None#prepare_bgmask()    print(f'b = {b}')
    for currentdir in listofdirs:

        print(currentdir)
        listofiles=glob(currentdir+'/*.fit');

        for fn in listofiles:
            filename=fn
            print(npics, filename)
            try:
              hdl=pyfits.open(filename)
              a=hdl[0].data
              foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:]
              backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:]
              npics+=1
            except:
              print("Failed here")
              pass
    #npics-=1
    print(npics)
    return foregrounds[:,:,:npics],backgrounds[:,:,:npics]

def getindiviualpics(basename):
    import numpy as np
    from glob import glob
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits

    listofiles=glob(basename+'*.fit');
    print(listofiles)
    bunchsize=5
    npics=0;
    id1=[]
    foregrounds=np.zeros([512,512,bunchsize])
    backgrounds=np.zeros([512,512,bunchsize])
    #origpics=None#np.zeros([512,512,bunchsize])
    #bgmask = None#prepare_bgmask()
    #for currentdir in listofdirs:

        #print(currentdir)
        #listofiles=glob(currentdir+'/*.fit');

    for fn in listofiles:
        filename=fn
        print(npics, filename)
        try:
          hdl=pyfits.open(filename)
          a=hdl[0].data
          foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:]
          backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:]
          npics+=1
        except:
          print("Failed here")
          pass
    #npics-=1
    print(npics)
    return foregrounds[:,:,:npics],backgrounds[:,:,:npics]


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
    #foregrounds=None#np.zeros([512,512,bunchsize])
    #backgrounds=None#np.zeros([512,512,bunchsize])
    #origpics=None#np.zeros([512,512,bunchsize])
    #bgmask = None#prepare_bgmask()

    for currentdir in listofdirs:

        print(currentdir)
        listofiles=glob(currentdir+'/*.fit');

        for fn in listofiles:
            filename=fn
            print(npics, filename)
            hdl=pyfits.open(filename);
            a=hdl[0].data
            try:
              if not 'foregrounds' in locals():
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
            except:
                break
            if (npics==(bunchsize)):
                print('Converting')
                pics,optrefimages,tel = fringeremoval1( foregrounds,backgrounds,bgmask);
                #pics,optrefimages,tel = removefringe( foregrounds,backgrounds,bgmask);
                print('Saving, elapsed time',tel)
                saveimages(id1,pics)
                npics=0
                id1=[]

    print('Converting last', npics)
    fg2=foregrounds[:,:,:npics]
    bg2=backgrounds[:,:,:npics]
    #pics,optrefimages,tel = removefringe(fg2,bg2,bgmask)
    pics,optrefimages,tel = fringeremoval1( fg2,bg2,bgmask);
    print('Saving, elapsed time',tel)
    saveimages(id1,pics)
    return pics,origpics,npics

# - - - - - - - - - - - - - - - - - - - - - - - - \
# =|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
# =|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
# - - - - - - - - - - - - - - - - - - - - - - - - /

def filtertest(runs,n):
  from time import perf_counter
  BGmask=kl.prepare_bgmask()
  toplot,t1=kl.fringeremoval_otf(mydata[0,:,:],self.camera.BGpics[:,:,:self.camera.nBGs],BGmask)
  n_atoms,n_max=self.camera.getNatoms_otf(toplot)
  n_atoms = np.format_float_positional(n_atoms, precision = 3, unique = False, fractional = False, trim = 'k')

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
      for fn in listofiles:
            filename=fn
            print(npics, filename)
            try:
              hdl=pyfits.open(filename)
              a=hdl[0].data
              foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:]
              backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:]
              npics+=1
            except:
              print("Failed here")
              pass
    #npi
      b=filter_mask(a)
      c=filter_mask2(a)
      diff+=np.array_equal(b,c)
  toc = perf_counter()
  print(f'Filter_mask completed {runs} runs in {toc-tic} seconds; difference = {diff}')
  
if __name__=='__main__':
    bgMask=prepare_bgmask()
    FG,BG=getindiviualpics('0 Individual Images/test/Go_20250227')
    print(FG.shape,BG.shape)
    #FG,BG=getsomepics('20250219')
    myindex=4
    myFG=FG[:,:,myindex]
    refpic=-np.log(FG[:,:,myindex]/BG[:,:,myindex])
    test=fringeremoval_otf(myFG,BG,bgMask)
    import matplotlib.pyplot as plt
    plt.subplot(1,2,1)
    plt.imshow(test[0],cmap='inferno')
    plt.subplot(1,2,2)
    plt.imshow(refpic,cmap="inferno")
    plt.show()

