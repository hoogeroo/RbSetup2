import numpy as np

dac_names=['Trigger DDS','Dipole AOM Ampl.','MOT 2 coils current','Shutters','RF disable','Grey Molasses Shutter','Y Field','RF Freq Ramp']

dio_names = ['Camera Trigger','Unused']

EDnames=['Eagle DAC # '+str(i) for i in range(24)]
EDnames[3:6] = ['HH x','HH y','HH z']

#aom_names=[i+1 for i in range(8)]
#aom_names[:8] = ['Repump','1st MOT','2nd MOT','Push','Sheet','Shadow','Opt. pump','Free']
aom_names = ['Repump','1st MOT','2nd MOT','Push','Sheet','Shadow','Opt. pump','Free']

dac_prefire = np.zeros(len(dac_names))
#dac_prefire[1] = 1; dac_prefire[3] = 1 
#dac_prefire = np.array([0, .1, 0, .1, 0, 0, 0, 0])# times in ms

class dac_conversion():
  def __init__(self,dac_index):
    self.pars=np.zeros(10)
    self.pars[1]=1.0
    self.dac_index=dac_index
    self.minv=0.0
    self.maxv=5.0
    self.step=0.1
    
  def getval(self,inval):
    p=np.flip(self.pars)
    return np.polyval(p,inval)
  def getpars(self):
    return minv,maxv,step
  
class aom_amp_conversion(dac_conversion):
  def __init__(self,aom_index):
    super().__init__(self)
    self.aom_index = aom_index
    self.maxv = 1.0
    self.step = 0.05
    
  
dac_conversions=[]
for i in range(len(dac_names)):
  dac_conversions.append(dac_conversion(i))
  
dac_conversions[2].pars[1]=5/100
dac_conversions[2].maxv=100.0
dac_conversions[2].step=0.5

dac_conversions[-1].pars[1] = 5/100
dac_conversions[-1].maxv = 100.
dac_conversions[-1].step = 0.1


# Had to measure the AOM response to input voltage to figure out the conversion
# This approach should appropriately linearise it
# If you change the voltage divider box that leads to the AOM freq gen box, you might need to remeasure these
#
power_max = 100
#dipole_powers = np.array([0.013, 0.085, 1.4, 4.9, 10.0, 16.2, 23, 30.4, 38.1, 46, 53.8, 61.2, 67.9, 74.0, 79.1, 83.4, 86.7, 88.1]) # in milliWatts
#dipole_powers *= power_max/max(dipole_powers)
#dipole_volts = np.linspace(0,3.4, len(dipole_powers)) # in Volts
#dipole_pars = np.polyfit(dipole_powers, dipole_volts, 5)#We want to put in a desired power and get back a voltage

percentage = np.concatenate((np.arange(3, 10, 1), np.arange(10, 70, 10))) 
dipole_powers = np.array([23.3E-3, 59E-3, 0.165, 0.377, 0.715, 1.18, 1.79, 2.51, 14.6, 31, 49.3, 65.4, 71.1]) # in milliWatts
dipole_powers *= power_max/max(dipole_powers)
dipole_volts = 3.4 * percentage/max(percentage) # in Volts
dipole_pars = np.polyfit(dipole_powers, dipole_volts, 5)#We want to put in a desired power and get back a voltage

#dac_conversions[1].pars=np.array([0, 1/20])
dac_conversions[1].pars[0:len(dipole_pars)] = np.flip(dipole_pars)
dac_conversions[1].maxv = power_max
dac_conversions[1].step = 0.1

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

aom_amp_conversions = [aom_amp_conversion(i) for i in range(len(aom_names))]

sheet_powers = np.array([0.75,0.96,1.62,2.65,3.95,5.43,6.99,8.49,9.81,10.83,11.57,11.97,12.01])
sheet_powers -= min(sheet_powers) # I'm assuming that the offset (power(V = 0) =/= 0) is due to background, so subtract this off.
sheet_powers *= power_max/max(sheet_powers)
sheet_volts = np.linspace(0,0.6, len(sheet_powers))
sheet_pars = np.polyfit(sheet_powers, sheet_volts, 5)

aom_amp_conversions[4].pars[0:len(sheet_pars)] = np.flip(sheet_pars)
aom_amp_conversions[4].maxv = power_max
aom_amp_conversions[4].step = 0.1