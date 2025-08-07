'''
value_types.py: contains abstractions over the different variable types used by the device with interpolation settings built in
'''

import numpy as np

# optionally import portable decorator for so this works without artiq
try:
    from artiq.experiment import portable
except ImportError:
    def portable(func):
        return func

class BoolValue:
    @portable
    def __init__(self):
        self.array = np.zeros(2, dtype=np.bool_)

    @portable
    def to_array(self):
        return self.array

    @portable
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

    @portable
    def set_hold(self):
        self.array[0] = False
        self.array[1] = False

    @portable
    def set_constant(self, value):
        self.array[0] = True
        self.array[1] = value

    @portable
    def hold():
        value = BoolValue()
        value.set_hold()
        return value

    @portable
    def constant(value):
        bool_value = BoolValue()
        bool_value.set_constant(value)
        return bool_value

    @portable
    def is_hold(self):
        return self.array[0] == False

    @portable
    def is_constant(self):
        return self.array[0] == True

    @portable
    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

class IntValue:
    @portable
    def __init__(self):
        self.array = np.zeros(2, dtype=np.int64)

    @portable
    def to_array(self):
        return self.array

    @portable
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

    @portable
    def set_hold(self):
        self.array[0] = 0
        self.array[1] = 0

    @portable
    def set_constant(self, value):
        self.array[0] = 1
        self.array[1] = value

    @portable
    def hold():
        value = IntValue()
        value.set_hold()
        return value

    @portable
    def constant(value):
        int_value = IntValue()
        int_value.set_constant(value)
        return int_value

    @portable
    def is_hold(self):
        return self.array[0] == 0

    @portable
    def is_constant(self):
        return self.array[0] == 1

    @portable
    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

class FloatValue:
    @portable
    def __init__(self):
        self.array = np.zeros(3, dtype=np.float64)

    @portable
    def to_array(self):
        return self.array

    @portable
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

    @portable
    def set_hold(self):
        self.array[0] = 0.0
        self.array[1] = 0.0

    @portable
    def set_constant(self, value):
        self.array[0] = 1.0
        self.array[1] = value

    @portable
    def set_ramp(self, start, end):
        self.array[0] = 2.0
        self.array[1] = start
        self.array[2] = end

    @portable
    def hold():
        value = FloatValue()
        value.set_hold()
        return value

    @portable
    def constant(value):
        float_value = FloatValue()
        float_value.set_constant(value)
        return float_value

    @portable
    def ramp(start, end):
        float_value = FloatValue()
        float_value.set_ramp(start, end)
        return float_value

    @portable
    def is_hold(self):
        return self.array[0] == 0.0

    @portable
    def is_constant(self):
        return self.array[0] == 1.0

    @portable
    def is_ramp(self):
        return self.array[0] == 2.0

    @portable
    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

    @portable
    def ramp_values(self):
        if not self.is_ramp():
            raise ValueError("Value is not a ramp")
        return self.array[1], self.array[2]
