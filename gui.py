import numpy as np

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize
from PyQt6.uic import loadUi

big = 16777215

# initializes the gui using `gui.ui`
class Gui(QMainWindow):
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device

        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        # store reference to all the widgets to get their values later
        self.dc_widgets = []
        self.state_widgets = []
        self.copy_widgets = []

        # create column container for each stage
        stages = self.device.stages
        stage_containers = []
        for i in range(stages):
            stage = QVBoxLayout()
            self.stages_container.addLayout(stage)
            stage_containers.append(stage)

            # create a button for each stage
            button = QPushButton()
            button.setText(f"Stage {i + 1}")
            button.setMinimumSize(QSize(0, 24))
            button.setMaximumSize(QSize(big, 24))
            stage.addWidget(button)

            self.state_widgets.append([])

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
        for variable in self.device.variables:
            # add the widgets to the stage containers
            for i, stage in enumerate(stage_containers):
                stage_widget = variable.widget()
                stage.addWidget(stage_widget)
                self.state_widgets[i].append(stage_widget)

            # add the widget to the dc container
            dc_widget = variable.widget()
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
        self.actionSave.triggered.connect(self.save_settings)
        self.actionLoad.triggered.connect(self.load_settings)

    # applies the current values in the widgets to the numpy arrays
    def apply_values(self):
        # iterate through the widgets and get their values
        for i, variable in enumerate(self.device.variables):
            self.device.dc[i] = variable.value(self.dc_widgets[i])

            for j, stage_widgets in enumerate(self.state_widgets):
                self.device.experiment[j, i] = variable.value(stage_widgets[i])

    # updates the device with the values from the widgets
    def update_dc(self):
        self.apply_values()
        self.device.update_dc()
    
    # runs the experiment and using the data from the widgets
    def submit_experiment(self):
        self.apply_values()
        self.device.run_experiment()

    # saves the current gui settings to a file
    def save_settings(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "Numpy Array File (*.npz)")

        # load the current values from the widgets into the numpy arrays
        self.apply_values()

        # save the numpy arrays to a file
        np.savez(
            file_name,
            dc=self.device.dc,
            experiment=self.device.experiment
        )

    def load_settings(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "Numpy Array File (*.npz)")

        # load the settings from the file
        data = np.load(file_name)

        # update the device's dc and experiment arrays
        self.device.dc = data['dc']
        self.device.experiment = data['experiment']

        # refresh the gui and device with the new values
        self.refresh_widgets()
        self.device.update_dc()

    def refresh_widgets(self):
        # update the widgets with the current values in the numpy arrays
        for i, variable in enumerate(self.device.variables):
            # update the dc widgets
            variable.set_value(self.dc_widgets[i], self.device.dc[i])

            # update the stage widgets
            for j, stage_widgets in enumerate(self.state_widgets):
                variable.set_value(stage_widgets[i], self.device.experiment[j, i])

'''
abstractions over the different widget types used in the gui
'''
class VariableTypeBool:
    def __init__(self, label):
        self.label = label
    
    def widget(self) -> QCheckBox:
        checkbox = QCheckBox()
        checkbox.setMinimumSize(QSize(0, 24))
        checkbox.setMaximumSize(QSize(big, 24))
        return checkbox

    def changed_signal(self, widget: QCheckBox):
        return widget.stateChanged

    def value(self, widget: QCheckBox) -> float:
        return float(widget.isChecked())

    def set_value(self, widget: QCheckBox, value: float):
        widget.setChecked(bool(value))

class VariableTypeInt:
    def __init__(self, label, minimum=0, maximum=100, step=1):
        self.label = label
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
        return int(widget.value())

    def set_value(self, widget: QSpinBox, value: float):
        widget.setValue(int(value))

class VariableTypeFloat:
    def __init__(self, label, minimum=0.0, maximum=1.0, step=0.1):
        self.label = label
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

