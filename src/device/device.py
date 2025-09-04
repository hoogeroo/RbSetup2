'''
device.py: has the device code that works without artiq. mainly talking to the gui and taking photos
'''

from datetime import datetime
from multiprocessing import Pipe, Process
import numpy as np
import os
from scipy.interpolate import CubicSpline

from src.device.device_types import Dc, DeviceSettings, FlattenedStages, MultiGoSubmission, Stages
from src.device.multigo import MultiGoCancel, run_multigo_experiment
from src.gui.fits import save_settings
from src.gui.gui import run_gui
from src.gui.plots import CameraImages, FluorescenceSample
from src.host.camera import CameraConnection
from src.variable_types import *

SAVE_PATH = "runs"

'''
Abstraction over the device to run the gui without artiq
'''
class AbstractDevice:
    def build(self):
        # coil_current_calibration = lambda percentage: 5.0 * percentage / 100.0

        # percentage = np.concatenate((np.arange(3, 10, 1), np.arange(10, 70, 10))) 
        # dipole_powers = np.array([23.3E-3, 59E-3, 0.165, 0.377, 0.715, 1.18, 1.79, 2.51, 14.6, 31, 49.3, 65.4, 71.1]) # in milliWatts
        # dipole_powers *= 100 / max(dipole_powers)
        # dipole_volts = 3.4 * percentage / max(percentage) # in Volts
        # dipole_calibration = np.polyfit(dipole_powers, dipole_volts, 5) # We want to put in a desired power and get back a voltage

        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0, 'ms'),
            VariableTypeInt("Samples", "samples", 1, 10000, 100),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Dipole Amplitude", "dipole_amplitude", 0.0, 3.0, 0.1),
            VariableTypeFloat("MOT 2 coils current", "mot2_coils_current", 0.0, 5.0, 0.5),
            VariableTypeFloat("x Field", "x_field", 0.0, 5.0, 0.01),
            VariableTypeFloat("y Field", "y_field", 0.0, 5.0, 0.01),
            VariableTypeFloat("z Field", "z_field", 0.0, 5.0, 0.01),
            VariableTypeFloat("Repump Amplitude", "repump_amplitude"),
            VariableTypeFloat("Repump Frequency (MHz)", "repump_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("1st MOT Amplitude", "mot1_amplitude"),
            VariableTypeFloat("1st MOT Frequency (MHz)", "mot1_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("2nd MOT Amplitude", "mot2_amplitude"),
            VariableTypeFloat("2nd MOT Frequency (MHz)", "mot2_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("Push Amplitude", "push_amplitude"),
            VariableTypeFloat("Push Frequency (MHz)", "push_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("Shadow Amplitude", "shadow_amplitude"),
            VariableTypeFloat("Shadow Frequency (MHz)", "shadow_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("Optical Pump Amplitude", "optical_pump_amplitude"),
            VariableTypeFloat("Optical Pump Frequency (MHz)", "optical_pump_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeFloat("Sheet Amplitude", "sheet_amplitude"),
            VariableTypeFloat("Sheet Frequency (MHz)", "sheet_frequency", 55.0, 120.0, 1.0, 'MHz'),
            VariableTypeBool("Shutter", "shutter"),
            VariableTypeBool("Grey Molasses Shutter", "grey_molasses_shutter"),

            # VariableTypeBool("RF Disable", "rf_disable"),
            # VariableTypeBool("RF Freq Ramp", "rf_freq_ramp"),

            # VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            # VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0, 'MHz'),

        ]

    # spawns the gui in a separate process
    def run(self):
        # create a pipe for communication between the gui and the device
        device_pipe, gui_pipe = Pipe()
        self.device_pipe = device_pipe

        # start the gui in a separate process
        self.gui_process = Process(target=run_gui, args=(self.variables, gui_pipe,))
        self.gui_process.daemon = True # so gui exits when main process exits
        self.gui_process.start()

        # initialize the device settings
        self.device_settings = DeviceSettings()

        # wait for the gui to send a message
        while True:
            # check for messages from the gui
            if device_pipe.poll(0.1):
                msg = device_pipe.recv()

                if isinstance(msg, Dc):
                    # update the device with the new values
                    self.update_dc(msg)
                elif isinstance(msg, Stages):
                    # run the experiment with the provided stages
                    self.run_experiment(msg)
                elif isinstance(msg, MultiGoSubmission):
                    # run the multi-go routine
                    run_multigo_experiment(self, msg.multigo_settings, msg.stages)
                elif isinstance(msg, DeviceSettings):
                    # update the device settings
                    self.device_settings = msg
                elif isinstance(msg, MultiGoCancel):
                    print("Can't cancel multigo - not running")
                else:
                    print(f"Received unknown message type: {type(msg)}")
                    break

            # check if the GUI process is still alive
            if not self.gui_process.is_alive():
                break

            # read the fluorescence signal
            fluorescence = self.read_fluorescence()
            device_pipe.send(FluorescenceSample(fluorescence))

            # pulse the push laser if requested
            if self.device_settings.load_mot:
                self.pulse_push_laser()

        print("Exiting...")

        # stop the gui process
        self.gui_process.terminate()
        self.gui_process.join()

    # dummy method to be overridden by the device
    def update_dc(self, dc):
        print("DC updated:", dc)

    # handles the host side functions of running an experiment
    def run_experiment(self, stages):
        # tell the camera server to acquire a frame
        camera = None
        try:
            camera = CameraConnection()
            camera.shoot(1)
        except Exception as e:
            print("Error occurred while shooting:", e)

        # run the experiment on the artiq device
        flattened_stages = FlattenedStages(stages, self.variables)
        self.run_experiment_device(flattened_stages)

        # read back the camera images
        images = None
        if camera:
            try:
                # read the image from the camera server
                images = camera.read(timeout=1)
            except Exception as e:
                print("Error occurred while reading camera images:", e)
        if images is not None:
            # send the picture to the gui
            self.device_pipe.send(CameraImages(images))

        # save the results if requested
        if self.device_settings.save_runs:
            # create path using SAVE_PATH and date/time
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = os.path.join(SAVE_PATH, f"{timestamp}.fits")

            # create the save directory if it doesn't exist
            os.makedirs(SAVE_PATH, exist_ok=True)

            # save the settings to the file
            save_settings(
                file_path,
                self.variables,
                stages,
                images,
                overwrite=False,
            )

    # dummy method to be overridden by the device
    def run_experiment_device(self, flattened_stages):
        print("Experiment run with stages:", flattened_stages)

    # pulse push laser
    def pulse_push_laser(self):
        print("Pulsing push laser")

    # read fluorescence signal
    def read_fluorescence(self) -> float:
        return 100.0
