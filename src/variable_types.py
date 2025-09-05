'''
variable_types.py: different variable types used in the GUI and sent to the device
'''

from astropy.io import fits
from scipy.interpolate import PPoly

from src.gui.value_widgets import BoolWidget, FloatWidget, IntWidget
from src.value_types import BoolValue, FloatValue, IntValue

class VariableTypeBool:
    def __init__(self, label, id, hidden=False):
        self.label = label
        self.id = id
        self.hidden = hidden
        self.value_type = BoolValue

    def widget(self):
        return BoolWidget(self)

    def fits_column(self):
        return fits.Column(name=self.id, format='2L', dim='(2)')

class VariableTypeInt:
    def __init__(self, label, id, minimum=0, maximum=100, step=1, hidden=False):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.hidden = hidden
        self.value_type = IntValue

    def widget(self):
        return IntWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='2K', dim='(2)')

class VariableTypeFloat:
    def __init__(self, label, id, minimum=0.0, maximum=1.0, step=0.1, calibration: None|PPoly=None, hidden=False):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.calibration = calibration
        self.hidden = hidden
        self.value_type = FloatValue

    def widget(self):
        return FloatWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='3D', dim='(3)')
