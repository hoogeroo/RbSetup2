from artiq.experiment import *

from PyQt6.QtWidgets import *

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyuic6 form.ui -o ui_form.py
# from ui_form import Ui_Widget

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("My Form")

        self.label = QLabel("Hello World!")
        self.button = QPushButton("Click me")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

class LED(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")

    def gui(self):
        app = QApplication([])
        window = Window()
        window.show()
        app.exec()

        print("gui initalized")

    @kernel
    def run(self):
        self.gui()

        self.core.reset()
        self.ttl5.output()
        while True:
          delay(2*ms)
          self.ttl5.pulse(2*ms)

