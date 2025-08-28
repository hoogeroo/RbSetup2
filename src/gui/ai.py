from PyQt6.QtWidgets import *

from src.device.ai import AiSettings
from src.gui.multigo import RunVariableWidget

class AiDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("AI Settings")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add run variable selection widget
        self.run_variable_widget = RunVariableWidget(stages, steps=False)
        layout.addWidget(self.run_variable_widget)
        layout.addStretch()

        # add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.save_run_variables)
        layout.addWidget(self.button_box)

        # add the current settings
        ai_settings = stages.ai_settings
        for run_variable in ai_settings.run_variables:
            self.run_variable_widget.add_run_variable(run_variable)

    # saves the settings currently in the gui into the `StagesGui`'s ai_settings
    def save_run_variables(self):
        # get the currently selected run variables
        run_variables = self.run_variable_widget.get_run_variables()

        # update the AI settings with the new run variables
        self.stages.ai_settings = AiSettings(run_variables)

        # close the dialog
        self.accept()
