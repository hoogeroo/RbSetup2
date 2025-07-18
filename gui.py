import numpy as np
import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt
from PyQt6.uic import loadUi

from main import Dc, Stage

# Used to set the maximum size of the widgets
big = 16777215

class Gui(QMainWindow):
    '''
    Main GUI class that initializes the user interface and connects it to the device.
    It creates the layout, widgets, and connects signals to the device methods.
    The gui is built using PyQt6 and the layout is defined in `gui.ui`.
    '''
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device

        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        # store reference to all the widgets to get their values later
        self.dc_widgets = []
        self.copy_widgets = []
        self.stage_widgets = []
        self.stage_containers = []

        # add spacers to the dc, label, and copied containers
        spacers = []
        for i in range(3):
            label = QLabel()
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            spacers.append(label)
        self.dc_container.addWidget(spacers[0])
        self.label_container.addWidget(spacers[1])
        self.copied_container.addWidget(spacers[2])

        # fill dc, label, and copied containers with widgets
        for i, variable in enumerate(self.device.variables):
            # add the widget to the dc container
            dc_widget = variable.widget()
            if i == 0:
                dc_widget.setEnabled(False)  # time doesn't make sense for dc
            variable.changed_signal(dc_widget).connect(self.update_dc)
            self.dc_container.addWidget(dc_widget)
            self.dc_widgets.append(dc_widget)

            # add the widget to the copied container
            copied_widget = variable.widget()
            copied_widget.setEnabled(False)
            self.copied_container.addWidget(copied_widget)
            self.copy_widgets.append(copied_widget)

            # add the label to the label container
            label = QLabel()
            label.setText(variable.label)
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            self.label_container.addWidget(label)

        # add stretch to containers
        self.dc_container.addStretch()
        self.label_container.addStretch()
        self.copied_container.addStretch()
        
        # connect the run button to the submit_experiment method
        self.run_experiment.clicked.connect(self.submit_experiment)

        # connect the actions
        self.action_save.triggered.connect(self.save_settings_dialog)
        self.action_load.triggered.connect(self.load_settings_dialog)

        # load the default values (creates the needed stage widgets)
        self.load_settings('default.json')

    '''
    methods to get the values from the widgets and update the device.
    '''

    # extracts the values from the dc widgets and creates a Dc object
    def extract_dc(self) -> Dc:
        # uses setattr to dynamically create a Dc object with the values from the widgets
        dc = Dc()
        for i, variable in enumerate(self.device.variables):
            setattr(dc, variable.id, variable.value(self.dc_widgets[i]))
        return dc

    # extracts the values from the stage widgets and creates a list of Stage objects
    def extract_stages(self) -> list[Stage]:
        # creates a list of Stage objects with the values from the widgets
        stages = []
        for i in range(len(self.stage_containers)):
            stage = Stage()
            for j, variable in enumerate(self.device.variables):
                value = variable.value(self.stage_widgets[i][j])
                setattr(stage, variable.id, value)
            stages.append(stage)
        return stages

    # updates the device with the values from the widgets
    def update_dc(self):
        self.device.update_dc(self.extract_dc())

    # runs the experiment and using the data from the widgets
    def submit_experiment(self):
        self.device.run_experiment(self.extract_stages())

    '''
    methods for renaming, copying and creating stages
    '''

    def get_stage_index(self, stage_container) -> int:
        for i, container in enumerate(self.stage_containers):
            if container is stage_container:
                return i
        return -1

    # copies the right clicked stage values to the copied widgets
    def copy_stage(self, stage_container):
        stage_index = self.get_stage_index(stage_container)
        if stage_index == -1:
            print("Error: Stage container not found")
            return

        for i, variable in enumerate(self.device.variables):
            value = variable.value(self.stage_widgets[stage_index][i])
            variable.set_value(self.copy_widgets[i], value)

    # pastes the copied values to the right clicked stage
    def paste_stage(self, stage_container):
        stage_index = self.get_stage_index(stage_container)
        if stage_index == -1:
            print("Error: Stage container not found")
            return

        for i, variable in enumerate(self.device.variables):
            value = variable.value(self.copy_widgets[i])
            variable.set_value(self.stage_widgets[stage_index][i], value)

    # adds a new stage to the gui
    def insert_stage(self, idx: int):
        stage_container = QVBoxLayout()
        self.stages_container.insertLayout(idx, stage_container)
        self.stage_containers.insert(idx, stage_container)
        self.stage_widgets.insert(idx, [])

        # create a button at the top of the stage column
        button = QPushButton()
        button.setText(f"Stage {idx + 1}")
        button.setMinimumSize(QSize(0, 24))
        button.setMaximumSize(QSize(big, 24))
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        button.addAction("Copy", lambda: self.copy_stage(stage_container))
        button.addAction("Paste", lambda: self.paste_stage(stage_container))
        button.addAction("Insert Stage Left", lambda: self.insert_stage_left(stage_container))
        button.addAction("Insert Stage Right", lambda: self.insert_stage_right(stage_container))
        stage_container.addWidget(button)

        # create widgets for each variable and add them to the layout
        for variable in self.device.variables:
            widget = variable.widget()
            stage_container.addWidget(widget)
            self.stage_widgets[idx].append(widget)
        
        # add a spacer to the stage container
        stage_container.addStretch()

    # creates a new stage to the left
    def insert_stage_left(self, stage_container):
        stage_index = self.get_stage_index(stage_container)
        if stage_index == -1:
            print("Error: Stage container not found")
            return

        self.insert_stage(stage_index)
        self.paste_stage(self.stage_containers[stage_index])
    
    # creates a new stage to the right
    def insert_stage_right(self, stage_container):
        stage_index = self.get_stage_index(stage_container)
        if stage_index == -1:
            print("Error: Stage container not found")
            return

        self.insert_stage(stage_index + 1)
        self.paste_stage(self.stage_containers[stage_index + 1])

    '''
    methods to save and load settings from a file
    '''

    # open a file dialog for the user to choose a file
    def save_settings_dialog(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON File (*.json)")

        if file_name:
            self.save_settings(file_name)

    # open a file dialog for the user to choose a file
    def load_settings_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON File (*.json)")

        if file_name:
            self.load_settings(file_name)

    # save the settings to the file
    def save_settings(self, path):
        data = {
            'dc': self.extract_dc(),
            'stages': self.extract_stages()
        }
        data_json = json.dumps(data, default=lambda o: o.__dict__)

        with open(path, 'w') as f:
            f.write(data_json)

    # load the settings from the file
    def load_settings(self, path):
        with open(path, 'r') as f:
            data = json.load(f)

        # update the dc widgets with the values from the file
        for i, variable in enumerate(self.device.variables):
            if variable.id in data['dc']:
                variable.set_value(self.dc_widgets[i], data['dc'][variable.id])
            else:
                print(f"Warning: Unknown variable '{variable.id}' in dc data")

        # clear the current stage widgets
        for stage_container in self.stage_containers:
            for widget in stage_container:
                widget.deleteLater()
        self.stage_widgets.clear()
        self.stage_containers.clear()

        # create new stage widgets based on the loaded data
        for i, stage in enumerate(data['stages']):
            # create new column of widgets for the stage
            self.insert_stage(i)

            # fill the stage widgets with the values from the file
            for j, variable in enumerate(self.device.variables):
                if variable.id in stage:
                    variable.set_value(self.stage_widgets[i][j], stage[variable.id])
                else:
                    print(f"Warning: Unknown variable '{variable.id}' in stage {i} data")


'''
abstractions over the different variable types and corresponding
widget types used in the gui
'''

class VariableTypeBool:
    def __init__(self, label, id):
        self.label = label
        self.id = id

    def widget(self) -> QCheckBox:
        checkbox = QCheckBox()
        checkbox.setMinimumSize(QSize(0, 24))
        checkbox.setMaximumSize(QSize(big, 24))
        return checkbox

    def changed_signal(self, widget: QCheckBox):
        return widget.stateChanged

    def value(self, widget: QCheckBox) -> bool:
        return widget.isChecked()

    def set_value(self, widget: QCheckBox, value: bool):
        widget.setChecked(value)

class VariableTypeInt:
    def __init__(self, label, id, minimum=0, maximum=100, step=1):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def widget(self) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setMinimumSize(QSize(0, 24))
        spinbox.setMaximumSize(QSize(big, 24))
        spinbox.setMinimum(self.minimum)
        spinbox.setMaximum(self.maximum)
        spinbox.setSingleStep(self.step)
        return spinbox
    
    def changed_signal(self, widget: QSpinBox):
        return widget.valueChanged

    def value(self, widget: QSpinBox) -> int:
        return widget.value()

    def set_value(self, widget: QSpinBox, value: int):
        widget.setValue(value)

class VariableTypeFloat:
    def __init__(self, label, id, minimum=0.0, maximum=1.0, step=0.1):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def widget(self) -> QDoubleSpinBox:
        spinbox = QDoubleSpinBox()
        spinbox.setMinimumSize(QSize(0, 24))
        spinbox.setMaximumSize(QSize(big, 24))
        spinbox.setMinimum(self.minimum)
        spinbox.setMaximum(self.maximum)
        spinbox.setSingleStep(self.step)
        return spinbox
    
    def changed_signal(self, widget: QDoubleSpinBox):
        return widget.valueChanged

    def value(self, widget: QDoubleSpinBox) -> float:
        return float(widget.value())
    
    def set_value(self, widget: QDoubleSpinBox, value: float):
        widget.setValue(value)

