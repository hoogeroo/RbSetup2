'''
run_variables.py: widget for adding and removing run variables, used by multigo and ai
'''

from PyQt6.QtWidgets import *

# stores a run variable
class RunVariable:
    def __init__(self, stage_id, variable_id, start, end, steps):
        self.stage_id = stage_id
        self.variable_id = variable_id
        self.start = start
        self.end = end
        self.steps = steps

# custom widget for adding run_variables
class RunVariableWidget(QWidget):
    def __init__(self, stages, steps=True):
        super().__init__()

        self.stages = stages
        self.run_variables = []
        self.steps = steps
        self.button_column = 5 - int(not steps)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # add save/load buttons
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_dialog)
        self.grid.addWidget(save_button, 0, 0)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_dialog)
        self.grid.addWidget(load_button, 0, 1)

        # stage selection
        stage_dropdown = QComboBox()
        for stage in self.stages.stages:
            stage_dropdown.addItem(stage.label())
        self.grid.addWidget(stage_dropdown, 1, 0)

        # variable selection
        variable_dropdown = QComboBox()
        for variable in self.stages.variables:
            variable_dropdown.addItem(variable.label)
        self.grid.addWidget(variable_dropdown, 1, 1)

        # labels
        self.grid.addWidget(QLabel("Start"), 1, 2)
        self.grid.addWidget(QLabel("End"), 1, 3)
        if steps:
            self.grid.addWidget(QLabel("Steps"), 1, 4)

        # add add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.new_run_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 1, self.button_column)

    # gets the currently selected run variables
    def get_run_variables(self):
        run_variables = []

        # add all the run variables that havent been deleted
        for i, run_variable in enumerate(self.run_variables):
            item = self.grid.itemAtPosition(i + 2, self.button_column)
            if item:
                # update run_variable to the current values in the widgets
                start = self.grid.itemAtPosition(i + 2, 2).widget().get_value()
                end = self.grid.itemAtPosition(i + 2, 3).widget().get_value()
                run_variable.start = start
                run_variable.end = end

                # only set steps if the widget exists
                if self.steps:
                    steps = self.grid.itemAtPosition(i + 2, 4).widget().value()
                    run_variable.steps = steps

                # add the run_variable to the global list
                run_variables.append(run_variable)

        return run_variables

    # create a new run variable
    def new_run_variable(self, idx, variable):
        current_value = self.stages.stages[idx].widgets[variable].get_value()
        run_variable = RunVariable(
            self.stages.stages[idx].id,
            self.stages.variables[variable].id,
            current_value,
            current_value,
            0
        )
        self.add_run_variable(run_variable)

    # add a run variable to the dialog
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
        if self.steps:
            steps = QSpinBox()
            steps.setMinimum(1)
            steps.setValue(run_variable.steps)
            self.grid.addWidget(steps, row, 4)

        # add remove button
        remove_button = QPushButton(f"Remove {row - 1}")
        remove_button.clicked.connect(self.remove_run_variable)
        self.grid.addWidget(remove_button, row, self.button_column)

        # add to run variables
        self.run_variables.append(run_variable)

    # remove a run variable from the dialog
    def remove_run_variable(self):
        button = self.sender()
        rows = self.grid.rowCount()
        for i in range(rows):
            # find row that contains the button
            item = self.grid.itemAtPosition(i, self.button_column)
            if item and item.widget() == button:
                # delete all the widgets in that row
                columns = self.grid.columnCount()
                for j in range(columns):
                    widget = self.grid.itemAtPosition(i, j)
                    if widget:
                        widget.widget().deleteLater()
                break
    
    # opens a dialog for saving run variables
    def save_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Run Variables", "", "FITS File (*.fits)")
        if file_path:
            from src.gui.fits import save_run_variables
            try:
                save_run_variables(file_path, self.get_run_variables())
            except Exception as e:
                print(f"Error saving run variables: {e}")

    # opens a dialog for loading run variables
    def load_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Run Variables", "", "FITS File (*.fits)")
        if file_path:
            from src.gui.fits import load_run_variables
            try:
                run_variables = load_run_variables(file_path)
            except Exception as e:
                print(f"Error loading run variables: {e}")
                return

            # clear all the existing run variables
            for i in range(len(self.run_variables)):
                item = self.grid.itemAtPosition(i + 2, self.button_column)
                if item:
                    item.widget().click()

            # add the new run variables
            for run_variable in run_variables:
                self.add_run_variable(run_variable)
