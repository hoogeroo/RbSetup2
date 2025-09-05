'''
multigo.py: this file contains the gui dialogs for running multigo experiments
'''

from PyQt6.QtWidgets import *

from src.device.multigo import MultiGoCancel, MultiGoProgress, MultiGoSettings
from src.gui.run_variables import RunVariableWidget

# dialog for chaning multigo settings
class MultiGoDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("MultiGo")
        self.setModal(True)

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
        self.button_box.accepted.connect(self.save_multigo_settings)
        layout.addWidget(self.button_box)

        # load the current settings
        multigo_settings = stages.multigo_settings
        self.fluorescence_threshold.setValue(multigo_settings.fluorescence_threshold)
        for run_variable in multigo_settings.run_variables:
            self.run_variable_widget.add_run_variable(run_variable)

    # saves the settings currently in the gui into the `StagesGui`'s multigo_settings
    def save_multigo_settings(self):
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

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add the progress label
        self.progress_label = QLabel("Submitting to device...")
        layout.addWidget(self.progress_label)

        # add the progress bar
        self.progress_bar = QProgressBar()
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
