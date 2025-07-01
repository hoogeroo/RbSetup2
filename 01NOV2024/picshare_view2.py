import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import kicklib

data=[]
with open('/home/lab/picshare/temp.fits','rb') as file:
  a = fits.open(file)
  data = a[0].data
  
FG = data[0,:,:]
BG = data[1,:,:]
empty = data[2,:,:]

plt.figure()
plt.imshow(FG, cmap = cm.inferno)
plt.title('Foreground')

plt.figure()
plt.imshow(BG, cmap = cm.inferno)
plt.title('Background')

plt.figure()
plt.imshow(empty, cmap = cm.inferno)
plt.title('Zeroing shot')

top = kicklib.filter_mask2(FG - empty); bottom = kicklib.filter_mask2(BG - empty);
top[top<64] = 64; bottom[bottom<64] = 64
OD = -np.log(top/bottom)
#OD[OD>7] = 7

plt.figure()
plt.imshow(OD, cmap = cm.inferno)
plt.title('Optical Density')

plt.figure()
plt.subplot(2,1,1)
plt.plot(OD[:,0])
plt.subplot(2,1,2)
plt.plot(OD[:,-1])

#print(f'The unique values in the background photo are: {np.unique(empty/64.)}')
print(f'The five smallest unique values in the foreground photo are: {np.unique(FG)[:5]}')
print(f'The five smallest unique values in the background photo are: {np.unique(BG)[:5]}')
print(f'The five smallest unique values in the empty photo are: {np.unique(empty)[:5]}')
print(f'***\nThe five biggest unique values in the foreground photo are: {np.unique(FG)[-5:]}')
print(f'The five biggest unique values in the background photo are: {np.unique(BG)[-5:]}')
plt.show()

