from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from artiq.experiment import *

class FastDAC(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("fastino0")

class FastWindow(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        layout=QGridLayout()
        self.sb1=QDoubleSpinBox()#0.00)
        layout.addWidget(self.sb1,0,0)
        self.pb1=QPushButton("Click")
        layout.addWidget(self.pb1,1,0)
        self.sb1.valueChanged.connect(self.valueaction)
        self.pb1.pressed.connect(self.pushaction)
        self.setLayout(layout)
    def pushaction(self):
        print("Button pushed")
    def valueaction(self):
        print("Value changed: ", self.sb1.value())

def main():
   app = QApplication(sys.argv)
   mw = FastWindow()
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec())

if __name__ == '__main__':
   main()
        
        

