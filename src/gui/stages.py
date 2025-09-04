'''
stages.py: this file has the code for managing the stages in the experiment along with the experiment control buttons and checkboxes
'''

from uuid import uuid4

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import *

from src.device.ai import AiSettings
from src.device.device_types import DeviceSettings, MultiGoSubmission, Stage, Stages
from src.device.multigo import MultiGoSettings
from src.gui.ai import AiDialog
from src.gui.multigo import MultiGoDialog, MultiGoProgressDialog
from src.gui.value_widgets import big
from src.variable_types import *

# class to represent a stage in the gui. differs from Stage in that it can't be sent to the device
class GuiStage:
    def __init__(self, button, container, widgets, enabled=True, id=None):
        self.id = id if id is not None else uuid4()
        self.button = button
        self.container = container
        self.widgets = widgets
        self.enabled = enabled

    def label(self):
        return self.button.text()

class StagesGui:
    def __init__(self, window, variables):
        self.window = window
        self.variables = variables
        self.multigo_settings = MultiGoSettings([], 0.0)
        self.ai_settings = AiSettings([])

        # store reference to all the widgets to get their values later
        self.dc_widgets = []
        self.copy_widgets = []
        self.stages = []

        # add spacers to the dc, label, and copied containers
        spacers = []
        for _ in range(3):
            label = QLabel()
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            spacers.append(label)
        self.window.dc_container.addWidget(spacers[0])
        self.window.label_container.addWidget(spacers[1])
        self.window.copied_container.addWidget(spacers[2])

        # fill dc, label, and copied containers with widgets
        for i, variable in enumerate(self.variables):
            # add the widget to the dc container
            dc_widget = variable.widget()
            if variable.id == "time" or variable.id == "samples":
                dc_widget.setEnabled(False)  # time and samples don't make sense for dc
            dc_widget.changed_signal().connect(self.update_dc)
            self.window.dc_container.addWidget(dc_widget)
            self.dc_widgets.append(dc_widget)

            # add the widget to the copied container
            copied_widget = variable.widget()
            copied_widget.setEnabled(False)
            self.window.copied_container.addWidget(copied_widget)
            self.copy_widgets.append(copied_widget)

            # add the label to the label container
            label = QLabel()
            label.setText(variable.label)
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            self.window.label_container.addWidget(label)

        # add stretch to containers
        self.window.dc_container.addStretch()
        self.window.label_container.addStretch()
        self.window.copied_container.addStretch()

        # connect the ai buttons
        self.window.ai_options.clicked.connect(self.ai_dialog)
        # self.window.ai.clicked.connect(self.submit_ai)

        # connect the multigo buttons
        self.window.multigo_options.clicked.connect(self.multigo_dialog)
        self.window.multigo.clicked.connect(self.submit_multigo)

        # connect the run button to the submit_experiment method
        self.window.run_experiment.clicked.connect(self.submit_experiment)

        # connect the load mot and save runs checkbox to the update_device_settings method
        self.window.load_mot.stateChanged.connect(self.update_device_settings)
        self.window.save_runs.stateChanged.connect(self.update_device_settings)

    # gets a stage using the stage id
    def get_stage(self, stage_id):
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        raise ValueError(f"Stage with id {stage_id} not found")

    # gets a variable using the variable id
    def get_variable(self, variable_id):
        for i, variable in enumerate(self.variables):
            if variable.id == variable_id:
                return i, variable
        raise ValueError(f"Variable with id {variable_id} not found")

    '''
    methods to get the values from the widgets and update the device.
    '''

    # extracts the values from the dc widgets and creates a Dc object
    def extract_dc(self) -> Stage:
        # uses setattr to dynamically create a Dc object with the values from the widgets
        dc = Stage("DC Values", "dc", True)
        for i, variable in enumerate(self.variables):
            setattr(dc, variable.id, self.dc_widgets[i].get_value())
        return dc

    # extracts the values from the stage widgets and creates a Stages object to send to the device
    def extract_stages(self) -> Stages:
        stages = []
        for gui_stage in self.stages:
            name = gui_stage.button.text()
            stage = Stage(name, gui_stage.id, gui_stage.enabled)
            for i, variable in enumerate(self.variables):
                setattr(stage, variable.id, gui_stage.widgets[i].get_value())
            stages.append(stage)
        dc = self.extract_dc()
        return Stages(dc, stages)

    # updates the device with the values from the widgets
    def update_dc(self):
        # ignore widget updates if the UI is not loaded yet
        if not self.window.ui_loaded:
            return

        # send the extracted dc values to the device
        self.window.gui_pipe.send(self.extract_dc())

    # runs the experiment and using the data from the widgets
    def submit_experiment(self):
        # run the actual experiment
        self.window.gui_pipe.send(self.extract_stages())

    # open the multigo options popup
    def multigo_dialog(self):
        multigo = MultiGoDialog(self)
        multigo.exec()
    
    # sends the multigo event down the pipe with the gui state
    def submit_multigo(self):
        self.window.gui_pipe.send(MultiGoSubmission(self.multigo_settings, self.extract_stages()))

        self.window.multigo_progress = MultiGoProgressDialog(self.window)
        self.window.multigo_progress.exec()

    # open the ai options popup
    def ai_dialog(self):
        ai = AiDialog(self)
        ai.exec()

    # send the current device settings to the device
    def update_device_settings(self):
        # create a DeviceSettings object with the current values
        load_mot = self.window.load_mot.isChecked()
        save_runs = self.window.save_runs.isChecked()
        device_settings = DeviceSettings(load_mot, save_runs)

        # send the device settings to the device
        self.window.gui_pipe.send(device_settings)

    '''
    methods for renaming, copying, creating and deleting stages
    '''

    # we need to use the object reference since the index changes when we insert or delete stages
    def get_stage_index(self, button) -> int:
        for i, stage in enumerate(self.stages):
            if stage.button is button:
                return i
        raise ValueError("Stage button not found")

    # adds a new stage to the gui
    def insert_stage(self, idx: int, name=None, enabled=True, id=None):
        stage_container = QVBoxLayout()
        self.window.stages_container.insertLayout(idx, stage_container)

        # create a button at the top of the stage column
        button = QPushButton()
        button.setText(name if name else f"Stage {idx + 1}")
        button.setMinimumSize(QSize(0, 24))
        button.setMaximumSize(QSize(big, 24))
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        button.clicked.connect(lambda: self.disable_stage(self.get_stage_index(button)))
        button.addAction("Rename", lambda: self.rename_stage(self.get_stage_index(button)))
        button.addAction("Copy", lambda: self.copy_stage(self.get_stage_index(button)))
        button.addAction("Paste", lambda: self.paste_stage(self.get_stage_index(button)))
        button.addAction("Insert Stage Left", lambda: self.insert_stage_left(self.get_stage_index(button)))
        button.addAction("Insert Stage Right", lambda: self.insert_stage_right(self.get_stage_index(button)))
        button.addAction("Delete", lambda: self.delete_stage(self.get_stage_index(button)))
        stage_container.addWidget(button)

        # create widgets for each variable and add them to the layout
        widgets = []
        for variable in self.variables:
            widget = variable.widget()
            stage_container.addWidget(widget)
            widgets.append(widget)

        # add a spacer to the stage container
        stage_container.addStretch()

        self.stages.insert(idx, GuiStage(button, stage_container, widgets, enabled, id))
        if not enabled:
            for widget in widgets:
                widget.setEnabled(False)

    # disable stage
    def disable_stage(self, idx: int):
        # check if the stage is enabled
        enabled = self.stages[idx].enabled
        self.stages[idx].enabled = not enabled

        # disable the stage
        for widget in self.stages[idx].widgets:
            widget.setEnabled(not enabled)

    # renames the stage in the gui
    def rename_stage(self, idx: int):
        # get the current button text
        button = self.stages[idx].button
        current_text = button.text()

        # create a dialog to get the new name
        new_name, ok = QInputDialog.getText(self, "Rename Stage", "Enter new stage name:", text=current_text)

        if ok and new_name:
            # set the new name to the button
            button.setText(new_name)

    # copies the right clicked stage's values to the copied widgets
    def copy_stage(self, idx: int):
        for i, variable in enumerate(self.variables):
            value = self.stages[idx].widgets[i].get_value()
            self.copy_widgets[i].set_value(value)

    # pastes the copied values to the right clicked stage
    def paste_stage(self, idx: int):
        for i, variable in enumerate(self.variables):
            value = self.copy_widgets[i].get_value()
            self.stages[idx].widgets[i].set_value(value)

    # creates a new stage to the left
    def insert_stage_left(self, idx: int):
        self.insert_stage(idx)
        self.paste_stage(idx)

    # creates a new stage to the right
    def insert_stage_right(self, idx: int):
        self.insert_stage(idx + 1)
        self.paste_stage(idx + 1)

    # deletes the stage at the right clicked container
    def delete_stage(self, idx: int):
        stage = self.stages.pop(idx)
        
        # remove the button and widgets from the layout
        for j in reversed(range(stage.container.count())):
            widget = stage.container.itemAt(j).widget()
            if widget is not None:
                widget.deleteLater()
