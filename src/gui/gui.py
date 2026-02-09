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
from src.gui.temperatures import fetch_temperatures, ESP_url

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
        self.action_fringe_removal.triggered.connect(self.update_device_settings)
        self.action_pca.triggered.connect(self.update_device_settings)
        self.action_low_pass_filter.triggered.connect(self.update_device_settings)
        self.action_fft_filter.triggered.connect(self.update_device_settings)

        # create the hidden GUI
        self.hidden_gui = HiddenGui(self, variables)

        # create the stages GUI
        self.stages_gui = StagesGui(self, variables, self.hidden_gui)

        # create the plots GUI
        self.plots_gui = PlotsGui(self)

        # load the default values (creates the needed stage widgets)
        load_settings('default.fits', self)

        # uncomment this to add new tabs then save a new 'default.fits' and comment it out again
        # self.stages_gui.insert_stage(4, name="Stage 4", tab="Other")

        # mark the UI as loaded
        self.ui_loaded = True
        self.stages_gui.update_holds()

        # Send device settings to device on startup
        self.update_device_settings()

        # event timer
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.handle_device_events)
        self.event_timer.start(100)

        # temperature polling timer
        self.temp_timer = QTimer()
        self.temp_timer.timeout.connect(self._poll_temperatures)
        if ESP_url:
            self.temp_timer.start(1000)  # poll every 1000 ms

    # polls the gui pipe for messages from the device
    def handle_device_events(self):
        # poll the pipe with no timeout (only read already queued values)
        if self.gui_pipe.poll():
            # get the received value
            msg = self.gui_pipe.recv()

            if isinstance(msg, FluorescenceSample):
                self.plots_gui.update_fluorescence(msg)
            elif isinstance(msg, CameraImages):
                self.plots_gui.update_images(msg)
            elif isinstance(msg, MultiGoProgress):
                self.multigo_progress.update_progress(msg)
            elif isinstance(msg, AiProgress):
                self.ai_progress.update_progress(msg)
            elif isinstance(msg, AiPlotData):
                # Pass AI plot data to the AI progress dialog if it exists
                if hasattr(self, 'ai_progress') and self.ai_progress:
                    self.ai_progress.update_ai_plots(msg)
            else:
                print("Received unknown message type from device:", type(msg))

    # send the current device settings to the device
    def update_device_settings(self):
        # create a DeviceSettings object with the current values
        load_mot = self.load_mot.isChecked()
        save_runs = self.save_runs.isChecked()
        
        # Get current filtering settings from the menu actions
        fringe_removal = self.action_fringe_removal.isChecked()
        pca = self.action_pca.isChecked()
        low_pass = self.action_low_pass_filter.isChecked()
        fft_filter = self.action_fft_filter.isChecked()
        
        device_settings = DeviceSettings(
            load_mot=load_mot,
            save_runs=save_runs,
            fringe_removal=fringe_removal,
            pca=pca,
            low_pass=low_pass,
            fft_filter=fft_filter
        )

        # send the device settings to the device
        self.gui_pipe.send(device_settings)

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
    
    # poll the ESP8266 server for temperature data and update the GUI
    def _poll_temperatures(self):
        vals = fetch_temperatures(ESP_url)
        if vals:
            self.plots_gui.update_temperatures(vals)