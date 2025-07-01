import numpy as np
import AIOUSB as da

da.AIOUSB_Init()
da.DACDirect(0,0,2024)
npts=100000
t=np.arange(npts)/npts
samples=8*npts
buffer=np.zeros((8,npts))
for j in range(8):
  buffer[j,:]=np.sin(t+j)*4096
buffer2=buffer.astype(np.ushort).flatten('C')
buffer2[-1]=buffer2[-1]+0x8000
out=da.DACOutputProcess(0,10000,samples,buffer2)
