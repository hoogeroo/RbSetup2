from artiq.experiment import *

from PyQt6.QtWidgets import *

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyuic6 form.ui -o ui_form.py
# from ui_form import Ui_Widget

class Gui(QDialog):
    def __init__(self, device):
        self.device = device

        super(Gui, self).__init__()
        self.setWindowTitle("My Form")

        self.label = QLabel("Hello World!")
        self.button = QPushButton("Click me")
        self.button.clicked.connect(self.pulse)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

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
