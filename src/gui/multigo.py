'''
multigo.py: this file contains the gui dialogs for running multigo experiments
'''

from PyQt6.QtWidgets import *

from src.device.device_types import Stages
from src.device.multigo import MultiGoCancel, MultiGoProgress, MultiGoRunVariable, MultiGoSettings
from src.gui.plots import FluorescenceSample

# dialog for chaning multigo settings
class MultiGoDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("MultiGo")

        # set the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # add run variable selection widget
        self.run_variable_widget = RunVariableWidget(stages)
        layout.addWidget(self.run_variable_widget)
        layout.addStretch()

        # add fluorescence threshold
        form_layout = QFormLayout()
        self.fluorescence_threshold = QDoubleSpinBox()
        form_layout.addRow(QLabel("Fluorescence Threshold"), self.fluorescence_threshold)
        layout.addLayout(form_layout)

        # add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.save_run_variables)
        layout.addWidget(self.button_box)

        # add the current settings
        multigo_settings = stages.multigo_settings
        self.fluorescence_threshold.setValue(multigo_settings.fluorescence_threshold)
        for run_variable in multigo_settings.run_variables:
            self.run_variable_widget.add_run_variable(run_variable)

    # saves the settings currently in the gui into the `StagesGui`'s multigo_settings
    def save_run_variables(self):
        # get the currently selected run variables
        run_variables = self.run_variable_widget.get_run_variables()

        # get the fluorescence threshold
        fluorescence_threshold = self.fluorescence_threshold.value()

        # store the new settings
        self.stages.multigo_settings = MultiGoSettings(run_variables, fluorescence_threshold)

        # closes the dialog
        self.accept()

# for showing progress of a multigo submission
class MultiGoProgressDialog(QDialog):
    def __init__(self, window):
        super().__init__()

        self.window = window

        self.setWindowTitle("MultiGo Progress")
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # add the progress label
        self.progress_label = QLabel("Submitting to device...", self)
        layout.addWidget(self.progress_label)

        # add the progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # add the cancel button
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.rejected.connect(self.cancel_multigo)
        layout.addWidget(self.button_box)

    def cancel_multigo(self):
        self.window.gui_pipe.send(MultiGoCancel())

    def update_progress(self, received: MultiGoProgress):
        self.progress_label.setText(f"Running step {received.current_step} of {received.total_steps}")
        self.progress_bar.setValue(int(received.current_step / received.total_steps * 100))

        if received.current_step == received.total_steps:
            self.accept()

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
        if steps:
            self.grid.addWidget(QLabel("Steps"), 0, 4)

        # add add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.new_run_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 0, self.button_column)

    # gets the currently selected run variables
    def get_run_variables(self):
        run_variables = []

        # add all the run variables that havent been deleted
        for i, run_variable in enumerate(self.run_variables):
            item = self.grid.itemAtPosition(i + 1, self.button_column)
            if item:
                # update run_variable to the current values in the widgets
                start = self.grid.itemAtPosition(i + 1, 2).widget().get_value()
                end = self.grid.itemAtPosition(i + 1, 3).widget().get_value()
                run_variable.start = start
                run_variable.end = end

                # only set steps if the widget exists
                if self.steps:
                    steps = self.grid.itemAtPosition(i + 1, 4).widget().value()
                    run_variable.steps = steps

                # add the run_variable to the global list
                run_variables.append(run_variable)

        return run_variables

    # create a new run variable
    def new_run_variable(self, idx, variable):
        current_value = self.stages.stages[idx].widgets[variable].get_value()
        run_variable = MultiGoRunVariable(
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
        remove_button = QPushButton(f"Remove {row}")
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
