import numpy as np

#dac_names=['DAC # '+str(i) for i in range(24)]
#dac_names[:8]=['Trigger DDS','Trigger Camera','MOT 2 coils current','Shutters','RF disable','Science coils','Lens 1','Lens 2']
dac_names=['Trigger DDS','Trigger Camera','MOT 2 coils current','Shutters','RF disable','Science coils','Lens 1','Lens 2']

#dac_names[0]=['Trigger DDS']
#dac_names[1]='Trigger Camera' 
#dac_names[2]='MOT 2 coils current' 
#dac_names[3]='Shutters' 
#dac_names[4]='RF disable' 
#dac_names[5]='Science coils' 
#dac_names[6]='Lens 1' 
#dac_names[7]='Lens 2' 

EDnames=['Eagle DAC # '+str(i) for i in range(24)]
EDnames[3:6] = ['HH x','HH y','HH z']
#EDnames = ['HH x','HH y','HH z']
#for i in range(24):
#  EDnames.append('Eagle DAC # '+str(i))
#EDnames[3]='HH x'
#EDnames[4]='HH y'
#EDnames[5]='HH z'

aom_names=[i+1 for i in range(6)]
aom_names[:6] = ['Repump','1st MOT','2nd MOT','Push','Dipole','Shadow']
#aom_names[0]='Repump'
#aom_names[1]='1st MOT'
#aom_names[2]='2nd MOT'
#aom_names[3]='Push'
#aom_names[4]='Dipole'
#aom_names[5]='Shadow'

class dac_conversion():
  def __init__(self):
    self.pars=np.zeros(10)
    pars[1]=1.0
  def getval(self,inval):
    p=np.flip(self.pars)
    return np.polyval(p,inval)
  
dac_conversions=[]
#for i in range(8):
#  dac_conversions.append(dac_conversion())
#dac_conversions[2].pars[1]=5/100
#dac_funcs=[]
#for i in range(8):
  #dac_funcs.append(lambda:x x)

#dac_funcs[2]=(lambda x: x/20)     
