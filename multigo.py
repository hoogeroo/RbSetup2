from PyQt6.QtWidgets import *

BUTTON_COLUMN = 5

class MultiGoRunVariable:
    def __init__(self, stage_id, variable_id, start, end, steps):
        self.stage_id = stage_id
        self.variable_id = variable_id
        self.start = start
        self.end = end
        self.steps = steps

class MultiGoDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages
        self.run_variables = []

        self.setWindowTitle("MultiGo")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.save_run_variables)

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
        add_button.clicked.connect(lambda: self.new_run_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 0, BUTTON_COLUMN)

        layout.addLayout(self.grid)
        layout.addStretch()
        layout.addWidget(self.buttonBox)        
        self.setLayout(layout)

        # add all existing run variables
        for run_variable in self.stages.run_variables:
            self.add_run_variable(run_variable)
    
    def save_run_variables(self):
        self.stages.run_variables = []

        # add all the run variables that havent been deleted
        for i, run_variable in enumerate(self.run_variables):
            item = self.grid.itemAtPosition(i + 1, BUTTON_COLUMN)
            if item:
                # update run_variable to the current values in the widgets
                start = self.grid.itemAtPosition(i + 1, 2).widget().get_value()
                end = self.grid.itemAtPosition(i + 1, 3).widget().get_value()
                steps = self.grid.itemAtPosition(i + 1, 4).widget().value()
                run_variable.start = start
                run_variable.end = end
                run_variable.steps = steps

                # add the run_variable to the global list
                self.stages.run_variables.append(run_variable)

        # accept the dialog
        self.accept()

    def new_run_variable(self, idx, variable):
        current_value = self.stages.stages[idx].widgets[variable].get_value()
        run_variable = MultiGoRunVariable(
            self.stages.stages[idx].id,
            self.stages.variables[variable].id,
            current_value,
            current_value,
            1
        )
        self.add_run_variable(run_variable)

    def add_run_variable(self, run_variable):
        stage = self.stages.get_stage(run_variable.stage_id)
        variable_idx, variable = self.stages.get_variable(run_variable.variable_id)

        # add labels
        row = self.grid.rowCount()
        self.grid.addWidget(QLabel(stage.label()), row, 0)
        self.grid.addWidget(QLabel(variable.label), row, 1)

        # add start and end
        start_widget = variable.widget()
        start_widget.set_value(run_variable.start)
        end_widget = variable.widget()
        end_widget.set_value(run_variable.end)
        self.grid.addWidget(start_widget, row, 2)
        self.grid.addWidget(end_widget, row, 3)

        # add steps
        steps = QSpinBox()
        steps.setMinimum(1)
        steps.setValue(run_variable.steps)
        self.grid.addWidget(steps, row, 4)

        # add remove button
        remove_button = QPushButton(f"Remove {row}")
        remove_button.clicked.connect(self.remove_run_variable)
        self.grid.addWidget(remove_button, row, BUTTON_COLUMN)

        # add to run variables
        self.run_variables.append(run_variable)

    def remove_run_variable(self):
        button = self.sender()
        rows = self.grid.rowCount()
        for i in range(rows):
            # find row that contains the button
            item = self.grid.itemAtPosition(i, BUTTON_COLUMN)
            if item and item.widget() == button:
                # delete all the widgets in that row
                columns = self.grid.columnCount()
                for j in range(columns):
                    widget = self.grid.itemAtPosition(i, j)
                    if widget:
                        widget.widget().deleteLater()
                break
