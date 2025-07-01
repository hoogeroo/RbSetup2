# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 11:39:20 2014
piclib.py
@author: maarten
"""
import numpy as np

def addpics(filenames):
    #[y s]=addpics(filenames) 
    # Adds the pictures in filenames, and returns a 2D array  y and a scalefactor
    # s, which is the velocity of one pixel
    y=np.zeros([512,512]);
    n=0
    for filename in filenames:
        t1,t2=getpic(filename,0);
        y=y+t1;
        n=n+1
    y=y/n;
    s=t2;
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
    #command=sprintf('%s%s','gunzip ',filename);
    try:
        matname=filename[0:-3]+'mat';
        #print(matname)
        tmp=loadmat(matname);
        out=tmp['a1'];
        if (mat_only):
#            print("returning out")
            return out, 1
        hdulist=pyfits.open(filename);
        if (dopic):
            print('Found matfile')
    except:
        try:
            matname=matname[0:4]+'/'+matname;
            #print (matname)
            tmp=loadmat(matname);
            out=tmp['a1']
            fn2=filename[0:4]+'/'+filename;
            #print(fn2)
            hdulist=pyfits.open(fn2);
            #print('there')
            if (dopic):
                print('Found matfile')
            #break
        except:
            try:
                hdulist=pyfits.open(filename)
                print("Trying impo", filename)
                a=hdulist[0].data
                #print(a.shape)
                if (dopic):
                   print("found fits file",filename)
                #print(hdulist)
                #fileinfo = fitsinfo(filename);
            except FileNotFoundError:
                print("Why are we here")
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
            out=filter2(out)
            plt.imshow(out)
        plt.show()
    return out,scale
  
def fringeremoval(foregrounds,backgrounds,bgmask):
    import time
    #import numpy as np
    from scipy.linalg import lu
    t=time.time()
    k=np.nonzero(bgmask.flatten())
    nk=np.size(k)
    sx,sy,nimgs=foregrounds.shape
    R=backgrounds.reshape([sx*sy,nimgs])
    A=foregrounds.reshape([sx*sy,nimgs])
    O1=np.zeros([sx*sy,nimgs])
    Rk=R[k,:].reshape([nk,nimgs])
    
    p,l,u=lu(np.dot(np.transpose(Rk),Rk))
    pp=np.nonzero(p)[1]
    
    for j in range(nimgs):
        Akj=A[k,j].reshape(nk)
        b=np.dot(np.transpose(Rk),Akj)
        c=np.linalg.solve(u,np.linalg.solve(l,b[pp,:]))
        O1[:,j]=np.dot(R,c)
        
    odimages=np.reshape(-np.log(A/O1),[sx,sy,nimgs])
    oprefs=np.reshape(O1,[sx,sy,nimgs])
    elapsed=time.time()-t
    return odimages,oprefs,elapsed
        
def fringeremoval1(foregrounds,backgrounds,bgmask):
    import time
    #import numpy as np
    #from scipy.linalg import lu
    t=time.time()
    k=np.nonzero(bgmask.flatten())
    nk=np.size(k)
    sx,sy,nimgs=foregrounds.shape
    R=backgrounds.reshape([sx*sy,nimgs])
    A=foregrounds.reshape([sx*sy,nimgs])
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
        
    odimages=np.reshape(-np.log(A/O1),[sx,sy,nimgs])
    oprefs=np.reshape(O1,[sx,sy,nimgs])
    elapsed=time.time()-t
    return odimages,oprefs,elapsed        
  
def fringeremoval2(foregrounds,backgrounds,bgmask):
    import time
    #import numpy as np
    t=time.time()
    A=bgmask.flatten()
    sx,sy,nfiles=foregrounds.shape
    #sy=foregrounds.shape[1]
    pics=np.zeros([sx,sy,nfiles])
    thisbg=np.zeros([sx,sy,nfiles])
    for i in range(nfiles):
        t1=backgrounds[:,:,i]*bgmask
        t2=t1.flatten()
        A=np.column_stack([A,t2])
    Ap=np.transpose(A)
    b=np.dot(Ap,A)
    for i in range(nfiles):
        y=(foregrounds[:,:,i]*bgmask).flatten()
        c=np.dot(Ap,y)
        sol=np.linalg.solve(b,c)
        if i==0:
            print(sol)
        thisbg[:,:,i]=sol[0]
        for j in range(nfiles):
            thisbg[:,:,i]=thisbg[:,:,i]+sol[j+1]*backgrounds[:,:,j]
        thisbg[:,:,i]=thisbg[:,:,i]+sol[0]
        pics[:,:,i]=-np.log(foregrounds[:,:,i]/thisbg[:,:,i])
    elapsed=time.time()-t
    #print elapsed
    return pics,thisbg,elapsed
      
def saveimages(ids,pics):
    from scipy.io import savemat
    i=0    
    for fn in ids:
        matname=fn[0:-3]+'mat';
        print(matname)
        a={}
        a['a1']=pics[:,:,i]                    
        #a1=pics[:,:,i].flatten()
        #print a1.shape()
        savemat(matname,a);
        i=i+1
        #clear foregrounds
        #clear backgrounds

def filter2(z):
    out=np.zeros([z.shape[0]-2,z.shape[1]-2])
    f=np.array([[0.1,0.1,0.1],[0.1,0.2,0.1],[0.1,0.1,0.1]])
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            for k in range(3):
                for l in range(3):
                    out[i,j]=out[i,j]+f[k,l]*z[i+k,j+l]
    return out

def getallpics(basename,bunchsize):
    import numpy as np
    from glob import glob
    try:
      import astropy.io.fits as pyfits
    except:
      import pyfits  
    bgmask=np.zeros([512,512]);
    bgcor=50
    bgmask[0:(bgcor),0:(bgcor)]=1;
    bgmask[0:(bgcor),-bgcor:]=1;
    bgmask[-bgcor:,0:(bgcor)]=1;
    bgmask[-bgcor:,-bgcor:]=1;
        
    listofdirs=glob(basename+'*');
    #print listofdirs
    #ndirs=length(listofdirs);
    
    #foregrounds=cell(1,1);
    #backgrounds=cell(1,1);
    npics=0;
    id1=[]
    foregrounds=np.zeros([512,512,bunchsize])
    backgrounds=np.zeros([512,512,bunchsize])
    origpics=np.zeros([512,512,bunchsize])
    for currentdir in listofdirs:
        #currentdir=listofdirs[k].name;
        print(currentdir)
        listofiles=glob(currentdir+'/*.fit');
        #print listofiles
        #nfiles=length(listofiles);
        for fn in listofiles:
            #fn=listofiles(j).name;
            #t1=np.size(fn);
            #if (t1>4):
            #    ext=fn[-3:-1];
            #else:
            #    ext=fn;
            
            filename=fn
            print(npics, filename)
            hdl=pyfits.open(filename);
            a=hdl[0].data
            foregrounds[:,:,npics]=a[0,:,:]-a[2,:,:];
            backgrounds[:,:,npics]=a[1,:,:]-a[2,:,:];
            origpics[:,:,npics]=-np.log(foregrounds[:,:,npics]/backgrounds[:,:,npics])
            id1.append(filename)
            npics=npics+1
            if (npics==(bunchsize)):
                print('Converting')
                pics,optrefimages,tel = fringeremoval1( foregrounds,backgrounds,bgmask);
                print('Saving, elapsed time',tel)
                saveimages(id1,pics)
                npics=0
                id1=[]
    print('Converting last', npics)
    fg2=foregrounds[:,:,:npics]
    bg2=backgrounds[:,:,:npics]
    pics,optrefimages,tel = fringeremoval1(fg2,bg2,bgmask) 
    print('Saving, elapsed time',tel)
    saveimages(id1,pics)
    return pics,origpics,npics
#        try:
#            [ pics,optrefimages,avgimage,timer ] = fringeremoval2( foregrounds,backgrounds,bgmask);
#        except:
#           print 'folder ' +currentdir+' has no data files in it\n' 
#        for i in range(l):
#            tmp=id1[i]
#            matname=tmp[0:-3]+'mat';
#            a1=pics[:,:,i]
#            #savemat(matname,a1);
