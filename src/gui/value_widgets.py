'''
value_widgets.py: widgets for each of the value types
'''

from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import *

from src.value_types import *

# Used to set the maximum size of the widgets
big = 16777215

class BoolWidget(QWidget):
    changed_signal = pyqtSignal()

    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable
        self.state = "constant"

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
        self.checkbox.stateChanged.connect(self.changed_signal.emit)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def hide(self):
        self.checkbox.setVisible(False)
        self.hold_label.setVisible(False)

    def mode_hold(self):
        self.state = "hold"
        self.hide()
        self.hold_label.setVisible(True)
        self.changed_signal.emit()

    def mode_constant(self):
        self.state = "constant"
        self.hide()
        self.checkbox.setVisible(True)
        self.changed_signal.emit()

    def get_value(self):
        if self.state == "hold":
            return BoolValue.hold()
        elif self.state == "constant":
            return BoolValue.constant(self.checkbox.isChecked())
        else:
            raise ValueError(f"BoolWidget in invalid state {self.state}")

    def set_value(self, value):
        if value.is_hold():
            self.mode_hold()
        if value.is_constant():
            self.mode_constant()
            self.checkbox.setChecked(bool(value.constant_value()))
        self.changed_signal.emit()

class IntWidget(QWidget):
    changed_signal = pyqtSignal()

    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable
        self.state = "constant"

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
        self.spinbox.valueChanged.connect(self.changed_signal.emit)
        layout.addWidget(self.spinbox)

        self.setLayout(layout)

    def hide(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(False)

    def mode_hold(self):
        self.state = "hold"
        self.hide()
        self.hold_label.setVisible(True)
        self.changed_signal.emit()

    def mode_constant(self):
        self.state = "constant"
        self.hide()
        self.spinbox.setVisible(True)
        self.changed_signal.emit()

    def get_value(self):
        if self.state == "hold":
            return IntValue.hold()
        elif self.state == "constant":
            return IntValue.constant(self.spinbox.value())
        else:
            raise ValueError(f"IntWidget in invalid state {self.state}")

    def set_value(self, value):
        if value.is_hold():
            self.mode_hold()
        if value.is_constant():
            self.mode_constant()
            self.spinbox.setValue(value.constant_value())
        self.changed_signal.emit()

class FloatWidget(QWidget):
    changed_signal = pyqtSignal()

    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable
        self.state = "constant"
        self.changed_signal.connect(self.update_color)

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
        self.spinbox.valueChanged.connect(self.changed_signal.emit)
        layout.addWidget(self.spinbox)

        self.ramp_spinbox1 = QDoubleSpinBox()
        self.ramp_spinbox1.setMinimumSize(QSize(0, 24))
        self.ramp_spinbox1.setMaximumSize(QSize(big, 24))
        self.ramp_spinbox1.setMinimum(self.variable.minimum)
        self.ramp_spinbox1.setMaximum(self.variable.maximum)
        self.ramp_spinbox1.setSingleStep(self.variable.step)
        self.ramp_spinbox1.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.ramp_spinbox1.valueChanged.connect(self.changed_signal.emit)
        self.ramp_spinbox1.setVisible(False)
        layout.addWidget(self.ramp_spinbox1)
        self.ramp_spinbox2 = QDoubleSpinBox()
        self.ramp_spinbox2.setMinimumSize(QSize(0, 24))
        self.ramp_spinbox2.setMaximumSize(QSize(big, 24))
        self.ramp_spinbox2.setMinimum(self.variable.minimum)
        self.ramp_spinbox2.setMaximum(self.variable.maximum)
        self.ramp_spinbox2.setSingleStep(self.variable.step)
        self.ramp_spinbox2.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.ramp_spinbox2.valueChanged.connect(self.changed_signal.emit)
        self.ramp_spinbox2.setVisible(False)
        layout.addWidget(self.ramp_spinbox2)

        self.setLayout(layout)

    def hide(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(False)
        self.ramp_spinbox1.setVisible(False)
        self.ramp_spinbox2.setVisible(False)

    def mode_hold(self):
        self.state = "hold"
        self.hide()
        self.hold_label.setVisible(True)
        self.changed_signal.emit()

    def mode_constant(self):
        self.state = "constant"
        self.hide()
        self.spinbox.setVisible(True)
        self.changed_signal.emit()

    def mode_ramp(self):
        self.state = "ramp"
        self.hide()
        self.ramp_spinbox1.setVisible(True)
        self.ramp_spinbox2.setVisible(True)
        self.changed_signal.emit()

    def get_value(self):
        if self.state == "hold":
            return FloatValue.hold()
        elif self.state == "constant":
            return FloatValue.constant(self.spinbox.value())
        elif self.state == "ramp":
            return FloatValue.ramp(self.ramp_spinbox1.value(), self.ramp_spinbox2.value())
        else:
            raise ValueError(f"FloatWidget in invalid state {self.state}")

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
        self.changed_signal.emit()
    
    def update_color(self):
        from matplotlib import cm

        boxes = [self.spinbox, self.ramp_spinbox1, self.ramp_spinbox2]
        for box in boxes:
            value = box.value()
            color = background_color(value, self.variable)
            box.setStyleSheet(f"background-color: {color.name()}")

def background_color(value, variable):
    from matplotlib import cm

    ratio = (value - variable.minimum) / (variable.maximum - variable.minimum)
    ratio = ratio * 0.8 + 0.1
    cmap = cm.get_cmap('berlin')
    red, green, blue, _ = [int(255 * c) for c in cmap(ratio)]
    color = QColor(red, green, blue)
    return color
