'''
ai.py: this file contains the gui dialogs for running ai models
'''

from PyQt6.QtWidgets import *

from src.device.ai import AiProgress, AiSettings, CancelAi
from src.gui.run_variables import RunVariableWidget

# dialog for changing AI settings
class AiDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("AI Settings")
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add settings
        form_layout = QFormLayout()
        self.pre_training_steps = QSpinBox()
        self.training_steps = QSpinBox()
        form_layout.addRow("Pre-Training Steps:", self.pre_training_steps)
        form_layout.addRow("Training Steps:", self.training_steps)
        layout.addLayout(form_layout)

        # add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.save_ai_settings)
        layout.addWidget(self.button_box)

        # load the current settings
        ai_settings = self.stages.ai_settings
        self.pre_training_steps.setValue(ai_settings.pre_training_steps)
        self.training_steps.setValue(ai_settings.training_steps)

    # saves the settings currently in the gui into the `StagesGui`'s ai_settings
    def save_ai_settings(self):
        pre_training_steps = self.pre_training_steps.value()
        training_steps = self.training_steps.value()

        # update the AI settings with the new run variables
        self.stages.ai_settings = AiSettings(pre_training_steps, training_steps)

        # close the dialog
        self.accept()

class AiProgressDialog(QDialog):
    def __init__(self, window):
        super().__init__()

        self.window = window

        self.setWindowTitle("AI Progress")
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add a label to show the progress
        self.progress_label = QLabel("Submitting to device...")
        layout.addWidget(self.progress_label)

        # add a progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # add a button to cancel the operation
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.rejected.connect(self.cancel_ai)
        layout.addWidget(self.button_box)

    def cancel_ai(self):
        self.window.gui_pipe.send(CancelAi())

    def update_progress(self, received: AiProgress):
        self.progress_label.setText(f"Running step {received.current_step} of {received.total_steps}")
        self.progress_bar.setValue(int(received.current_step / received.total_steps * 100))

        if received.current_step == received.total_steps:
            self.accept()
