# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import Slot

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = Window()
    window.show()

    app.exec()

