'''
value_types.py: contains abstractions over the different variable types used by the device with interpolation settings built in
'''

import numpy as np
import astropy.io.fits as fits

class BoolValue:
    def __init__(self):
        self.array = np.zeros(2, dtype=np.bool_)

    def to_array(self):
        return self.array

    def from_array(array):
        if array.shape != (2,):
            raise ValueError("Array must have shape (2,)")
        if not np.issubdtype(array.dtype, np.bool_):
            raise ValueError("Array must be of boolean type")
        if array[0] not in (False, True):
            raise ValueError("First element of array must be False (hold) or True (constant)")
        value = BoolValue()
        value.array = array
        return value

    def set_hold(self):
        self.array[0] = False
        self.array[1] = False

    def set_constant(self, value):
        self.array[0] = True
        self.array[1] = value

    def hold():
        value = BoolValue()
        value.set_hold()
        return value

    def constant(value):
        bool_value = BoolValue()
        bool_value.set_constant(value)
        return bool_value

    def is_hold(self):
        return self.array[0] == False

    def is_constant(self):
        return self.array[0] == True

    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

class IntValue:
    def __init__(self):
        self.array = np.zeros(2, dtype=np.int64)

    def to_array(self):
        return self.array

    def from_array(array):
        if array.shape != (2,):
            raise ValueError("Array must have shape (2,)")
        if not np.issubdtype(array.dtype, np.integer):
            raise ValueError("Array must be of integer type")
        if array[0] not in (0, 1):
            raise ValueError("First element of array must be 0 (hold) or 1 (constant)")
        value = IntValue()
        value.array = array
        return value

    def set_hold(self):
        self.array[0] = 0
        self.array[1] = 0

    def set_constant(self, value):
        self.array[0] = 1
        self.array[1] = value

    def hold():
        value = IntValue()
        value.set_hold()
        return value

    def constant(value):
        int_value = IntValue()
        int_value.set_constant(value)
        return int_value

    def is_hold(self):
        return self.array[0] == 0

    def is_constant(self):
        return self.array[0] == 1

    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

class FloatValue:
    def __init__(self):
        self.array = np.zeros(3, dtype=np.float64)

    def to_array(self):
        return self.array

    def from_array(array):
        if array.shape != (3,):
            raise ValueError("Array must have shape (3,)")
        if not np.issubdtype(array.dtype, np.floating):
            raise ValueError("Array must be of floating point type")
        if array[0] not in (0.0, 1.0, 2.0):
            raise ValueError("First element of array must be 0.0 (hold), 1.0 (constant) or 2.0 (ramp)")
        value = FloatValue()
        value.array = array
        return value

    def set_hold(self):
        self.array[0] = 0.0
        self.array[1] = 0.0

    def set_constant(self, value):
        self.array[0] = 1.0
        self.array[1] = value

    def set_ramp(self, start, end):
        self.array[0] = 2.0
        self.array[1] = start
        self.array[2] = end

    def hold():
        value = FloatValue()
        value.set_hold()
        return value

    def constant(value):
        float_value = FloatValue()
        float_value.set_constant(value)
        return float_value

    def ramp(start, end):
        float_value = FloatValue()
        float_value.set_ramp(start, end)
        return float_value

    def is_hold(self):
        return self.array[0] == 0.0

    def is_constant(self):
        return self.array[0] == 1.0

    def is_ramp(self):
        return self.array[0] == 2.0

    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

    def ramp_values(self):
        if not self.is_ramp():
            raise ValueError("Value is not a ramp")
        return self.array[1], self.array[2]

    def sample(self, step, samples):
        if self.is_hold():
            raise ValueError("Cannot sample a hold value")
        if self.is_constant():
            return self.constant_value()
        if self.is_ramp():
            start, end = self.array[1], self.array[2]
            if samples <= 1:
                return start
            return start + (end - start) * step / (samples - 1)
        else:
            raise ValueError("unreachable")

# used for storing any type of value
class AnyValue:
    def __init__(self, value=None):
        self.array = np.zeros(4)
        if value:
            if isinstance(value, BoolValue):
                self.array[0] = 0.0
                self.array[1:] = value.to_array()
            elif isinstance(value, IntValue):
                self.array[0] = 1.0
                self.array[1:] = value.to_array()
            elif isinstance(value, FloatValue):
                self.array[0] = 2.0
                self.array[1:] = value.to_array()
            else:
                raise ValueError("Unsupported value type")

    def to_array(self):
        return self.array

    def from_array(array):
        if array.shape != (4,):
            raise ValueError("Array must have shape (4,)")
        if not np.issubdtype(array.dtype, np.floating):
            raise ValueError("Array must be of floating point type")
        if array[0] not in (0.0, 1.0, 2.0):
            raise ValueError("First element of array must be 0.0 (hold), 1.0 (constant) or 2.0 (ramp)")
        value = AnyValue()
        value.array = array
        return value

    def to_value(self):
        if self.is_bool():
            return BoolValue.from_array(self.array[1:])
        elif self.is_int():
            return IntValue.from_array(self.array[1:])
        elif self.is_float():
            return FloatValue.from_array(self.array[1:])
        else:
            raise ValueError("Unknown value type")

    def is_bool(self):
        return self.array[0] == 0.0

    def is_int(self):
        return self.array[0] == 1.0

    def is_float(self):
        return self.array[0] == 2.0

    def fits_column(self, name):
        return fits.Column(name=name, format='E', array=self.array[1:])
