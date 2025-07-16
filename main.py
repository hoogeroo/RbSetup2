from artiq.experiment import *

from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi

class Gui(QDialog):
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device
        
        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        self.submit.clicked.connect(self.submit_function)

    def submit_function(self):
        self.textdisplay.setText(f"Input 1: {self.input1.text()}\nInput 2: {self.input2.text()}")

    def pulse(self):
        self.device.pulse()

class Device(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")

    def run(self):
        app = QApplication([])
        gui = Gui(self)
        gui.show()
        app.exec()

        self.pulse()
        

    @kernel
    def pulse(self):
        print("Switched context")

        self.core.reset()

        self.ttl5.pulse(0.5*s)
        # self.core.wait_until_mu(now_mu())

        print("Queued pulse!")
