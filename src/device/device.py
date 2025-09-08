'''
device.py: has the device code that works without artiq. mainly talking to the gui and taking photos
'''

from datetime import datetime
from multiprocessing import Pipe, Process
import numpy as np
import os
from scipy.interpolate import CubicSpline

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

SAVE_PATH = "runs"

'''
Abstraction over the device to run the gui without artiq
'''
class AbstractDevice:
    def build(self):
        x = np.linspace(0.0, 1.0, 10)
        y = x**3
        calibration = CubicSpline(x, y)

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

        # Initialize image analysis
        self.image_analysis = ImageAnalysis()
        
        # Initialize background management for filtering
        self.background_bank = np.zeros((512, 512, 100))  # Background image bank
        self.number_of_backgrounds = 0
        self.Natoms = []
        self.MaxOD = []

        # process all the messages from the gui
        queue = []
        while True:
            # grab all the messages from the gui into the queue
            if device_pipe.poll(0.1):
                while device_pipe.poll():
                    msg = device_pipe.recv()
                    queue.append(msg)
                print("polled queue", queue)

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
                    self.device_settings = msg
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
            # Process images
            Foreground = images[0,:,:] - images[2,:,:]
            Background = images[1,:,:] - images[2,:,:]
            self.save_background(Background) # Saves new background if unique
            ODimage = -np.log((Foreground)/(Background))

            self.Natoms.append(self.image_analysis.get_atom_number(ODimage = ODimage))
            self.MaxOD.append(self.image_analysis.get_max_od(ODimage = ODimage))

            # apply filtering based on device settings
            if self.device_settings.fringe_removal  and self.number_of_backgrounds > 5:
                ODimage, opref = filtering.fringe_removal(Foreground, self.background_bank[:,:,:self.number_of_backgrounds])
            
            if self.device_settings.pca and self.number_of_backgrounds > 5:
                ODimage, opref = filtering.pca(Foreground, self.background_bank[:,:,:self.number_of_backgrounds])
            
            if self.device_settings.low_pass:
                ODimage = filtering.low_pass(images)
            
            if self.device_settings.fft_filter:
                ODimage = filtering.fft_filter(ODimage)    

            # send the picture to the gui
            self.device_pipe.send(CameraImages(images, ODimage))

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


    def save_background(self, new_background: np.ndarray):
        # Saves Bacground image to bank if unique
        # Uses circular buffer to keep the 100 most recent backgrounds.
        # Check if this background already exists
        for i in range(self.background_bank.shape[2]):
            if np.allclose(self.background_bank[:, :, i], new_background, atol=0):
                return False 
        
        # Add new background at current BGindex position
        self.background_bank[:, :, self.BGindex] = new_background
        
        # Increment BGindex and wrap around if bank is full using modulo
        self.BGindex = (self.BGindex + 1) % self.background_bank.shape[2]
        self.number_of_backgrounds += 1
        
        return True  # Background was added