'''
multigo.py: has the code for running multigo experiments
'''

from src.device.device_types import Stages
from src.gui.plots import FluorescenceSample

class MultiGoSettings:
    def __init__(self, run_variables, fluorescence_threshold):
        self.run_variables = run_variables
        self.fluorescence_threshold = fluorescence_threshold

# class for sending multigo progress updates from device to gui
class MultiGoProgress:
    def __init__(self, current_step, total_steps):
        self.current_step = current_step
        self.total_steps = total_steps

# class for cancelling multigo, sent from gui to device
class MultiGoCancel:
    pass

# runs a multigo experiment 
def run_multigo_experiment(device, multigo_settings: MultiGoSettings, stages: Stages):
    run_variables = multigo_settings.run_variables
    fluorescence_threshold = multigo_settings.fluorescence_threshold

    values = []

    # create array of all the values that need to be interpolated
    total_runs = 1
    for var in run_variables:
        array = var.start.interpolate(var.end, var.steps)
        values.append(array)
        total_runs *= len(array)

    # loop over all combinations
    indices = [0] * len(values)
    while True:
        # get what step of multigo we are at
        current = 0
        place = 1
        for i, index in enumerate(indices):
            current += index * place
            place *= len(values[i])
        assert(total_runs == place)
        progress = MultiGoProgress(current, total_runs)
        device.device_pipe.send(progress)

        # update stages to the current state
        for i, index in enumerate(indices):
            stage_id = run_variables[i].stage_id
            variable_id = run_variables[i].variable_id
            stage = stages.get_stage(stage_id)
            setattr(stage, variable_id, values[i][index])

        # wait for fluorescence
        canceled = False
        while True:
            # wait for cancellation for 100ms
            if device.device_pipe.poll(0.1):
                msg = device.device_pipe.recv()
                if not isinstance(msg, MultiGoCancel):
                    print(f"Received weird message during multigo: {type(msg)}")
                canceled = True
                break

            # check fluorescence
            fluorescence = device.read_fluorescence()
            device.device_pipe.send(FluorescenceSample(fluorescence))
            if fluorescence >= fluorescence_threshold:
                break
        if canceled:
            break

        # run the experiment
        device.run_experiment(stages)

        # update the indices
        done = False
        for i, index in enumerate(indices):
            if index < len(values[i]) - 1:
                indices[i] += 1
                break
            if i == len(indices) - 1:
                done = True
                break
            indices[i] = 0

        # exit if done
        if done:
            break

    # send final progress update
    device.device_pipe.send(MultiGoProgress(total_runs, total_runs))
