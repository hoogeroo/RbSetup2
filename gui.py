'''
gui.py: creates the main gui and sends commands to main.py to interface with the device
'''

import numpy as np
from astropy.io import fits

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic import loadUi

from multigo import MultiGoProgress, MultiGoRunVariable
from plots import PlotsGui, CameraImages, FluorescenceSample
from stages import StagesGui
from value_types import AnyValue

def run_gui(variables, gui_pipe):
    app = QApplication([])
    gui = Gui(variables, gui_pipe)
    gui.show()
    app.exec()

class Gui(QMainWindow):
    '''
    Main GUI class that initializes the user interface and connects it to the device.
    It creates the layout, widgets, and connects signals to the device methods.
    The gui is built using PyQt6 and the layout is defined in `gui.ui`.
    '''
    def __init__(self, variables, gui_pipe):
        super(Gui, self).__init__()
        self.gui_pipe = gui_pipe
        self.ui_loaded = False

        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)

        # remove central widget since we are using docks
        self.setCentralWidget(None)

        # connect the menu actions
        self.action_save.triggered.connect(self.save_settings_dialog)
        self.action_load.triggered.connect(self.load_settings_dialog)

        # create the stages GUI
        self.stages_gui = StagesGui(self, variables)

        # create the plots GUI
        self.plots_gui = PlotsGui(self)

        # load the default values (creates the needed stage widgets)
        self.load_settings('default.fits')

        # mark the UI as loaded
        self.ui_loaded = True

        # fluorescence timer
        self.fluorescence_timer = QTimer()
        self.fluorescence_timer.timeout.connect(self.handle_device_events)
        self.fluorescence_timer.start(100)

    def handle_device_events(self):
        # poll the pipe with no timeout (only read already queued values)
        if self.gui_pipe.poll():
            # get the recieved value
            recieved = self.gui_pipe.recv()

            if isinstance(recieved, FluorescenceSample):
                self.plots_gui.update_fluorescence(recieved)
            elif isinstance(recieved, CameraImages):
                self.plots_gui.update_images(recieved)
            elif isinstance(recieved, MultiGoProgress):
                self.multigo_progress.update_progress(recieved)
            else:
                print("Received unknown message type from device:", type(recieved))

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
        # create the primary HDU
        primary_hdu = fits.PrimaryHDU()

        # save the window layout
        layout = self.saveState()
        primary_hdu.header['layout'] = str(layout)

        # add the stages
        stage_columns = []

        # add the stage name column
        stage_names = [stage.button.text() for stage in self.stages_gui.stages]
        stage_names.insert(0, 'dc')
        stage_columns.append(fits.Column(name='stage_name', format='A20', array=stage_names))
        
        # add the enabled column
        enabled = [stage.enabled for stage in self.stages_gui.stages]
        enabled.insert(0, True)  # dc is always enabled
        stage_columns.append(fits.Column(name='enabled', format='L', array=enabled))

        # add the id column
        ids = [stage.id for stage in self.stages_gui.stages]
        ids.insert(0, 'dc')
        stage_columns.append(fits.Column(name='id', format='A36', array=ids))

        # add columns for each variable in the gui
        for i, variable in enumerate(self.stages_gui.variables):
            col = variable.fits_column()

            # gather the column of data
            data = []
            data.append(self.stages_gui.dc_widgets[i].get_value().array)
            for stage in self.stages_gui.stages:
                value = stage.widgets[i].get_value().array
                data.append(value)

            col.array = np.stack(data)
            stage_columns.append(col)

        # create a fits table hdu for the stages
        stages_hdu = fits.BinTableHDU.from_columns(stage_columns)

        # add the multigo settings
        multigo_columns = []
        run_variables = self.stages_gui.run_variables

        # add the stage ids
        stage_ids = [var.stage_id for var in run_variables]
        multigo_columns.append(fits.Column(name='stage_id', format='A36', array=stage_ids))

        # add the variable ids
        variable_ids = [var.variable_id for var in run_variables]
        multigo_columns.append(fits.Column(name='variable_id', format='A36', array=variable_ids))

        # add the start and end values
        start_values = [AnyValue(var.start).to_array() for var in run_variables]
        multigo_columns.append(fits.Column(name='start_value', format='4D', dim='(4)', array=start_values))
        end_values = [AnyValue(var.end).to_array() for var in run_variables]
        multigo_columns.append(fits.Column(name='end_value', format='4D', dim='(4)', array=end_values))

        # add the steps
        step_values = [var.steps for var in run_variables]
        multigo_columns.append(fits.Column(name='steps', format='K', array=step_values))

        # create a fits table hdu for the multigo settings
        multigo_hdu = fits.BinTableHDU.from_columns(multigo_columns)

        # write the HDU array
        hdul = fits.HDUList([primary_hdu, stages_hdu, multigo_hdu])
        hdul.writeto(path, overwrite=True)

    # load the settings from the file
    def load_settings(self, path):
        # read the fits file
        primary_hdu, stages_hdu, multigo_hdu = fits.open(path)

        # load the window layout
        layout = primary_hdu.header['layout']
        self.restoreState(eval(layout))

        # load the stages data
        stages_data = stages_hdu.data

        # update the dc widgets with the values from the file
        for dc_widget in self.stages_gui.dc_widgets:
            if dc_widget.variable.id in stages_data.names:
                array = stages_data[0][dc_widget.variable.id]
                value = dc_widget.variable.value_type.from_array(array)
                dc_widget.set_value(value)
            else:
                print(f"Warning: '{dc_widget.variable.id}' not in dc data")
        stages_data = stages_data[1:]  # skip the first row which is the dc

        # clear the current stage widgets
        for i in reversed(range(len(self.stages_gui.stages))):
            self.delete_stage(i)
        self.stages_gui.stages.clear()

        # create new stage widgets based on the loaded data
        for i, stage_row in enumerate(stages_data):
            # create new column of widgets for the stage
            stage_name = stage_row['stage_name'].strip()
            enabled = stage_row['enabled']
            id = stage_row['id'].strip()
            self.stages_gui.insert_stage(len(self.stages_gui.stages), name=stage_name, enabled=enabled, id=id)

            # fill the stage widgets with the values from the file
            for widget in self.stages_gui.stages[i].widgets:
                if widget.variable.id in stages_data.names:
                    array = stage_row[widget.variable.id]
                    value = widget.variable.value_type.from_array(array)
                    widget.set_value(value)
                else:
                    print(f"Warning: Unknown variable '{widget.variable.id}' in stage {i} data")

        # load the multigo settings
        self.stages_gui.run_variables = []
        for row in multigo_hdu.data:
            self.stages_gui.run_variables.append(MultiGoRunVariable(
                row['stage_id'],
                row['variable_id'],
                AnyValue.from_array(row['start_value']).to_value(),
                AnyValue.from_array(row['end_value']).to_value(),
                row['steps']
            ))
