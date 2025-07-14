from artiq.experiment import *

import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Slot

import matplotlib.pyplot as plt

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyuic6 form.ui -o ui_form.py
from ui_form import Ui_Widget

@Slot()
def say_hello():
    print("Button clicked, Hello!")

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

        self.button.clicked.connect(say_hello)

class LED(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl5")

    @kernel
    def run(self):
        self.core.reset()
        # app = QApplication(sys.argv)
        # main_window = QMainWindow()
        # main_window.show()
        # sys.exit(app.exec_())

        plt.plot([(0, 0), (1, 1)])
        plt.show()

        app = QApplication(sys.argv)
    
        window = Window()
        window.show()

        app.exec()

        self.core.break_realtime()

        self.ttl5.output()
        while True:
          delay(2*ms)
          self.ttl5.pulse(2*ms)

