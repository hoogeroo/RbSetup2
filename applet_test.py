from artiq.applets.simple import SimpleApplet

from PySide6.QtWidgets import *
from PySide6.QtCore import Slot

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

applet = SimpleApplet(Window())
applet.run()