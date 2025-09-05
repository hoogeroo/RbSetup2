'''
hidden.py: handles showing the hidden variables
'''

from PyQt6.QtWidgets import QFormLayout

class HiddenGui:
    def __init__(self, window, variables):
        self.window = window
        self.variables = variables

        self.widgets = {}

        # use a form layout and add widgets for hidden variables
        form_layout = window.hidden_form
        for variable in self.variables:
            # skip non-hidden variables
            if not variable.hidden:
                continue

            # create the widget for the variable
            widget = variable.widget()
            widget.changed_signal().connect(self.update_hidden)
            form_layout.addRow(variable.label, widget)
            self.widgets[variable.id] = widget

    # updates the device with the values from the widgets
    def update_hidden(self):
        self.window.stages_gui.update_dc()
