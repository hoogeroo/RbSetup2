from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import os
import EagleDAC_main as edac
from qmsbox import *

class MySpinBox(QSpinBox):
  def __init__(self):
    super(QSpinBox,self).__init__()
    self.valueChanged.connect(self.colourbox)
    self.setAutoFillBackground(True)
  def colourbox(self):
    p=self.palette()
    mycolour=QColor.fromRgbF(0,1,0)
    p.setColor(self.backgroundRole(),mycolour)
    self.setPalette(p)
    #print(self.parent().parent())
    #self.parent().parent().allboxes.Spinboxes[

class MultiGoPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.layout=QGridLayout()
        #self.setTitle('MultiGo Settings')
        # self.MultiGoButton=QPushButton('MultiGo')
        # self.layout.addWidget(self.MultiGoButton,3,1)
        # self.MultiGoButton.clicked.connect(self.MultiGo)
        self.cbExpKind=QComboBox()
        eklabel=QLabel("Kind")
        self.sbNCycles=QSpinBox()
        self.sbNCycles.setValue(11)
        self.NClabel=QLabel("Steps")
        
        slabel=QLabel("Step")
        self.mgCount=QLabel('0 of '+str(self.sbNCycles.value()))
        
        
        #self.cbExpKind.addItem('X Field')
        #self.cbExpKind.addItem('Y Field')
        #self.cbExpKind.addItem('Z Field')
        
        self.sbExpFrom=QDoubleSpinBox()
        #self.sbExpFrom.setValue(0.0)
        self.sbExpTo=QDoubleSpinBox()
        #self.sbExpTo.setValue(1.0)
        #fromlabel=QLabel("From")
        #tolabel=QLabel("To")
        
        
        
        
        #self.layout.addWidget(tolabel,1,0)
        #self.layout.addWidget(fromlabel,0,0)
        #self.layout.addWidget(self.sbExpFrom,0,1)
        #self.layout.addWidget(self.sbExpTo,1,1)
        
        self.layout.addWidget(eklabel,0,0)
        self.layout.addWidget(self.cbExpKind,0,1)
        self.layout.addWidget(self.NClabel,1,0)
        self.layout.addWidget(self.sbNCycles,1,1)
        self.layout.addWidget(slabel,2,0)
        self.layout.addWidget(self.mgCount,2,1)
        self.setLayout(self.layout)


class MultiGoDialog(QDialog):
    def __init__(self, filename,devnames,stagenames, tek):
        super(QDialog, self).__init__()
        self.setWindowTitle("MultiGo Parameters")
        self.layout = QGridLayout()
        self.params=Parameters(devnames,stagenames, tek)
        #self.devnames=devnames
        #self.stagenames=stagenames
        self.namebox=QLineEdit()
        self.namebox.setText(filename)
        self.layout.addWidget(self.namebox,0,0)
        #self.myread(filename)
        self.newread(filename)
        
        self.addParButton=QPushButton('+')
        self.delParButton=QPushButton('-')
        self.addParButton.clicked.connect(self.newpar)
        self.delParButton.clicked.connect(self.delpar)
        self.layout.addWidget(self.addParButton,0,1)
        self.layout.addWidget(self.delParButton,0,2)
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.naccept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox,40,0)
        
        self.loadButton=QPushButton("Open")
        self.saveButton=QPushButton("Save")
        self.layout.addWidget(self.loadButton,0,3)
        self.layout.addWidget(self.saveButton,0,4)
        self.loadButton.clicked.connect(self.newread2)
        self.saveButton.clicked.connect(self.newsave)
        #self.loadButton.clicked.connect(self.myread2)
        #self.saveButton.clicked.connect(self.mysave)
        
        labelnames=['Description','Initial','Final','Stage #','Device #','Type','Linear Ramp']
        for i, name in enumerate(labelnames):
            self.layout.addWidget(QLabel(name),1,i)
            
        self.setLayout(self.layout)
    
    def clear_params(self):
        pars=self.params.params
        for i in range(len(pars)):
            self.delpar()
    
    def newread2(self):
        #filename=self.namebox.text()
        name,path = QFileDialog.getOpenFileName(self, 'Open file','./',"MultiGo files (*.mgo)")
        i=name.rfind("/")
        filename=name[i+1:]
        #print(name, path)
        self.namebox.setText(filename)
        self.newread(filename)
        #self.myread(filename)
        
    def newsave(self):
        fn=self.namebox.text()
        if os.path.exists(fn):
           print("File exists")
           os.remove(fn)
        f=open(fn,'w')
        ps=self.params.params
        for p in ps:
          paramname = p.title.text()
          f.write(f'{paramname.replace(" ", "_")} {p.Startbox.value()} {p.Stopbox.value()} {p.time.currentIndex()} {p.channel.currentIndex()} {p.mytype.currentIndex()} {p.rampcheck.checkState()}\n')
        f.close()
        
    def newread(self,filename):
        self.clear_params()
        #filename=filename+".mgo"
        #print(filename)
        if os.path.exists(filename):
            f=open(filename,"r")
            ls=f.readlines()
            #self.namebox.setText(filename)
            if len(ls)>0 and len(ls[0])>0:
                for j in range(len(ls)):
                   self.newpar()
                   #print(j)
            pars=self.params.params
            npars=len(pars)
            print(f'During read - Number of lines: {len(ls)}; Number of parameters: {npars}')
            for i,l in enumerate(ls):
                p=l.split(' ')
                #print(i)
                try:
                    pars[i].mytype.setCurrentIndex(int(p[5]))
                except:
                    print('No types included in this file; might break with new set-up')
                try:
                    pars[i].rampCheck.isChecked() # Params dont necessarily come with rampCheck - if it doesnt exist, we need to provide it!
                except:
                    setattr(pars[i],'rampCheck',QCheckBox())
                try:
                    pars[i].rampCheck.setCheckState(int(p[6].rstrip('\n'))) # If the mgo file doesnt have the rampCheck box, we'll default to false
                except:
                    pars[i].rampCheck.setCheckState(False)
                #except:
                #    print('p[6].rstrip("\n") = '+p[6].rstrip("\n"))
                #    print()
                #    print('No ramp check included in this file; might break with new set-up')    
                      
                pars[i].channel.setCurrentIndex(int(p[4]))
                
                pars[i].title.setText(p[0].replace("_", " "))
                pars[i].Startbox.setValue(float(p[1]))
                pars[i].Stopbox.setValue(float(p[2]))
                pars[i].time.setCurrentIndex(int(p[3]))
                
            f.close()
        #print("Hello")
        
    def newpar(self):
        self.params.newpar()
        pars=self.params.params
        npars=len(pars)
        hlines=1
        self.layout.addWidget(pars[-1].title,npars+hlines,0)
        self.layout.addWidget(pars[-1].Startbox,npars+hlines,1)
        self.layout.addWidget(pars[-1].Stopbox,npars+hlines,2)
        self.layout.addWidget(pars[-1].time,npars+hlines,3)
        self.layout.addWidget(pars[-1].channel,npars+hlines,4)
        self.layout.addWidget(pars[-1].mytype,npars+hlines,5)
        self.layout.addWidget(pars[-1].rampcheck,npars+hlines,6)
        
    def delpar(self):
        pars=self.params.params
        self.layout.removeWidget(pars[-1].title)
        self.layout.removeWidget(pars[-1].Startbox)
        self.layout.removeWidget(pars[-1].Stopbox)
        self.layout.removeWidget(pars[-1].time)
        self.layout.removeWidget(pars[-1].channel)
        self.layout.removeWidget(pars[-1].rampcheck)
        self.layout.removeWidget(pars[-1].mytype)
        self.params.delpar()
        self.adjustSize()
        
    def naccept(self):
        self.newsave()
        #self.mysave()
        self.close()
        
    #def reject(self):
    #    print("rejected")
    #    self.close()
        
    #def reject(self):
    #    print("rejected")
    #    self.close()
    
def multigomenu(MGPanel,devnames,stagenames, tek): # Open Multigo dialog. Something odd is that it takes two clicks to close.
    filename=MGPanel.cbExpKind.currentText()+".mgo"
    dlg=MultiGoDialog(filename,devnames,stagenames, tek)
    if dlg.exec_():
      print('success')
      dlg.mysave()
      #self.addMGFiles()
      dlg.close()
    else:
      print("fail")
      dlg.close()
      
class Parameters():
    def __init__(self,devnames,stagenames, tek):
        self.params = []
        self.devnames = devnames
        self.stagenames = stagenames
        self.tek = tek
        
    class AParam():
        def __init__(self,x,y):
            self.Startbox=QDoubleSpinBox()
            self.Stopbox=QDoubleSpinBox()
            self.title=QLineEdit()
            self.time=MySpinBox()
            self.time.setValue(x)
            self.channel=QSpinBox()
            self.channel.setValue(y)
            self.rampcheck=QCheckBox()
            self.mytype=QComboBox()
            types = ["EagleDAC","AOM","DAC","Time"]
            for devtype in types:
                self.mytype.addItem(devtype)

    class NewParam():
        def __init__(self):
            self.Startbox=QDoubleSpinBox()
            self.Stopbox=QDoubleSpinBox()
            self.title=QLineEdit()
            self.time=QComboBox()
            self.channel=QComboBox()
            self.rampcheck=QCheckBox()
            self.mytype=QComboBox()
            types = ["EagleDAC","AOM","DAC","Time","RF (freq)","RF (amp)"]
            for devtype in types:
                self.mytype.addItem(devtype)
  
    def delpar(self):
        self.params[-1].title.deleteLater()
        self.params[-1].Startbox.deleteLater()
        self.params[-1].Stopbox.deleteLater()
        self.params[-1].time.deleteLater()
        self.params[-1].channel.deleteLater()
        self.params[-1].rampcheck.deleteLater()
        self.params[-1].mytype.deleteLater()
        del self.params[-1]
        #self.setLayout(self.layout)

    def newpar(self):
        self.params.append(self.NewParam())
        self.params[-1].mytype.setCurrentIndex(0)
        self.params[-1].time.setCurrentIndex(0)
        self.params[-1].channel.setCurrentIndex(0)
        self.params[-1].channel.currentIndexChanged.connect(lambda state, x=self.params[-1]: self.fixBoxes(x))
        self.load_devices_stages(self.params[-1])
        self.params[-1].title.setText("Parameter_"+str(len(self.params)))
        self.params[-1].mytype.currentIndexChanged.connect(lambda state, x=self.params[-1]: self.load_devices_stages(x))

    def load_devices_stages(self,myparam):
        self.update_devices(myparam)
        self.update_stages(myparam)
        self.fixBoxes(myparam)
        
    def fixBoxes(self,myparam):
        temp=[]
        stepsize=1
        if myparam.mytype.currentText()=="Time":
          temp=Timebox()
          Vmin = temp.minimum(); Vmax = temp.maximum()
        elif myparam.mytype.currentText()=="EagleDAC":
          temp = edac.Eagle_box(0,0)
          Vmin= temp.minimum(); Vmax = temp.maximum(); stepsize = temp.singleStep()
        elif myparam.mytype.currentText()=="AOM":
          Vmin,Vmax,stepsize = self.fixAOMboxes(myparam)
        elif myparam.mytype.currentText()=="DAC":
          temp=DAC_Box(0,0)
          Vmin = temp.minimum(); Vmax = temp.maximum(); stepsize = temp.singleStep()
        elif myparam.mytype.currentText()=="RF (freq)":
          Vmin=1; Vmax = 100
        elif myparam.mytype.currentText()=="RF (amp)":
          Vmin = 0; Vmax = 1000
        else:
          Exception('The box type broke!')
        self.setBoxRange(myparam,Vmin,Vmax,stepsize)
        del temp
    
    def fixAOMboxes(self,myparam):
      dev = myparam.channel.currentText()
      Vmin,Vmax,stepsize=0,0,1
      if dev[-4:]=="Freq":
        Vmin = 55; Vmax = 105
      elif dev[-4:]=="Ampl":
        Vmin = 0; Vmax = 1; stepsize = 0.05
      return Vmin,Vmax,stepsize
    
    def setBoxRange(self,myparam,Vmin,Vmax,stepsize):
        myparam.Startbox.setRange(Vmin,Vmax)
        myparam.Startbox.setSingleStep(stepsize)
        myparam.Stopbox.setRange(Vmin,Vmax)
        myparam.Stopbox.setSingleStep(stepsize)
        myparam.Startbox.setToolTip('Allowed range: '+str(Vmin)+' -> '+str(Vmax))
        myparam.Stopbox.setToolTip('Allowed range: '+str(Vmin)+' -> '+str(Vmax))
        
        
    def update_devices(self,myparam):
        myparam.channel.clear()
        curtext=myparam.mytype.currentText()
        if not curtext == 'Time' and not curtext == 'RF (amp)':
            myparam.channel.setEnabled(True)
            if not curtext == 'RF (freq)':
                myparam.channel.addItems(self.devnames[myparam.mytype.currentText()])
            else:
                myparam.channel.addItems([self.tek.RF_start_label.text(), self.tek.RF_stop_label.text()])
        else:
            myparam.channel.setEnabled(False)

    def update_stages(self,myparam):
        myparam.time.clear()
        if not myparam.mytype.currentText() == 'EagleDAC':
            myparam.time.setEnabled(True)
            myparam.time.addItems(self.stagenames)
        else:
            myparam.time.setEnabled(False)
            
    def newread(self,filename):
        if len(self.params)>0:
            for i in range(len(self.params)):
                self.delpar()
        if os.path.exists(filename):
            with open(filename,"r") as f:
                ls=f.readlines()
                #self.namebox.setText(filename)
                if len(ls)>0 and len(ls[0])>0:
                    for j in range(len(ls)):
                      self.newpar()
                      #print(j)
                pars=self.params
                npars=len(pars)
                print('During read - Number of lines: ',len(ls),'; Number of parameters: ',npars)
                for i,l in enumerate(ls):
                    p=l.split(' ')
                    #print(p)
                    try:
                      try:
                          pars[i].mytype.setCurrentIndex(int(p[5]))
                      except:
                          print('No types included in this file; might break with new set-up')
                      try:
                          pars[i].rampCheck.isChecked() # Params dont necessarily come with rampCheck - if it doesnt exist, we need to provide it!
                      except:
                          setattr(pars[i],'rampCheck',QCheckBox())
                      try:
                          pars[i].rampCheck.setCheckState(int(p[6].rstrip('\n'))) # If the mgo file doesnt have the rampCheck box, we'll default to false
                      except:
                          pars[i].rampCheck.setCheckState(False)
                      #try:
                      #    pars[i].rampCheck.setCheckState(int(p[6]))
                      #except:
                      #    print('No ramp check included in this file; might break with new set-up')    
                      pars[i].channel.setCurrentIndex(int(p[4]))
                      pars[i].time.setCurrentIndex(int(p[3]))
                      
                      pars[i].title.setText(p[0])
                      pars[i].Startbox.setValue(float(p[1]))
                      pars[i].Stopbox.setValue(float(p[2]))
                      
                    except:
                      pass

        
    def accept(self):
        self.mysave()
        self.close()

if __name__=='__main__':
  import sys
  app=QApplication(sys.argv)
  w=MultiGoDialog("Fmolasses.mgo")
  #w.myread("untitled.mgo")
  w.show()
  sys.exit(app.exec_())
