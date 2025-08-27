from datetime import datetime
from multiprocessing import Process, Pipe
import numpy as np
import os
from scipy.interpolate import CubicSpline

from camera import CameraConnection
from device_types import Dc, Stages, FlattenedStages, MultiGoSubmission, DeviceSettings
from fits import save_settings
from gui import run_gui
from multigo import MultiGoCancel, run_multigo_experiment
from plots import CameraImages, FluorescenceSample
from variable_types import *

SAVE_PATH = "runs"

'''
Abstraction over the device to run the gui without artiq
'''
class AbstractDevice:
    def build(self):
        x = np.linspace(0.0, 1.0, 10)
        y = x**3
        laser_calibration = CubicSpline(x, y)

        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0, 'ms'),
            VariableTypeInt("Samples", "samples", 1, 10000, 100),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Analog", "analog", calibration=laser_calibration),
            VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0, 'MHz'),
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
        try:
            camera = CameraConnection()
            camera.shoot(1)
        except Exception as e:
            camera = None
            print("Error occurred while shooting:", e)

        # run the experiment on the artiq device
        flattened_stages = FlattenedStages(stages, self.variables)
        self.run_experiment_device(flattened_stages)

        # read back the camera images
        images = None
        if camera:
            # read the image from the camera server
            images = camera.read(timeout=1)

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

if __name__ == '__main__':
    device = AbstractDevice()
    device.build()
    device.run()

    exit(0)
