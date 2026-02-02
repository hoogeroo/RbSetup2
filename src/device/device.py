'''
device.py: has the device code that works without artiq. mainly talking to the gui and taking photos
'''

from datetime import datetime
from multiprocessing import Pipe, Process
import numpy as np
import os
from scipy.interpolate import CubicSpline
import time

from src.device.ai import AiCancel, AiExecuter
from src.device.device_types import AiSubmission, DeviceSettings, FlattenedStages, MultiGoSubmission, Stage, Stages
from src.device.multigo import MultiGoCancel, run_multigo_experiment
from src.gui.fits import save_settings
from src.gui.gui import run_gui
from src.gui.plots import CameraImages, FluorescenceSample
from src.host.camera import CameraConnection
from src.variable_types import VariableTypeBool, VariableTypeInt, VariableTypeFloat
from src.device import filtering
from src.device.data_analysis import ImageAnalysis
from src.value_types import BoolValue, IntValue, FloatValue

SAVE_PATH = "runs"

# TCP settings for pulse control
TCP_IP = "130.216.51.242"
TCP_PORT = 8833

'''
Abstraction over the device to run the gui without artiq
'''
class AbstractDevice:
    def build(self):
        # example calibration for an analog output
        x = np.linspace(0.0, 1.0, 10)
        y = x**3
        calibration = CubicSpline(x, y)

        # example variable definitions
        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0),
            VariableTypeInt("Samples", "samples", 1, 10000, 100),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Analog", "analog", calibration=calibration),
            VariableTypeFloat("x Field", "x_field", 0.0, 5.0, 0.1, hidden=True),
            VariableTypeFloat("z Field", "z_field", 0.0, 5.0, 0.1, hidden=True),
            VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0),
        ]

        # initialize the device settings
        self.device_settings = DeviceSettings()

        # initialize background management for filtering
        self.image_analysis = ImageAnalysis(self)

    # spawns the gui in a separate process
    def run(self):
        # create a pipe for communication between the gui and the device
        device_pipe, gui_pipe = Pipe()
        self.device_pipe = device_pipe

        # start the gui in a separate process
        self.gui_process = Process(target=run_gui, args=(self.variables, gui_pipe,))
        self.gui_process.daemon = True # so gui exits when main process exits
        self.gui_process.start()

        # process all the messages from the gui
        queue = []
        while True:
            # grab all the messages from the gui into the queue
            if device_pipe.poll(0.1):
                while device_pipe.poll():
                    msg = device_pipe.recv()
                    queue.append(msg)

            # process all the messages from the queue
            while queue:
                # get the next message
                msg = queue.pop(0)

                # process the message based on its type
                if isinstance(msg, Stage):
                    # only use the latest dc message (skip message if newer one exists)
                    found = False
                    for m in queue:
                        if isinstance(m, Stage):
                            found = True
                            break
                    if found:
                        continue
                    self.push_amp = msg.push_amplitude.constant_value()
                    self.mot1_amp = msg.mot1_amplitude.constant_value()
                    self.push_freq = msg.push_frequency.constant_value()
                    self.mot1_freq = msg.mot1_frequency.constant_value()

                    dds_amp_update(3, self.push_amp) 
                    dds_freq_update(3, self.push_freq)
                    dds_amp_update(1, self.mot1_amp)
                    dds_freq_update(1, self.mot1_freq)

                    # sets the outputs to the ones in a stage (for dc)
                    self.run_stage(msg)
                elif isinstance(msg, Stages):
                    # run the experiment with the provided stages
                    self.run_experiment(msg)
                elif isinstance(msg, MultiGoSubmission):
                    # run the multi-go routine
                    run_multigo_experiment(self, msg.multigo_settings, msg.stages)
                elif isinstance(msg, AiSubmission):
                    # run the AI routine
                    ai_executer = AiExecuter(self, msg.multigo_settings, msg.ai_settings, msg.stages)
                    ai_executer.run_ai_experiment()
                elif isinstance(msg, DeviceSettings):
                    # update the device settings
                    self.update_device_settings(msg)
                elif isinstance(msg, MultiGoCancel):
                    print("Can't cancel multigo - not running")
                elif isinstance(msg, AiCancel):
                    print("Can't cancel AI - not running")
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

    # sets the current output values to the ones in a stage
    def run_stage(self, stage):
        flattened_stages = FlattenedStages(Stages(stage, []), self.variables)
        self.run_experiment_device(flattened_stages)

    # handles the host side functions of running an experiment
    def run_experiment(self, stages, multigo_settings=None) -> tuple[float, float, np.ndarray]:
        disable_pulsing()
        time.sleep(0.2)

        # tell the camera server to acquire a frame
        camera = None
        try:
            camera = CameraConnection()
            camera.shoot(3)
        except Exception as e:
            print("Error occurred while shooting:", e)

        # run the experiment on the artiq device
        flattened_stages = FlattenedStages(stages, self.variables)
        self.run_experiment_device(flattened_stages)

        enable_pulsing()

        # read back the camera images
        n_atoms = float('nan')
        max_od = float('nan')
        images = None
        camera_images = None
        if camera:
            try:
                # read the image from the camera server
                images = camera.read(timeout=1)
            except Exception as e:
                print("Error occurred while reading camera images:", e)
        if images is not None:
            # filter the images and extract parameters
            camera_images = CameraImages(images[0], images[1], images[2])
            self.device_pipe.send(self.image_analysis.filter_images(camera_images))

        # save the results if requested (only save when we actually have camera_images)
        if self.device_settings.save_runs and camera_images is not None:
            # create path using SAVE_PATH and date/time
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # determine base save directory; for multigo, put runs in a subfolder
            save_dir = SAVE_PATH
            if multigo_settings is not None:
                # Create/reuse a per-multigo folder so all fits for the same multigo go to the same place
                # Use an explicit session key if provided, otherwise fall back to the multigo_settings object's id
                mg_key = getattr(multigo_settings, "_multigo_session_id", None) or id(multigo_settings)

                # if this is a new multigo session (or first time seeing it), compute and store the folder
                if not hasattr(self, "_current_multigo_key") or self._current_multigo_key != mg_key:
                    save_dir = os.path.join(SAVE_PATH, f"multigo_{timestamp}")

                    # persist for subsequent runs within the same multigo session
                    self._current_multigo_key = mg_key
                    self._current_multigo_dir = save_dir
                else:
                    # reuse previously determined directory for this multigo session
                    save_dir = getattr(self, "_current_multigo_dir", SAVE_PATH)

            # create directory if it doesn't exist
            os.makedirs(save_dir, exist_ok=True)            

            # build file path and save
            file_path = os.path.join(save_dir, f"{timestamp}.fits")
            save_settings(
                file_path,
                self.variables,
                stages,
                camera_images,
                overwrite=False,
            )
        
        return (n_atoms, max_od, images)

    # dummy method to be overridden by the device
    def run_experiment_device(self, flattened_stages):
        print("Experiment run with stages:", flattened_stages)

    # pulse push laser
    def pulse_push_laser(self):
        print("Pulsing push laser")

    # read fluorescence signal
    def read_fluorescence(self) -> float:
        return 100.0
    
    def update_device_settings(self, device_settings):
        self.device_settings = device_settings

        # Check if MOT loading is enabled and handle pulsing accordingly
        if self.device_settings.load_mot:
            enable_pulsing()
        else:
            disable_pulsing()

'''
temporary functions to enable/disable pulsing
'''

def enable_pulsing():
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml = 'PULSE,ON'
        s.send(ml.encode())

        s.close()
        time.sleep(0.1)
    except:
        pass



def disable_pulsing():
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        ml = 'PULSE,OFF'
        s.send(ml.encode())

        s.close()
        time.sleep(0.1)
    except:
        pass

def dds_amp_update(id, amplitude):
    import socket
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((TCP_IP, TCP_PORT))
        ml = 'AMPL,%d,%f' % (id, amplitude)
        s.send(ml.encode())
        s.recv(5)
        s.close()
    except:
        pass
 

def dds_freq_update(id, frequency):
    import socket
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((TCP_IP, TCP_PORT))
        ml = 'FREQ,%d,%f' % (id, frequency)
        s.send(ml.encode())
        s.recv(5)
        s.close()
    except:
        pass