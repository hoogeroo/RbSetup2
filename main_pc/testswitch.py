import AIOUSB as da
from time import sleep
print(da.GetDevices())
sleep(0.1)
while 1:
  count=4095
  DACid=3
  da.DACDirect(0,DACid,count)
  sleep(0.1)
  da.DACDirect(0,DACid,0)
  sleep(0.1)