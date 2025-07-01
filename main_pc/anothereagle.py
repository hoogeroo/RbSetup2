from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
#from qmsbox import *
import DAQ


class Eagle_box(QDoubleSpinBox):
    def __init__(self,i,j):
        super(QDoubleSpinBox,self).__init__()
        self.DACid=i*8+j
        self.setRange(-1000,1000)
        self.setSingleStep(0.01)
        self.setToolTip('DAC '+str(self.DACid))
        self.valueChanged.connect(self.updateDAC)
    def updateDAC(self):
        self.parent().EDRE.writeChannel(0,self.DACid,int(self.value()*1000))


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
        layout = QGridLayout()
        self.setTitle('Eagle DACs')
        self.setLayout(layout)
        self.Eagle_boxes=[]
        self.EDRE=DAQ.EDRE_Interface()
        for i in range(3):
          for j in range(8):
            self.Eagle_boxes.append(Eagle_box(i,j))
            layout.addWidget(self.Eagle_boxes[-1],i,j)
            
        
        
if __name__=='__main__':                
  app = QApplication(sys.argv)
  screen = Window()
  screen.show()
  sys.exit(app.exec_())