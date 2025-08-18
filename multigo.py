from PyQt6.QtWidgets import *

class MultiGo(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("MultiGo")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        self.grid = QGridLayout()

        # stage selection
        stage_dropdown = QComboBox()
        for stage in self.stages.stages:
            stage_dropdown.addItem(stage.label())
        self.grid.addWidget(stage_dropdown, 0, 0)

        # variable selection
        variable_dropdown = QComboBox()
        for variable in self.stages.variables:
            variable_dropdown.addItem(variable.label)
        self.grid.addWidget(variable_dropdown, 0, 1)

        # add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 0, 2)

        layout.addLayout(self.grid)
        layout.addWidget(self.buttonBox)        
        self.setLayout(layout)

    def add_variable(self, idx, variable):
        stage_name = self.stages.stages[idx].label()
        variable_name = self.stages.variables[variable].label

        row = self.grid.rowCount()
        self.grid.addWidget(QLabel(stage_name), row, 0)
        self.grid.addWidget(QLabel(variable_name), row, 1)
