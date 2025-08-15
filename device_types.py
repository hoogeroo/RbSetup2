'''
simply stores classes used to send data to and from the device. kept in a separate file to avoid circular imports
'''

# dummy class used to represent the device's digital and analog outputs
# this class will be filled with ids set in the variables array then 
# sent to the device
class Dc:
    def __init__(self):
        pass

# same as above but for an experiment stage
class DeviceStages:
    def __init__(self):
        pass

# device settings that aren't directly related to the experiment stages or dc values
class DeviceSettings:
    def __init__(self, load_mot=False):
        self.load_mot = load_mot
