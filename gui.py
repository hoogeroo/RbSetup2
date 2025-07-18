import numpy as np
import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize
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
        self.state_widgets = [[] for _ in range(self.device.stages)]
        self.copy_widgets = []

        # create column container for each stage
        stage_containers = []
        for i in range(self.device.stages):
            stage = QVBoxLayout()
            self.stages_container.addLayout(stage)
            stage_containers.append(stage)

            # create a button for each stage
            button = QPushButton()
            button.setText(f"Stage {i + 1}")
            button.setMinimumSize(QSize(0, 24))
            button.setMaximumSize(QSize(big, 24))
            stage.addWidget(button)

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

        # create widgets for each variable and add them to the layout
        for j, variable in enumerate(self.device.variables):
            # add the widgets to the stage containers
            for i, stage in enumerate(stage_containers):
                stage_widget = variable.widget()
                stage.addWidget(stage_widget)
                self.state_widgets[i].append(stage_widget)

            # add the widget to the dc container
            dc_widget = variable.widget()
            if j == 0:
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
        for stage in stage_containers:
            stage.addStretch()
        
        # connect the run button to the submit_experiment method
        self.run_experiment.clicked.connect(self.submit_experiment)

        # connect the menubar actions
        self.actionSave.triggered.connect(self.save_settings_dialog)
        self.actionLoad.triggered.connect(self.load_settings_dialog)

        # load the default values into the newly created widgets
        self.load_settings('default.json')

    '''
    methods to get the values from the widgets and update the device.
    '''

    def get_dc(self) -> Dc:
        # uses setattr to dynamically create a Dc object with the values from the widgets
        dc = Dc()
        for i, variable in enumerate(self.device.variables):
            setattr(dc, variable.id, variable.value(self.dc_widgets[i]))
        return dc

    def get_stages(self) -> list[Stage]:
        # creates a list of Stage objects with the values from the widgets
        stages = []
        for i in range(self.device.stages):
            stage = Stage()
            for j, variable in enumerate(self.device.variables):
                value = variable.value(self.state_widgets[i][j])
                setattr(stage, variable.id, value)
            stages.append(stage)
        return stages

    # updates the device with the values from the widgets
    def update_dc(self):
        self.device.update_dc(self.get_dc())

    # runs the experiment and using the data from the widgets
    def submit_experiment(self):
        self.device.run_experiment(self.get_stages())

    '''
    file save/load methods and dialogs
    '''

    # open a file dialog for the user to choose a file
    def save_settings_dialog(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON File (*.json)")

        if file_name:
            self.save_settings(file_name)

    # save the settings to the file
    def save_settings(self, path):
        data = {
            'dc': self.get_dc(),
            'stages': self.get_stages()
        }
        data_json = json.dumps(data, default=lambda o: o.__dict__)

        with open(path, 'w') as f:
            f.write(data_json)

    # open a file dialog for the user to choose a file
    def load_settings_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON File (*.json)")

        if file_name:
            self.load_settings(file_name)

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

        # update the stage widgets with the values from the file
        for i, stage in enumerate(data['stages']):
            if i < self.device.stages:
                for j, variable in enumerate(self.device.variables):
                    if variable.id in stage:
                        variable.set_value(self.state_widgets[i][j], stage[variable.id])
                    else:
                        print(f"Warning: Unknown variable '{variable.id}' in stage {i} data")
            else:
                print(f"Warning: Extra stage data found for stage {i}, ignoring")


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

