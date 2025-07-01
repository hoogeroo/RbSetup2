from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

AFG_TCP="130.216.50.158"
rframpID = 7

class TekAFG(QGroupBox):
  def __init__(self, parent=None):
      super().__init__(parent=parent)
      self.layout=QGridLayout()
      self.layout.setVerticalSpacing(0)
      self.setFixedHeight(80)
      
      self.RF_start_freq=QDoubleSpinBox()
      self.RF_start_freq.setValue(10.0)
      self.RF_start_label=QLabel("RF start")
      self.RF_start_freq.valueChanged.connect(self.Change_RF_Freqs)
      self.layout.addWidget(self.RF_start_label,0,0)
      self.layout.addWidget(self.RF_start_freq,1,0)
      
      self.RF_stop_freq=QDoubleSpinBox()
      self.RF_stop_freq.setValue(5.0)
      self.RF_stop_label=QLabel("RF stop")
      #self.RF_stop_freq.valueChanged.connect(self.Change_RF_stopF)
      self.RF_stop_freq.valueChanged.connect(self.Change_RF_Freqs)
      self.layout.addWidget(self.RF_stop_label,0,1)
      self.layout.addWidget(self.RF_stop_freq,1,1)
      
      self.RF_stage_select=QComboBox()
      self.RF_stage_label=QLabel("RF Stage")
      self.layout.addWidget(self.RF_stage_label,0,2)
      self.layout.addWidget(self.RF_stage_select,1,2)

      self.RF_amplitude=QDoubleSpinBox()
      self.RF_ampl_label=QLabel("RF Amplitude (mV)")
      self.RF_amplitude.setRange(0,1000)
      self.RF_amplitude.setValue(150)
      self.RF_amplitude.valueChanged.connect(self.Change_RF_amplitude)
      self.layout.addWidget(self.RF_ampl_label,0,3)
      self.layout.addWidget(self.RF_amplitude,1,3)
      
      self.RF_sweep_time=0
      
      self.RF_sweepstyle=QComboBox()
      self.RF_swestylabel = QLabel("RF Sweep Style")
      self.RF_sweepstyle.addItem("Linear")
      self.RF_sweepstyle.addItem("Logarithmic")
      self.RF_sweepstyle.currentTextChanged.connect(lambda linlog = self.RF_sweepstyle.currentText():self.Change_RF_sweepstyle(linlog))
      self.layout.addWidget(self.RF_swestylabel,0,4)
      self.layout.addWidget(self.RF_sweepstyle,1,4)

      self.setLayout(self.layout)

  def Change_RF_stopF(self):
      newvalue=self.RF_stop_freq.value()*1e6
      try:
          import pyvisa
          rm=pyvisa.ResourceManager('@py')
          #rm.open_resource('TCPIP::130.216.50.90::INSTR')
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:FREQ:STOP '+str(newvalue))
          afg.close()
      except:
          pass

  def Change_RF_startF(self):
      newvalue=self.RF_start_freq.value()*1e6
      try:
          import pyvisa
          rm=pyvisa.ResourceManager('@py')
          #rm.open_resource('TCPIP::130.216.50.91::INSTR')
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:FREQ:START '+str(newvalue))
          afg.close()
      except:
          pass
        
  def Change_RF_Freqs(self):
      start=self.RF_start_freq.value()*1e6
      stop=self.RF_stop_freq.value()*1e6
      newcent=int((start+stop)/2)
      newdev=abs(int(start-newcent))
      
      try:
        immediateparentflag = False
        for attr in dir(self.parent()):
          if attr == "Stages":
            immediateparentflag = True
        
        if immediateparentflag:
          allboxes = self.parent()
        else:
          allboxes = self.parent().parent().parent().parent() # oof, dont ask
                                                              # After changing the structure of the GUI from allboxes alone to a tabbed window, 
                                                              # we now have to work our way 'through the onion'
                                                              # aka out of the widget, stackedwidget then tabwidget in order to reach allboxes
            #print("allboxes.%s = %r" % (attr, getattr(self.parent(), attr)))
        
        rangevals = [self.RF_start_freq.value(),self.RF_stop_freq.value()]
        stages = allboxes.Stages.stages
        for stage in stages:
          stage.boxes[rframpID].adjustrange(min(rangevals),max(rangevals))
      except Exception as e:
        print(f'Attempt at changing RF box ranges failed!\nException: {e}')
        #pass
      
      try:
          import pyvisa
          import time
          rm=pyvisa.ResourceManager('@py')
          #rm.open_resource('TCPIP::130.216.50.91::INSTR')
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:FREQ '+str(newcent))
          afg.close()
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:FM:DEV '+str(newdev))
          afg.close()
      except:
          pass

  def Change_RF_length(self):
      t=self.RF_sweep_time
      try:
          import pyvisa
          rm=pyvisa.ResourceManager('@py')
          #rm.open_resource('TCPIP::130.216.50.91::INSTR')
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:SWE:TIME '+str(t)+'ms')
          afg.close()
      except:
          pass

  def Change_RF_amplitude(self):
      newvalue=self.RF_amplitude.value()/1000
      try:
          import pyvisa
          rm=pyvisa.ResourceManager('@py')
          #rm.open_resource('TCPIP::130.216.50.91::INSTR')
          afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
          afg.write('SOUR1:VOLT:LEV:IMM:AMPL '+str(newvalue)+'Vpp')
          afg.close()
      except:
          pass
        
  def Change_RF_sweepstyle(self,linlog):
    assert linlog=='Linear' or linlog=='Logarithmic'; 'The sweep style must either be linear or logarithmic!'
    if linlog == 'Linear':
        newvalue='LIN'
    else:
        newvalue='LOG'
    try:
        import pyvisa
        rm=pyvisa.ResourceManager('@py')
        #rm.open_resource('TCPIP::130.216.50.91::INSTR')
        afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
        afg.write('SOUR1:SWE:SPAC '+newvalue)
        afg.close()
        #print(newvalue)
    except:
        pass 
        
  def Change_RF_stage(self,newvalue):
    #newvalue=self.RF_sweep_time.value()
    try:
        import pyvisa
        rm=pyvisa.ResourceManager('@py')
        #rm.open_resource('TCPIP::130.216.50.91::INSTR')
        afg=rm.open_resource('TCPIP::'+AFG_TCP+'::INSTR')
        afg.write('SOUR1:SWE:TIME '+str(newvalue)+'ms')
        print(f'New sweep time: {newvalue}')
        afg.close()
        #print(newvalue)
    except:
        pass 

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()Change_RF_stopF
#         panel=TekAFG()
#         self.setCentralWidget(panel)

def main():
   app = QApplication(sys.argv)
   mw = QMainWindow()
   panel=TekAFG()
   mw.setCentralWidget(panel)
   #layout=QGridLayout()
   #mw.setLayout(layout)
   #layout.addWidget(panel)
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
