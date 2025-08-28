'''
simply stores classes used to send data to and from the device. kept in a separate file to avoid circular imports
'''

import numpy as np

from src.value_types import FloatValue
from src.variable_types import VariableTypeFloat

# dummy class used to represent the device's digital and analog outputs
# this class will be filled with ids set in the variables array then 
# sent to the device
class Dc:
    def __init__(self):
        pass

class Stage:
    def __init__(self, name, id, enabled):
        self.name = name
        self.id = id
        self.enabled = enabled

# same as above but for an experiment stage
class Stages:
    def __init__(self, dc, stages):
        self.dc = dc
        self.stages = stages

    def get_stage(self, id):
        for stage in self.stages:
            if stage.id == id:
                return stage
        raise ValueError(f"Stage with id {id} not found")

# represents a multigo submission
class MultiGoSubmission:
    def __init__(self, multigo_settings, stages: Stages):
        self.multigo_settings = multigo_settings
        self.stages = stages

# device settings that aren't directly related to the experiment stages or dc values
class DeviceSettings:
    def __init__(self, load_mot=False, save_runs=False):
        self.load_mot = load_mot
        self.save_runs = save_runs

# pre processed class to send to artiq
class FlattenedStages:
    def __init__(self, stages: Stages, variables):
        # initialise the variable lists with the dc value for each variable
        for i, variable in enumerate(variables):
            dc_value = getattr(stages.dc, variable.id)
            setattr(self, variable.id, [dc_value])

        # extend the lists with the stage values
        for stage in stages.stages:
            # skip the stage if it is not enabled
            if not stage.enabled:
                continue

            # get the number of samples
            samples = max(stage.samples.constant_value(), 1)

            # add values to the lists for each sample
            for sample in range(samples):
                for variable in variables:
                    # get the value and list for the variable
                    value = getattr(stage, variable.id)
                    flattened_list = getattr(self, variable.id)

                    # special case for time variable
                    if variable.id == "time":
                        flattened_list.append(value.constant_value() / samples)
                        continue

                    # if hold repeat the last value
                    if value.is_hold():
                        flattened_list.append(flattened_list[-1])
                    # if constant use the constant value
                    elif value.is_constant():
                        flattened_list.append(value.constant_value())
                    # for float ramps sample the ramp for each value
                    elif isinstance(value, FloatValue):
                        if value.is_ramp():
                            flattened_list.append(value.sample(sample, samples))

        # turn the lists into numpy arrays
        for variable in variables:
            flattened_list = getattr(self, variable.id)
            flattened_array = np.array(flattened_list)

            # apply calibration if needed
            if isinstance(variable, VariableTypeFloat):
                if variable.calibration is not None:
                    flattened_array = variable.calibration(flattened_array)

            setattr(self, variable.id, flattened_array)
