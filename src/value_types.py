'''
value_types.py: contains abstractions over the different variable types used by the device with interpolation settings built in
'''

import numpy as np
import astropy.io.fits as fits

class BoolValue:
    def __init__(self):
        self.array = np.zeros(2, dtype=np.bool_)
    
    def __repr__(self):
        if self.is_hold():
            return "Hold"
        elif self.is_constant():
            return f"{self.constant_value()}"
        else:
            raise ValueError("unreachable")

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

    def interpolate(self, end, steps):
        raise ValueError("Cannot interpolate boolean values")

class IntValue:
    def __init__(self):
        self.array = np.zeros(2, dtype=np.int64)

    def __repr__(self):
        if self.is_hold():
            return "Hold"
        elif self.is_constant():
            return f"{self.constant_value()}"
        else:
            raise ValueError("unreachable")

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

    def interpolate(self, end, steps):
        if not self.is_constant():
            raise ValueError("Can't interpolate non-constant values")
        if not end.is_constant():
            raise ValueError("Can't interpolate to a non-constant value")
        start = self.constant_value()
        end = end.constant_value()
        values = np.linspace(start, end, steps, dtype=np.int64)
        output = []
        for value in values:
            output.append(IntValue.constant(value))
        return output

class FloatValue:
    def __init__(self):
        self.array = np.zeros(3, dtype=np.float64)

    def __repr__(self):
        if self.is_hold():
            return "Hold"
        elif self.is_constant():
            return f"{self.constant_value()}"
        elif self.is_ramp():
            start, end = self.ramp_values()
            mode = self.ramp_mode()
            if mode == 'exponential':
                return f"({start} -> {end} [exp])"
            return f"({start} -> {end})"
        else:
            raise ValueError("unreachable")

    def to_array(self):
        return self.array

    def from_array(array):
        if array.shape != (3,):
            raise ValueError("Array must have shape (3,)")
        if not np.issubdtype(array.dtype, np.floating):
            raise ValueError("Array must be of floating point type")
        # accept linear (2.0) and exponential (3.0) ramp codes
        if array[0] not in (0.0, 1.0, 2.0, 3.0):
            raise ValueError("First element of array must be 0.0 (hold), 1.0 (constant), 2.0 (ramp linear) or 3.0 (ramp exponential)")
        value = FloatValue()
        value.array = array
        return value

    def set_hold(self):
        self.array[0] = 0.0
        self.array[1] = 0.0

    def set_constant(self, value):
        self.array[0] = 1.0
        self.array[1] = value

    def set_ramp(self, start, end, mode='linear'):
        # mode: 'linear' or 'exponential'
        code = 2.0 if mode == 'linear' else 3.0
        self.array[0] = code
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

    def ramp(start, end, mode='linear'):
        float_value = FloatValue()
        float_value.set_ramp(start, end, mode=mode)
        return float_value

    def is_hold(self):
        return self.array[0] == 0.0

    def is_constant(self):
        return self.array[0] == 1.0

    def is_ramp(self):
        return self.array[0] in (2.0, 3.0)

    def ramp_mode(self):
        if not self.is_ramp():
            raise ValueError("Value is not a ramp")
        return 'linear' if self.array[0] == 2.0 else 'exponential'

    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]

    def ramp_values(self):
        if not self.is_ramp():
            raise ValueError("Value is not a ramp")
        return self.array[1], self.array[2]

    # samples values in a float ramp
    def sample(self, step, samples):
        if self.is_hold():
            raise ValueError("Cannot sample a hold value")
        if self.is_constant():
            return self.constant_value()
        if self.is_ramp():
            start, end = self.array[1], self.array[2]
            if samples <= 1:
                return start
            t = step / (samples - 1)
            if self.ramp_mode() == 'linear':
                return start + (end - start) * t
            # exponential (assume positive start/end): geometric interpolation
            return start * (end / start) ** t
        else:
            raise ValueError("unreachable")

    def interpolate(self, end, steps):
        if self.is_hold():
            raise ValueError("Can't interpolate from a hold value")
        if end.is_hold():
            raise ValueError("Can't interpolate to a hold value")
        if self.is_constant() and end.is_constant():
            start = self.constant_value()
            endv = end.constant_value()
            values = np.linspace(start, endv, steps)
            output = []
            for value in values:
                output.append(FloatValue.constant(value))
            return output
        if self.is_ramp() and end.is_ramp():
            start1, end1 = self.ramp_values()
            start2, end2 = end.ramp_values()
            values1 = np.linspace(start1, end1, steps)
            values2 = np.linspace(start2, end2, steps)
            output = []
            mode = self.ramp_mode()
            for i in range(steps):
                output.append(FloatValue.ramp(values1[i], values2[i], mode=mode))
            return output

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
