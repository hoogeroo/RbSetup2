import DAQ


class adc():
    def __init__(self):
      self.snADC=1000034495
      self.EDRE=DAQ.EDRE_Interface()
    def read(self,channel):
      uVolt=DAQ.ctypes.c_long(0)
      output=0.0
      for i in range(10):
          result=self.EDRE.fifo.EDRE_ADSingle(self.snADC,channel,2,0,DAQ.ctypes.byref(uVolt))
          output=output+uVolt.value/10000.0
      #print(result)
      return -output
    
if __name__=='__main__':
  myadc=adc()
  print(myadc.read(0))
