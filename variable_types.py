'''
variable_types.py: different variable types used in the GUI and sent to the device
'''

from scipy.interpolate import PPoly
from astropy.io import fits

from gui_types import BoolWidget, IntWidget, FloatWidget
from value_types import BoolValue, IntValue, FloatValue

class VariableTypeBool:
    def __init__(self, label, id):
        self.label = label
        self.id = id
        self.value_type = BoolValue

    def widget(self):
        return BoolWidget(self)

    def fits_column(self):
        return fits.Column(name=self.id, format='2L', dim='(2)')

class VariableTypeInt:
    def __init__(self, label, id, minimum=0, maximum=100, step=1):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.value_type = IntValue

    def widget(self):
        return IntWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='2K', dim='(2)')

class VariableTypeFloat:
    def __init__(self, label, id, minimum=0.0, maximum=1.0, step=0.1, unit='', calibration: None|PPoly=None):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.unit = unit
        self.calibration = calibration
        self.value_type = FloatValue

    def widget(self):
        return FloatWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='3D', dim='(3)', unit=self.unit)
