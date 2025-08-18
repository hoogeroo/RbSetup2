import numpy as np

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSize

from camera import CameraConnection
from device_types import Dc, DeviceStages, DeviceSettings
from gui_types import big
from multigo import MultiGo
from variable_types import *

# class to represent a stage in the gui. differs from Stage in that it can't be sent to the device
class GuiStage:
    def __init__(self, button, container, widgets, enabled=True):
        self.button = button
        self.container = container
        self.widgets = widgets
        self.enabled = enabled

class StagesGui:
    def __init__(self, window, variables):
        self.window = window
        self.variables = variables

        # store reference to all the widgets to get their values later
        self.dc_widgets = []
        self.copy_widgets = []
        self.stages = []

        # add spacers to the dc, label, and copied containers
        spacers = []
        for i in range(3):
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

        # connect the multigo options button
        self.window.options.clicked.connect(self.multigo_options)

        # connect the run button to the submit_experiment method
        self.window.run_experiment.clicked.connect(self.submit_experiment)

        # connect the load mot checkbox to the update_device_settings method
        self.window.load_mot.stateChanged.connect(self.update_device_settings)

    '''
    methods to get the values from the widgets and update the device.
    '''

    # extracts the values from the dc widgets and creates a Dc object
    def extract_dc(self) -> Dc:
        # uses setattr to dynamically create a Dc object with the values from the widgets
        dc = Dc()
        for i, variable in enumerate(self.variables):
            setattr(dc, variable.id, self.dc_widgets[i].get_value().constant_value())
        return dc

    # extracts the values from the stage widgets and creates a DeviceStages object to send to the device
    def extract_stages(self) -> DeviceStages:
        # initialise the variable lists with the dc value for each variable
        device_stages = DeviceStages()
        for i, variable in enumerate(self.variables):
            setattr(device_stages, variable.id, [self.dc_widgets[i].get_value().constant_value()])

        # extend the lists with the stage values
        for i in range(len(self.stages)):
            # skip the stage if it is not enabled
            if not self.stages[i].enabled:
                continue

            # extract the stage into a temporary object to make it easier to work with
            tmp = Dc()
            for j, variable in enumerate(self.variables):
                value = self.stages[i].widgets[j].get_value()
                setattr(tmp, variable.id, value)

            # get the number of samples
            samples = max(tmp.samples.constant_value(), 1)

            # add values to the lists for each sample
            for sample in range(samples):
                for variable in self.variables:
                    # get the value and list for the variable
                    value = getattr(tmp, variable.id)
                    device_variable_list = getattr(device_stages, variable.id)

                    # special case for time variable
                    if variable.id == "time":
                        device_variable_list.append(tmp.time.constant_value() / samples)
                        continue

                    # if hold repeat the last value
                    if value.is_hold():
                        device_variable_list.append(device_variable_list[-1])
                    # if constant use the constant value
                    elif value.is_constant():
                        device_variable_list.append(value.constant_value())
                    # for float ramps sample the ramp for each value
                    elif isinstance(value, FloatValue):
                        if value.is_ramp():
                            device_variable_list.append(value.sample(sample, samples))

        # turn the lists into numpy arrays
        for variable in self.variables:
            device_variable_list = getattr(device_stages, variable.id)
            device_variable_array = np.array(device_variable_list)

            # apply calibration if needed
            if isinstance(variable, VariableTypeFloat):
                if variable.calibration is not None:
                    device_variable_array = variable.calibration(device_variable_array)

            setattr(device_stages, variable.id, device_variable_array)

        return device_stages

    # updates the device with the values from the widgets
    def update_dc(self):
        # ignore widget updates if the UI is not loaded yet
        if not self.window.ui_loaded:
            return

        # send the extracted dc values to the device
        self.window.gui_pipe.send(self.extract_dc())

    # runs the experiment and using the data from the widgets
    def submit_experiment(self):
        # tell the camera server to acquire a frame
        try:
            camera = CameraConnection()
            camera.shoot(1)
        except Exception as e:
            camera = None
            print("Error occurred while shooting:", e)

        # run the actual experiment
        self.window.gui_pipe.send(self.extract_stages())

        if camera:
            # read the image from the camera server
            picture = camera.read(timeout=1)

            # plot the image
            self.camera_ax.clear()
            self.camera_ax.imshow(picture[0, :, :], aspect='equal')
            self.camera_canvas.figure.colorbar(self.camera_ax.images[0], ax=self.camera_ax)
            self.camera_canvas.draw()

    # open the multigo options popup
    def multigo_options(self):
        multi_go = MultiGo()
        multi_go.exec()

    # send the current device settings to the device
    def update_device_settings(self):
        # create a DeviceSettings object with the current values
        load_mot = self.window.load_mot.isChecked()
        device_settings = DeviceSettings(load_mot=load_mot)

        # send the device settings to the device
        self.window.gui_pipe.send(device_settings)

    '''
    methods for renaming, copying, creating and deleting stages
    '''

    # we need to use the object reference since the index changes when we insert or delete stages
    def get_stage_index(self, stage_container) -> int:
        for i, stage in enumerate(self.stages):
            if stage.container is stage_container:
                return i
        raise ValueError("Stage container not found") 

    # adds a new stage to the gui
    def insert_stage(self, idx: int, name=None, enabled=True):
        stage_container = QVBoxLayout()
        self.window.stages_container.insertLayout(idx, stage_container)

        # create a button at the top of the stage column
        button = QPushButton()
        button.setText(name if name else f"Stage {idx + 1}")
        button.setMinimumSize(QSize(0, 24))
        button.setMaximumSize(QSize(big, 24))
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        button.clicked.connect(lambda: self.disable_stage(self.get_stage_index(stage_container)))
        button.addAction("Rename", lambda: self.rename_stage(self.get_stage_index(stage_container)))
        button.addAction("Copy", lambda: self.copy_stage(self.get_stage_index(stage_container)))
        button.addAction("Paste", lambda: self.paste_stage(self.get_stage_index(stage_container)))
        button.addAction("Insert Stage Left", lambda: self.insert_stage_left(self.get_stage_index(stage_container)))
        button.addAction("Insert Stage Right", lambda: self.insert_stage_right(self.get_stage_index(stage_container)))
        button.addAction("Delete", lambda: self.delete_stage(self.get_stage_index(stage_container)))
        stage_container.addWidget(button)

        # create widgets for each variable and add them to the layout
        widgets = []
        for variable in self.variables:
            widget = variable.widget()
            stage_container.addWidget(widget)
            widgets.append(widget)

        # add a spacer to the stage container
        stage_container.addStretch()

        self.stages.insert(idx, GuiStage(button, stage_container, widgets, enabled))
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