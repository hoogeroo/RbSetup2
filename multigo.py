from PyQt6.QtWidgets import *

BUTTON_COLUMN = 5

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

        # labels
        self.grid.addWidget(QLabel("Start"), 0, 2)
        self.grid.addWidget(QLabel("End"), 0, 3)
        self.grid.addWidget(QLabel("Steps"), 0, 4)

        # add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_run_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 0, BUTTON_COLUMN)

        layout.addLayout(self.grid)
        layout.addStretch()
        layout.addWidget(self.buttonBox)        
        self.setLayout(layout)

    def add_run_variable(self, idx, variable):
        stage_name = self.stages.stages[idx].label()
        variable_name = self.stages.variables[variable].label

        # add labels
        row = self.grid.rowCount()
        self.grid.addWidget(QLabel(stage_name), row, 0)
        self.grid.addWidget(QLabel(variable_name), row, 1)

        # add start and end
        current_value = self.stages.stages[idx].widgets[variable]
        start = current_value.variable.widget()
        start.set_value(current_value.get_value())
        end = current_value.variable.widget()
        end.set_value(current_value.get_value())
        self.grid.addWidget(start, row, 2)
        self.grid.addWidget(end, row, 3)

        # add steps
        steps = QSpinBox()
        steps.setMinimum(1)
        steps.setValue(1)
        self.grid.addWidget(steps, row, 4)

        # add remove button
        remove_button = QPushButton(f"Remove {row}")
        remove_button.clicked.connect(self.remove_run_variable)
        self.grid.addWidget(remove_button, row, BUTTON_COLUMN)

    def remove_run_variable(self):
        button = self.sender()
        rows = self.grid.rowCount()
        for i in range(rows):
            widget = self.grid.itemAtPosition(i, BUTTON_COLUMN)
            if widget and widget.widget() == button:
                print(f"Removing row {i}")
                columns = self.grid.columnCount()
                for j in range(columns):
                    widget = self.grid.itemAtPosition(i, j)
                    if widget:
                        widget.widget().deleteLater()
                break
