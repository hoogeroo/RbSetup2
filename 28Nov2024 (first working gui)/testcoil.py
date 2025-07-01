from AIOUSB import DACDirect,GetDevices
from time import sleep

a=GetDevices()

while 1:
  DACDirect(0,2,256)
  sleep(1)
  DACDirect(0,2,0)
  sleep(1)

