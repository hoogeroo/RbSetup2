import comedi as c

class adc():
    def __init__(self):
      self.device=c.comedi_open('/dev/comedi4')
      self.max=c.comedi_get_maxdata(self.device,0,0)
      self.range=c.comedi_get_range(self.device,0,0,0)
    
    def read(self,channel):
      res,data=c.comedi_data_read(self.device,0,channel,0,c.AREF_GROUND)
      return c.comedi_to_phys(data,self.range,self.max)
    
if __name__=='__main__':
  myadc=adc()
  print(myadc.read(0))
