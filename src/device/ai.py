from src.device.device_types import Stages
from src.device.multigo import MultiGoSettings
from src.gui.plots import FluorescenceSample

# settings for the AI experiment
class AiSettings:
    def __init__(self, pre_training_steps, training_steps):
        self.pre_training_steps = pre_training_steps
        self.training_steps = training_steps

# message to indicate AI progress to the gui
class AiProgress:
    def __init__(self, current_step, total_steps):
        self.current_step = current_step
        self.total_steps = total_steps

# message to cancel the AI experiment
class CancelAi:
    pass

def run_ai_experiment(device, multigo_settings: MultiGoSettings, ai_settings: AiSettings, stages: Stages):
    # implement the AI experiment logic here
    for i in range(10):
        # simulate some processing
        progress = AiProgress(i, 10)
        device.device_pipe.send(progress)

        # wait for fluorescence
        canceled = False
        while True:
            # wait for cancellation for 100ms
            if device.device_pipe.poll(0.1):
                msg = device.device_pipe.recv()
                if not isinstance(msg, AiCancel):
                    print(f"Received weird message during multigo: {type(msg)}")
                canceled = True
                break

            # check fluorescence
            fluorescence = device.read_fluorescence()
            device.device_pipe.send(FluorescenceSample(fluorescence))
            if fluorescence >= multigo_settings.fluorescence_threshold:
                break
        if canceled:
            break

    # send final progress update
    device.device_pipe.send(AiProgress(10, 10))
