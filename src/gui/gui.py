'''
gui.py: creates the main gui and sends commands to main.py to interface with the device
'''

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt6.uic import loadUi

from src.device.ai import AiProgress
from src.device.device_types import DeviceSettings
from src.device.multigo import MultiGoProgress
from src.gui.ai import AiPlotData
from src.gui.fits import load_settings, save_settings
from src.gui.hidden import HiddenGui
from src.gui.plots import CameraImages, FluorescenceSample, PlotsGui
from src.gui.stages import StagesGui

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
        
        # create the hidden GUI
        self.hidden_gui = HiddenGui(self, variables)

        # create the stages GUI
        self.stages_gui = StagesGui(self, variables, self.hidden_gui)

        # create the plots GUI
        self.plots_gui = PlotsGui(self)

        # load the default values (creates the needed stage widgets)
        load_settings('default.fits', self)

        # mark the UI as loaded
        self.ui_loaded = True
        
        # Send device settings to device on startup
        self.stages_gui.update_device_settings()

        # event timer
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.handle_device_events)
        self.event_timer.start(100)

    def handle_device_events(self):
        # poll the pipe with no timeout (only read already queued values)
        if self.gui_pipe.poll():
            # get the recieved value
            recieved = self.gui_pipe.recv()

            if isinstance(recieved, FluorescenceSample):
                self.plots_gui.update_fluorescence(recieved.sample)
            elif isinstance(recieved, CameraImages):
                self.plots_gui.update_images(recieved.images)
            elif isinstance(recieved, MultiGoProgress):
                self.multigo_progress.update_progress(recieved)
            elif isinstance(recieved, AiProgress):
                self.ai_progress.update_progress(recieved)
            elif isinstance(recieved, AiPlotData):
                # Pass AI plot data to the AI progress dialog if it exists
                if hasattr(self, 'ai_progress') and self.ai_progress:
                    self.ai_progress.update_ai_plots(recieved)
            else:
                print("Received unknown message type from device:", type(recieved))

    def send_filtering_settings(self):
        # Send current filtering settings to the device
        
        # Create DeviceSettings with current filtering
        device_settings = DeviceSettings(
            load_mot=self.load_mot.isChecked(),
            save_runs=self.save_runs.isChecked(),
            fringe_removal=self.action_fringe_removal.isChecked(),
            pca=self.action_pca.isChecked(),
            low_pass=self.action_low_pass_filter.isChecked(),
            fft_filter=self.action_fft_filter.isChecked()
        )
        # Send via pipe to device
        self.gui_pipe.send(device_settings)
        print(f"Sent filtering settings: {device_settings}")

    '''
    methods to save and load settings from a file
    '''

    # open a file dialog for the user to choose a file
    def save_settings_dialog(self):
        # open a file dialog for the user to choose a file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "FITS File (*.fits)")

        if file_name:
            save_settings(
                file_name,
                self.stages_gui.variables,
                self.stages_gui.extract_stages(),
                self.plots_gui.images,
                self.stages_gui.multigo_settings,
                self.stages_gui.ai_settings,
                self.saveState(),
            )

    # open a file dialog for the user to choose a file
    def load_settings_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "FITS File (*.fits)")

        if file_name:
            load_settings(file_name, self)
