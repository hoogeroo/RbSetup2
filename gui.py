from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSize
from PyQt6.uic import loadUi

class Gui(QMainWindow):
    def __init__(self, device):
        super(Gui, self).__init__()
        self.device = device

        # to see what this does you can run `pyuic6 gui.ui | code -`
        loadUi('gui.ui', self)
        
        # big number for maximum size
        big = 16777215

        # create column container for each stage
        stages = self.device.stages
        stage_containers = []
        for i in range(stages):
            stage = QVBoxLayout()
            self.stages_container.addLayout(stage)
            stage_containers.append(stage)

            # create a button for each stage
            button = QPushButton()
            button.setText(f"Stage {i + 1}")
            button.setMinimumSize(QSize(0, 24))
            button.setMaximumSize(QSize(big, 24))
            stage.addWidget(button)

        # add spacers to the dc, label, and copied containers
        spacers = []
        for i in range(3):
            label = QLabel()
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            spacers.append(label)
        self.dc_container.addWidget(spacers[0])
        self.label_container.addWidget(spacers[1])
        self.copied_container.addWidget(spacers[2])

        # create widgets for each variable and add them to the layout
        for i, variable in enumerate(self.device.variables):
            # have to create each widget separately as widgets cannot be cloned
            widgets = []
            for j in range(self.device.stages + 1):
                if isinstance(variable, VariableTypeBool):
                    widget = QCheckBox()
                    widget.setMinimumSize(QSize(0, 24))
                    widget.setMaximumSize(QSize(big, 24))
                    widgets.append(widget)
                elif isinstance(variable, VariableTypeFloat):
                    widget = QDoubleSpinBox()
                    widget.setMinimumSize(QSize(0, 24))
                    widget.setMaximumSize(QSize(big, 24))
                    widget.setMinimum(variable.minimum)
                    widget.setMaximum(variable.maximum)
                    widget.setSingleStep(variable.step)
                    widgets.append(widget)
                else:
                    raise ValueError(f"Unknown variable type: {type(variable)}")
            
            # add the widgets to the stage containers
            for (i, stage) in enumerate(stage_containers):
                stage.addWidget(widgets[i])

            # add the widget to the dc container
            self.dc_container.addWidget(widgets[stages])

            # add the label to the label container
            label = QLabel()
            label.setText(variable.label)
            label.setMinimumSize(QSize(0, 24))
            label.setMaximumSize(QSize(big, 24))
            self.label_container.addWidget(label)
        
        # add strech to containers
        self.dc_container.addStretch()
        self.label_container.addStretch()
        self.copied_container.addStretch()
        for stage in stage_containers:
            stage.addStretch()


    def update_dc(self):
        for var in self.gui_variables:
            setattr(self.device, var, getattr(self, var).value())

        print("Updating device with:")

        self.device.update_dc()

class VariableTypeBool:
    def __init__(self, label):
        self.label = label

class VariableTypeFloat:
    def __init__(self, label, minimum=0.0, maximum=1.0, step=0.1):
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
