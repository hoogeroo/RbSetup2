#!/usr/local/anaconda3/bin/python
import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import kicklib

def roundstr(x,n):
    if not n:
        return str(int(round(x,0)))
    else:
        return str(round(x,n))

data=[]
with open('/home/lab/picshare/temp.fits','rb') as file:
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
plt.imshow(FG, cmap = cm.inferno)
plt.colorbar()
plt.title('Foreground')

plt.figure()
plt.imshow(BG, cmap = cm.inferno)
plt.colorbar()
plt.title('Background')

plt.figure()
plt.imshow(empty, cmap = cm.inferno)
plt.colorbar()
plt.title('Zeroing shot')



top = kicklib.filter_mask2(FG - empty); bottom = kicklib.filter_mask2(BG - empty);
top[top<64] = 64; bottom[bottom<64] = 64
#OD = -np.log(ratio*top/bottom)
OD = -np.log(top/bottom)
#OD[OD>7] = 7
mask = np.ones(OD.shape, dtype = int)
mask[10:-10, 10:-10] = 0
empty_mean = np.mean(OD[mask])
OD -= empty_mean

plt.figure()
plt.imshow(OD, cmap = cm.inferno)
plt.colorbar()
plt.title('Optical Density')

A_of_px=((1e-3)/131)**2
Rb_crosssection = 1.3e-13 # See Ian Wenas' MSc thesis from 2007, pg65
N_atoms = A_of_px * np.sum(OD) / Rb_crosssection

print(f'Unrounded: Number of atoms = {N_atoms}')
try:
  power = np.floor(np.log10(N_atoms)/3)
  N_est = roundstr(N_atoms*10**(-3*power),1)
  print(f'Rounded: Number of atoms = {N_est} x 10^{int(3*power)}')
except Exception as e:
  print(f'Cannot round number - Exception:{e}')

#print(f'The unique values in the background photo are: {np.unique(empty/64.)}')
#print(f'The five smallest unique values in the foreground photo are: {np.unique(FG)[:5]}')
#print(f'The five smallest unique values in the background photo are: {np.unique(BG)[:5]}')
#print(f'The five smallest unique values in the empty photo are: {np.unique(empty)[:5]}')
#print(f'***\nThe five biggest unique values in the foreground photo are: {np.unique(FG)[-5:]}')
#print(f'The five biggest unique values in the background photo are: {np.unique(BG)[-5:]}')
plt.show()

