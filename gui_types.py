import numpy as np

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt

from astropy.io import fits

# Used to set the maximum size of the widgets
big = 16777215

'''
variable types for the GUI
'''

class VariableTypeBool:
    def __init__(self, label, id):
        self.label = label
        self.id = id
        self.value_type = BoolValue

    def widget(self) -> QCheckBox:
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
        self.unit = unit
        self.value_type = IntValue

    def widget(self):
        return IntWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='2K', dim='(2)')

class VariableTypeFloat:
    def __init__(self, label, id, minimum=0.0, maximum=1.0, step=0.1, unit=''):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.unit = unit
        self.value_type = FloatValue

    def widget(self):
        return FloatWidget(self)
    
    def fits_column(self):
        return fits.Column(name=self.id, format='2D', dim='(2)', unit=self.unit)

'''
custom widgets for the GUI
'''

class BoolWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.mode_hold)
        self.addAction("Constant", self.mode_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        self.hold_label.setVisible(False)
        layout.addWidget(self.hold_label)

        self.checkbox = QCheckBox()
        self.checkbox.setMinimumSize(QSize(0, 24))
        self.checkbox.setMaximumSize(QSize(big, 24))
        self.checkbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def mode_hold(self):
        self.checkbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def mode_constant(self):
        self.checkbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.hold_label.isVisible():
            return BoolValue.hold()
        else:
            return BoolValue.constant(self.checkbox.isChecked())

    def set_value(self, value):
        if value.is_constant():
            self.checkbox.setChecked(value.constant_value())
            self.checkbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif value.is_hold():
            self.checkbox.setVisible(False)
            self.hold_label.setVisible(True)

    def changed_signal(self):
        return self.checkbox.stateChanged

class IntWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.mode_hold)
        self.addAction("Constant", self.mode_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        self.hold_label.setVisible(False)
        layout.addWidget(self.hold_label)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimumSize(QSize(0, 24))
        self.spinbox.setMaximumSize(QSize(big, 24))
        self.spinbox.setMinimum(variable.minimum)
        self.spinbox.setMaximum(variable.maximum)
        self.spinbox.setSingleStep(variable.step)
        self.spinbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        layout.addWidget(self.spinbox)

        self.setLayout(layout)

    def mode_hold(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def mode_constant(self):
        self.spinbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.hold_label.isVisible():
            return IntValue.hold()
        else:
            return IntValue.constant(self.spinbox.value())

    def set_value(self, value):
        if value.is_constant():
            self.spinbox.setValue(value.constant_value())
            self.spinbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif value.is_hold():
            self.spinbox.setVisible(False)
            self.hold_label.setVisible(True)

    def changed_signal(self):
        return self.spinbox.valueChanged

class FloatWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.mode_hold)
        self.addAction("Constant", self.mode_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        self.hold_label.setVisible(False)
        layout.addWidget(self.hold_label)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimumSize(QSize(0, 24))
        self.spinbox.setMaximumSize(QSize(big, 24))
        self.spinbox.setMinimum(self.variable.minimum)
        self.spinbox.setMaximum(self.variable.maximum)
        self.spinbox.setSingleStep(self.variable.step)
        self.spinbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        layout.addWidget(self.spinbox)

        self.setLayout(layout)

    def mode_hold(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def mode_constant(self):
        self.spinbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.hold_label.isVisible():
            return FloatValue.hold()
        else:
            return FloatValue.constant(self.spinbox.value())

    def set_value(self, value):
        if value.is_constant():
            self.spinbox.setValue(value.constant_value())
            self.spinbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif value.is_hold():
            self.spinbox.setVisible(False)
            self.hold_label.setVisible(True)

    def changed_signal(self):
        return self.spinbox.valueChanged

'''
value types for the GUI
'''

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
        self.array = np.zeros(2, dtype=np.float64)

    def to_array(self):
        return self.array
    
    def from_array(array):
        if array.shape != (2,):
            raise ValueError("Array must have shape (2,)")
        if not np.issubdtype(array.dtype, np.floating):
            raise ValueError("Array must be of floating point type")
        if array[0] not in (0.0, 1.0):
            raise ValueError("First element of array must be 0.0 (hold) or 1.0 (constant)")
        value = FloatValue()
        value.array = array
        return value

    def set_hold(self):
        self.array[0] = 0.0
        self.array[1] = 0.0

    def set_constant(self, value):
        self.array[0] = 1.0
        self.array[1] = value
    
    def hold():
        value = FloatValue()
        value.set_hold()
        return value

    def constant(value):
        float_value = FloatValue()
        float_value.set_constant(value)
        return float_value

    def is_hold(self):
        return self.array[0] == 0.0

    def is_constant(self):
        return self.array[0] == 1.0

    def constant_value(self):
        if not self.is_constant():
            raise ValueError("Value is not constant")
        return self.array[1]
