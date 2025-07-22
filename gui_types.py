from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize, Qt

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

class VariableTypeInt:
    def __init__(self, label, id, minimum=0, maximum=100, step=1):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def widget(self):
        return IntWidget(self)

class VariableTypeFloat:
    def __init__(self, label, id, minimum=0.0, maximum=1.0, step=0.1):
        self.label = label
        self.id = id
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def widget(self):
        return FloatWidget(self)

'''
custom widgets for the GUI
'''

class BoolWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.set_hold)
        self.addAction("Constant", self.set_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        layout.addWidget(self.hold_label)

        self.checkbox = QCheckBox()
        self.checkbox.setMinimumSize(QSize(0, 24))
        self.checkbox.setMaximumSize(QSize(big, 24))
        self.checkbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.checkbox.setVisible(False)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def set_hold(self):
        self.checkbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def set_constant(self):
        self.checkbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.checkbox.isVisible():
            return BoolConstant(self.checkbox.isChecked())
        else:
            return BoolHold()
    
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

class IntWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.set_hold)
        self.addAction("Constant", self.set_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        layout.addWidget(self.hold_label)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimumSize(QSize(0, 24))
        self.spinbox.setMaximumSize(QSize(big, 24))
        self.spinbox.setMinimum(variable.minimum)
        self.spinbox.setMaximum(variable.maximum)
        self.spinbox.setSingleStep(variable.step)
        self.spinbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.spinbox.setVisible(False)
        layout.addWidget(self.spinbox)

        self.setLayout(layout)

    def set_hold(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def set_constant(self):
        self.spinbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.spinbox.isVisible():
            return IntConstant(self.spinbox.value())
        else:
            return IntHold()

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

class FloatWidget(QWidget):
    def __init__(self, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.variable = variable

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction("Hold", self.set_hold)
        self.addAction("Constant", self.set_constant)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.hold_label = QLabel("Hold")
        self.hold_label.setText("Hold")
        self.hold_label.setMinimumSize(QSize(0, 24))
        self.hold_label.setMaximumSize(QSize(big, 24))
        layout.addWidget(self.hold_label)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimumSize(QSize(0, 24))
        self.spinbox.setMaximumSize(QSize(big, 24))
        self.spinbox.setMinimum(self.variable.minimum)
        self.spinbox.setMaximum(self.variable.maximum)
        self.spinbox.setSingleStep(self.variable.step)
        self.spinbox.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.spinbox.setVisible(False)
        layout.addWidget(self.spinbox)

        self.setLayout(layout)

    def set_hold(self):
        self.spinbox.setVisible(False)
        self.hold_label.setVisible(True)
    
    def set_constant(self):
        self.spinbox.setVisible(True)
        self.hold_label.setVisible(False)

    def get_value(self):
        if self.spinbox.isVisible():
            return FloatConstant(self.spinbox.value())
        else:
            return FloatHold()

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
