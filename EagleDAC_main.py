from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPalette, QColor
from matplotlib import cm
import numpy as np
import sys
#from qmsbox import *
import DAQ


class Eagle_box(QDoubleSpinBox):
    def __init__(self,i,j):
        super(QDoubleSpinBox,self).__init__()
        self.DACid=i*8+j
        self.setRange(-10,10)
        self.setSingleStep(0.01)
        self.setToolTip('DAC '+str(self.DACid))
        self.valueChanged.connect(self.updateDAC)
        self.updatecolor()
        
    def updateDAC(self):
        self.updatecolor()
        try:
            self.parent().EDRE.writeChannel(0,self.DACid,int(self.value()*1000000))
        except:
            pass
          
    def updatecolor(self):
        cmap = cm.get_cmap(name='RdBu')#'Spectral')#
        #only choose a number between 0.25 and 0.75
        colrange=[0.25,0.75]
    
        value = self.value()
        if value==0:
            newcolor=3*[180]#[128,128,128]#'#AAAAAA'
        else:
            valrange=[self.minimum(),self.maximum()]
    
            cmap_val = colrange[0] + (colrange[1]-colrange[0])*(value-valrange[0])/(valrange[1] - valrange[0])
            newcolor=[int(np.ceil(255*x)) for x in cmap(cmap_val)]
    
        pal=self.palette()
        #pal.setColor(QPalette.Base, QColor(newcolor[0],newcolor[1],newcolor[2]))
        self.setPalette(pal)

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout=QGridLayout()
        self.setLayout(layout)
        mypanel=EaglePanel()
        layout.addWidget(mypanel)

class EaglePanel(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        self.setFixedHeight(100)
        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(0)
        self.setTitle('Eagle DACs')
        self.setLayout(self.layout)
        self.Eagle_boxes=[]
        self.EDRE=DAQ.EDRE_Interface()
        for i in range(3):
          for j in range(8):
            self.Eagle_boxes.append(Eagle_box(i,j))
            self.layout.addWidget(self.Eagle_boxes[-1],i,j)



if __name__=='__main__':
  app = QApplication(sys.argv)
  screen = Window()
  screen.show()
  sys.exit(app.exec_())
