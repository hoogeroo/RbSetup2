'''
gui_types.py: abstraction boilerplate for the various variable types used in gui and custom gui widgets for each variable type
'''

import numpy as np

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt

from astropy.io import fits

from value_types import *

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
        return fits.Column(name=self.id, format='3D', dim='(3)', unit=self.unit)

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

        layout = QHBoxLayout()
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
        if value.is_hold():
            self.mode_hold()
        if value.is_constant():
            self.mode_constant()
            self.checkbox.setChecked(value.constant_value())

    def changed_signal(self):
        return self.checkbox.stateChanged

class IntWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.mode_hold)
        self.addAction("Constant", self.mode_constant)

        layout = QHBoxLayout()
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
        if value.is_hold():
            self.mode_hold()
        if value.is_constant():
            self.mode_constant()
            self.spinbox.setValue(value.constant_value())

    def changed_signal(self):
        return self.spinbox.valueChanged

class FloatWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.mode_hold)
        self.addAction("Constant", self.mode_constant)
        self.addAction("Ramp", self.mode_ramp)

        layout = QHBoxLayout()
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

        self.ramp_spinbox1 = QDoubleSpinBox()
        self.ramp_spinbox1.setMinimumSize(QSize(0, 24))
        self.ramp_spinbox1.setMaximumSize(QSize(big, 24))
        self.ramp_spinbox1.setMinimum(self.variable.minimum)
        self.ramp_spinbox1.setMaximum(self.variable.maximum)
        self.ramp_spinbox1.setSingleStep(self.variable.step)
        self.ramp_spinbox1.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.ramp_spinbox1.setVisible(False)
        layout.addWidget(self.ramp_spinbox1)
        self.ramp_spinbox2 = QDoubleSpinBox()
        self.ramp_spinbox2.setMinimumSize(QSize(0, 24))
        self.ramp_spinbox2.setMaximumSize(QSize(big, 24))
        self.ramp_spinbox2.setMinimum(self.variable.minimum)
        self.ramp_spinbox2.setMaximum(self.variable.maximum)
        self.ramp_spinbox2.setSingleStep(self.variable.step)
        self.ramp_spinbox2.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.ramp_spinbox2.setVisible(False)
        layout.addWidget(self.ramp_spinbox2)

        self.setLayout(layout)

    def mode_hold(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(True)
        self.ramp_spinbox1.setVisible(False)
        self.ramp_spinbox2.setVisible(False)

    def mode_constant(self):
        self.spinbox.setVisible(True)
        self.hold_label.setVisible(False)
        self.ramp_spinbox1.setVisible(False)
        self.ramp_spinbox2.setVisible(False)

    def mode_ramp(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(False)
        self.ramp_spinbox1.setVisible(True)
        self.ramp_spinbox2.setVisible(True)

    def get_value(self):
        if self.hold_label.isVisible():
            return FloatValue.hold()
        elif self.spinbox.isVisible():
            return FloatValue.constant(self.spinbox.value())
        elif self.ramp_spinbox1.isVisible() and self.ramp_spinbox2.isVisible():
            return FloatValue.ramp(self.ramp_spinbox1.value(), self.ramp_spinbox2.value())
        else:
            raise ValueError("FloatWidget in invalid state")

    def set_value(self, value):
        if value.is_hold():
            self.mode_hold()
        if value.is_constant():
            self.mode_constant()
            self.spinbox.setValue(value.constant_value())
        if value.is_ramp():
            self.mode_ramp()
            start, end = value.ramp_values()
            self.ramp_spinbox1.setValue(start)
            self.ramp_spinbox2.setValue(end)

    def changed_signal(self):
        return self.spinbox.valueChanged
