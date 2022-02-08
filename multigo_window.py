from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import os

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

class AParam():
  def __init__(self,x,y):
    self.Startbox=QDoubleSpinBox()
    self.Stopbox=QDoubleSpinBox()
    self.title=QLineEdit()
    self.time=MySpinBox()
    self.time.setValue(x)
    self.channel=QSpinBox()
    self.channel.setValue(y)
    self.mytype=QComboBox()
    self.mytype.addItem("EagleDAC")
    self.mytype.addItem("AOMpar")
    self.mytype.addItem("DACpar")
    self.mytype.addItem("Time")

class MultiGoPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.layout=QGridLayout()
        # self.MultiGoButton=QPushButton('MultiGo')
        # self.layout.addWidget(self.MultiGoButton,3,1)
        # self.MultiGoButton.clicked.connect(self.MultiGo)
        self.cbExpKind=QComboBox()
        self.sbNCycles=QSpinBox()
        self.sbNCycles.setValue(11)
        self.layout.addWidget(self.sbNCycles,3,1)
        self.NClabel=QLabel("Steps")
        self.layout.addWidget(self.NClabel,3,0)
        self.cbExpKind.addItem('X Field')
        self.cbExpKind.addItem('Y Field')
        self.cbExpKind.addItem('Z Field')
        self.sbExpFrom=QDoubleSpinBox()
        self.sbExpFrom.setValue(0.0)
        self.sbExpTo=QDoubleSpinBox()
        self.sbExpTo.setValue(1.0)
        fromlabel=QLabel("From")
        tolabel=QLabel("To")
        eklabel=QLabel("Kind")
        slabel=QLabel("Step")
        self.layout.addWidget(tolabel,1,0)
        self.layout.addWidget(fromlabel,0,0)
        self.layout.addWidget(eklabel,2,0)
        self.layout.addWidget(slabel,4,0)
        self.layout.addWidget(self.sbExpFrom,0,1)
        self.layout.addWidget(self.sbExpTo,1,1)
        self.layout.addWidget(self.cbExpKind,2,1)
        self.mgCount=QLabel('0 of '+str(self.sbNCycles.value()))
        self.layout.addWidget(self.mgCount,4,1)
        self.setLayout(self.layout)


class MultiGoDialog(QDialog):
    def __init__(self, filename):
        super(QDialog, self).__init__()
        self.setWindowTitle("MultiGo Parameters")
        self.layout = QGridLayout()
        self.params=[]
        self.namebox=QLineEdit()
        self.namebox.setText(filename)
        self.layout.addWidget(self.namebox,0,0)
        self.myread(filename)
        self.addParButton=QPushButton('+')
        self.delParButton=QPushButton('-')
        self.addParButton.clicked.connect(self.newpar)
        self.delParButton.clicked.connect(self.delpar)
        self.layout.addWidget(self.addParButton,0,1)
        self.layout.addWidget(self.delParButton,0,2)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox,40,0)
        self.loadButton=QPushButton("Open")
        self.saveButton=QPushButton("Save")
        self.layout.addWidget(self.loadButton,0,3)
        self.layout.addWidget(self.saveButton,0,4)
        self.loadButton.clicked.connect(self.myread2)
        self.saveButton.clicked.connect(self.mysave)
        self.layout.addWidget(QLabel('Description'),1,0)
        self.layout.addWidget(QLabel('Initial'),1,1)
        self.layout.addWidget(QLabel('Final'),1,2)
        self.layout.addWidget(QLabel('Stage #'),1,3)
        self.layout.addWidget(QLabel('Device #'),1,4)
        self.layout.addWidget(QLabel('Type'),1,5)
        self.setLayout(self.layout)
        #self.myread(filename)

    def delpar(self):
        self.layout.removeWidget(self.params[-1].title)
        self.layout.removeWidget(self.params[-1].Startbox)
        self.layout.removeWidget(self.params[-1].Stopbox)
        self.layout.removeWidget(self.params[-1].time)
        self.layout.removeWidget(self.params[-1].channel)
        self.layout.removeWidget(self.params[-1].mytype)
        self.params[-1].title.deleteLater()
        self.params[-1].Startbox.deleteLater()
        self.params[-1].Stopbox.deleteLater()
        self.params[-1].time.deleteLater()
        self.params[-1].channel.deleteLater()
        self.params[-1].mytype.deleteLater()
        del self.params[-1]
        self.adjustSize()
        #self.setLayout(self.layout)

    def newpar(self):
        self.params.append(AParam(0,0))
        npars=len(self.params)
        hlines=1
        #print(npars)
        self.params[-1].title.setText("Parameter_"+str(npars))
        self.layout.addWidget(self.params[-1].title,npars+hlines,0)
        self.layout.addWidget(self.params[-1].Startbox,npars+hlines,1)
        self.layout.addWidget(self.params[-1].Stopbox,npars+hlines,2)
        self.layout.addWidget(self.params[-1].time,npars+hlines,3)
        self.layout.addWidget(self.params[-1].channel,npars+hlines,4)
        self.layout.addWidget(self.params[-1].mytype,npars+hlines,5)

    def mysave(self):
        fn=self.namebox.text()
        if os.path.exists(fn):
           print("File exists")
           os.remove(fn)
        f=open(fn,'w')
        np=len(self.params)
        for i in range(np):
          f.write("%s " % self.params[i].title.text())
          f.write("%g " % self.params[i].Startbox.value())
          f.write("%g " % self.params[i].Stopbox.value())
          f.write("%d " % self.params[i].time.value())
          f.write("%d " % self.params[i].channel.value())
          f.write("%d\n" % self.params[i].mytype.currentIndex())
        f.close()
        
    def myread2(self):
        #filename=self.namebox.text()
        name,path = QFileDialog.getOpenFileName(self, 'Open file','./',"MultiGo files (*.mgo)")
        i=name.rfind("/")
        filename=name[i+1:]
        #print(filename)
        
        self.myread(filename)
        
    def myread(self,filename):
        #filename=filename+".mgo"
        #print(filename)
        if os.path.exists(filename):
            f=open(filename,"r")
            ls=f.readlines()
            self.namebox.setText(filename)
            if len(ls)>1:
                for j in range(len(ls)):
                   self.newpar()
                   #print(j)
            npars=len(self.params)
            print('During read - Number of lines: ',len(ls),'; Number of parameters: ',len(self.params))
            for i,l in enumerate(ls):
                p=l.split(' ')
                #print(i)
                try:
                  self.params[i].title.setText(p[0])
                  self.params[i].Startbox.setValue(float(p[1]))
                  self.params[i].Stopbox.setValue(float(p[2]))
                  self.params[i].time.setValue(int(p[3]))
                  self.params[i].channel.setValue(int(p[4]))
                  self.params[i].mytype.setCurrentIndex(int(p[5]))
                except:
                  pass
            if len(ls) < npars:
                for i in range(len(ls),npars):
                    self.delpar()
            f.close()
        #print("Hello")
    def accept(self):
        self.mysave()
        self.close()
    #def reject(self):
    #    print("rejected")
    #    self.close()
    
def multigomenu(MGPanel): # Open Multigo dialog. Something odd is that it takes two clicks to close.
    filename=MGPanel.cbExpKind.currentText()+".mgo"
    dlg=MultiGoDialog(filename)
    if dlg.exec_():
      print('success')
      dlg.mysave()
      #self.addMGFiles()
      dlg.close()
    else:
      print("fail")
      dlg.close()

if __name__=='__main__':
  import sys
  app=QApplication(sys.argv)
  w=MultiGoDialog("Fmolasses.mgo")
  #w.myread("untitled.mgo")
  w.show()
  sys.exit(app.exec_())
