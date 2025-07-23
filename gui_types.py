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
            return BoolHold()
        else:
            return BoolConstant(self.checkbox.isChecked())
    
    def set_value(self, value):
        if isinstance(value, BoolConstant):
            self.checkbox.setChecked(value.value)
            self.checkbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif isinstance(value, BoolHold):
            self.checkbox.setVisible(False)
            self.hold_label.setVisible(True)
        else:
            raise ValueError("Invalid value type for BoolWidget")

    def changed_signal(self):
        return self.checkbox.stateChanged

    def to_fits(self):
        value = self.get_value()
        output = np.zeros(2, dtype=np.bool_)
        if isinstance(value, BoolConstant):
            output[0] = True
            output[1] = value.value
        return output
    
    def from_fits(self, fits_data):
        if fits_data[0]:
            self.set_value(BoolConstant(fits_data[1]))
        elif not fits_data[0]:
            self.set_value(BoolHold())
        else:
            raise ValueError("Invalid FITS data for BoolWidget")

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
            return IntHold()
        else:
            return IntConstant(self.spinbox.value())

    def set_value(self, value):
        if isinstance(value, IntConstant):
            self.spinbox.setValue(value.value)
            self.spinbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif isinstance(value, IntHold):
            self.spinbox.setVisible(False)
            self.hold_label.setVisible(True)
        else:
            raise ValueError("Invalid value type for IntWidget")

    def changed_signal(self):
        return self.spinbox.valueChanged

    def to_fits(self):
        value = self.get_value()
        output = np.zeros(2, dtype=np.int32)
        if isinstance(value, IntConstant):
            output[0] = 1
            output[1] = value.value
        return output

    def from_fits(self, fits_data):
        if fits_data[0] == 1:
            self.set_value(IntConstant(fits_data[1]))
        elif fits_data[0] == 0:
            self.set_value(IntHold())
        else:
            raise ValueError("Invalid FITS data for IntWidget")

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
            return FloatHold()
        else:
            return FloatConstant(self.spinbox.value())

    def set_value(self, value):
        if isinstance(value, FloatConstant):
            self.spinbox.setValue(value.value)
            self.spinbox.setVisible(True)
            self.hold_label.setVisible(False)
        elif isinstance(value, FloatHold):
            self.spinbox.setVisible(False)
            self.hold_label.setVisible(True)
        else:
            raise ValueError("Invalid value type for FloatWidget")

    def changed_signal(self):
        return self.spinbox.valueChanged
    
    def to_fits(self):
        value = self.get_value()
        output = np.zeros(2, dtype=np.float64)
        if isinstance(value, FloatConstant):
            output[0] = 1.0
            output[1] = value.value
        return output
    
    def from_fits(self, fits_data):
        if fits_data[0] == 1.0:
            self.set_value(FloatConstant(fits_data[1]))
        elif fits_data[0] == 0.0:
            self.set_value(FloatHold())
        else:
            raise ValueError("Invalid FITS data for FloatWidget")

'''
value types for the GUI
'''

class BoolHold:
    pass

class BoolConstant:
    def __init__(self, value):
        self.value = value

class IntHold:
    pass

class IntConstant:
    def __init__(self, value):
        self.value = value

class FloatHold:
    pass

class FloatConstant:
    def __init__(self, value):
        self.value = value
