from PyQt6.QtWidgets import *

class MultiGo(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiGo")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()

        message = QLabel("Something happened, is that OK?")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

