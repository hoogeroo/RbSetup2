'''
gui.py: creates the main gui and sends commands to main.py to interface with the device
'''

import numpy as np
import json

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt
from PyQt6.uic import loadUi

from astropy.io import fits

from camera import CameraConnection
from gui_types import *

def run_gui(variables, sender):
    app = QApplication([])
    gui = Gui(variables, sender)
    gui.show()
    app.exec()

# dummy class used to represent the device's digital and analog outputs
# this class will be fill with ids set in the variables array then 
# sent to the device
class Dc:
    def __init__(self):
        pass

# same as above but for an experiment stage
class Stage:
    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled

# class to represent a stage in the gui. differs from Stage in that it can't be sent to the device
class GuiStage:
    def __init__(self, button, container, widgets, enabled=True):
        self.button = button
        self.container = container
        self.widgets = widgets
        self.enabled = enabled

    def update_widgets(self):
        pass

class Gui(QMainWindow):
    '''
    Main GUI class that initializes the user interface and connects it to the device.
    It creates the layout, widgets, and connects signals to the device methods.
    The gui is built using PyQt6 and the layout is defined in `gui.ui`.
    '''
    def __init__(self, variables, sender):
        super(Gui, self).__init__()
        self.variables = variables
        self.sender = sender

        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        # remove central widget since we are using docks
        self.setCentralWidget(None)

        # plot
        self.camera_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.camera_ax = self.camera_canvas.figure.subplots()
        self.camera_grid.addWidget(self.camera_canvas, 1, 4, 1, 1)

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
        self.dc_container.addWidget(spacers[0])
        self.label_container.addWidget(spacers[1])
        self.copied_container.addWidget(spacers[2])

        # fill dc, label, and copied containers with widgets
        for i, variable in enumerate(self.variables):
            # add the widget to the dc container
            dc_widget = variable.widget()
            if i == 0:
                dc_widget.setEnabled(False)  # time doesn't make sense for dc
            dc_widget.changed_signal().connect(self.update_dc)
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
        self.load_settings('default.fits')

    def closeEvent(self, event):
        self.sender.send("exit")

    '''
    methods to get the values from the widgets and update the device.
    '''

    # extracts the values from the dc widgets and creates a Dc object
    def extract_dc(self) -> Dc:
        # uses setattr to dynamically create a Dc object with the values from the widgets
        dc = Dc()
        for i, variable in enumerate(self.variables):
            setattr(dc, variable.id, self.dc_widgets[i].get_value())
        return dc

    # extracts the values from the stage widgets and creates a list of Stage objects
    def extract_stages(self) -> list[Stage]:
        # creates a list of Stage objects with the values from the widgets
        stages = []
        for i in range(len(self.stages)):
            stage = Stage(self.stages[i].button.text(), self.stages[i].enabled)
            for j, variable in enumerate(self.variables):
                value = self.stages[i].widgets[j].get_value()
                setattr(stage, variable.id, value)
            stages.append(stage)
        return stages

    # updates the device with the values from the widgets
    def update_dc(self):
        self.sender.send(self.extract_dc())

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
        self.sender.send(self.extract_stages())

        if camera:
            # read the image from the camera server
            picture = camera.read(timeout=1)

            # plot the image
            self.camera_ax.clear()
            self.camera_ax.imshow(picture[0, :, :], aspect='equal')
            self.camera_canvas.figure.colorbar(self.camera_ax.images[0], ax=self.camera_ax)
            self.camera_canvas.draw()

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
        self.stages_container.insertLayout(idx, stage_container)

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

    '''
    methods to save and load settings from a file
    '''

    # open a file dialog for the user to choose a file
    def save_settings_dialog(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "FITS File (*.fits)")

        if file_name:
            self.save_settings(file_name)

    # open a file dialog for the user to choose a file
    def load_settings_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "FITS File (*.fits)")

        if file_name:
            self.load_settings(file_name)

    # save the settings to the file
    def save_settings(self, path):
        columns = []

        # add the stage name column
        stage_names = [stage.button.text() for stage in self.stages]
        stage_names.insert(0, 'dc')
        columns.append(fits.Column(name='stage_name', format='A20', array=stage_names))
        
        # add the enabled column
        enabled = [stage.enabled for stage in self.stages]
        enabled.insert(0, True)  # dc is always enabled
        columns.append(fits.Column(name='enabled', format='L', array=enabled))

        # add columns for each variable in the gui
        for i, variable in enumerate(self.variables):
            col = variable.fits_column()

            # gather the column of data
            data = []
            data.append(self.dc_widgets[i].get_value().array)
            for stage in self.stages:
                value = stage.widgets[i].get_value().array
                data.append(value)

            col.array = np.stack(data)
            columns.append(col)

        hdu = fits.BinTableHDU.from_columns(columns)
        hdu.writeto(path, overwrite=True)

    # load the settings from the file
    def load_settings(self, path):
        # read the fits file
        hdu = fits.open(path)[1]
        data = hdu.data

        # update the dc widgets with the values from the file
        for dc_widget in self.dc_widgets:
            if dc_widget.variable.id in data.names:
                array = data[0][dc_widget.variable.id]
                value = dc_widget.variable.value_type.from_array(array)
                dc_widget.set_value(value)
            else:
                print(f"Warning: '{dc_widget.variable.id}' not in dc data")
        data = data[1:]  # skip the first row which is the dc

        # clear the current stage widgets
        for i in reversed(range(len(self.stages))):
            self.delete_stage(i)
        self.stages.clear()
        
        # create new stage widgets based on the loaded data
        for i, stage_row in enumerate(data):
            # create new column of widgets for the stage
            stage_name = stage_row['stage_name'].strip()
            enabled = stage_row['enabled']
            self.insert_stage(len(self.stages), name=stage_name, enabled=enabled)

            # fill the stage widgets with the values from the file
            for widget in self.stages[i].widgets:
                if widget.variable.id in data.names:
                    array = stage_row[widget.variable.id]
                    value = widget.variable.value_type.from_array(array)
                    widget.set_value(value)
                else:
                    print(f"Warning: Unknown variable '{widget.variable.id}' in stage {i} data")
