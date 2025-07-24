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
