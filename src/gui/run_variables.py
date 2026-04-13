'''
run_variables.py: widget for adding and removing run variables, used by multigo and ai
'''

from PyQt6.QtWidgets import *
from src.variable_types import VariableTypeFloat

# stores a run variable (constant or ramp sweep)
class RunVariable:
    def __init__(self, stage_id, variable_id, start, end, steps,
                 is_ramp=False, ramp_start_start=0.0, ramp_start_end=0.0,
                 ramp_end_start=0.0, ramp_end_end=0.0, ramp_mode='linear'):
        self.stage_id = stage_id
        self.variable_id = variable_id
        # constant sweep (is_ramp=False)
        self.start = start
        self.end = end
        self.steps = steps
        # ramp sweep (is_ramp=True, float variables only)
        self.is_ramp = is_ramp
        self.ramp_start_start = ramp_start_start
        self.ramp_start_end = ramp_start_end
        self.ramp_end_start = ramp_end_start
        self.ramp_end_end = ramp_end_end
        self.ramp_mode = ramp_mode

    # Used to exclude qt references from pickling when saving run variables 
    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __setstate__(self, state):
        self.__dict__.update(state)

# custom widget for adding run_variables
class RunVariableWidget(QWidget):
    def __init__(self, stages, steps=True):
        super().__init__()

        self.stages = stages
        self.run_variables = []
        self.steps = steps
        self.button_column = 5 - int(not steps)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # add save/load buttons
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_dialog)
        self.grid.addWidget(save_button, 0, 0)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_dialog)
        self.grid.addWidget(load_button, 0, 1)

        # stage selection
        stage_dropdown = QComboBox()
        stage_dropdown.addItem('DC Value')
        for stage in self.stages.stages:
            stage_dropdown.addItem(stage.label())
        self.grid.addWidget(stage_dropdown, 1, 0)

        # variable selection
        variable_dropdown = QComboBox()
        for variable in self.stages.variables:
            variable_dropdown.addItem(variable.label)
        self.grid.addWidget(variable_dropdown, 1, 1)

        # labels
        self.grid.addWidget(QLabel("Start"), 1, 2)
        self.grid.addWidget(QLabel("End"), 1, 3)
        if steps:
            self.grid.addWidget(QLabel("Steps"), 1, 4)

        # add add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.new_run_variable(stage_dropdown.currentIndex(), variable_dropdown.currentIndex()))
        self.grid.addWidget(add_button, 1, self.button_column)

    # gets the currently selected run variables
    def get_run_variables(self):
        run_variables = []
        for rv in self.run_variables:
            # read current widget values into the RunVariable
            if hasattr(rv, '_ramp_cb') and rv._ramp_cb.isChecked():
                run_variables.append(RunVariable(
                    rv.stage_id, rv.variable_id, 
                    rv._start_w.get_value(), rv._end_w.get_value(),
                    rv._steps_w.value() if self.steps else rv.steps,
                    is_ramp = True,
                    ramp_start_start = rv._ramp_start_from.value(),
                    ramp_start_end = rv._ramp_start_to.value(),
                    ramp_end_start = rv._ramp_end_from.value(),
                    ramp_end_end = rv._ramp_end_to.value(),
                    ramp_mode = rv._ramp_mode_combo.currentText(),
                ))
            else:
                run_variables.append(RunVariable(
                    rv.stage_id, rv.variable_id,
                    rv._start_w.get_value(), rv._end_w.get_value(),
                    rv._steps_w.value() if self.steps else rv.steps,
                    is_ramp = False
                ))
        return run_variables
    
    @staticmethod
    def _ramp_to_constant(value):
        if hasattr(value, 'is_ramp') and value.is_ramp():
            _, end = value.ramp_values()
            return value.__class__.constant(end)
        return value

    # create a new run variable
    def new_run_variable(self, idx, variable):
        variable = self.stages.variables[variable]
        if variable.hidden:
            widget = self.stages.hidden_gui.widgets[variable.id]
            current_value = self._ramp_to_constant(widget.get_value())
            run_variable = RunVariable(
                #self.stages.hidden_gui.widgets[variable.id],
                'dc',
                variable.id,
                current_value,
                current_value,
                0
            )
        else:
            if idx==0:
                widget = self.stages.dc_widgets[variable.id]
                current_value = self._ramp_to_constant(widget.get_value())
                run_variable = RunVariable(
                    #self.stages.dc_widgets[variable.id],
                    'dc',
                    variable.id,
                    current_value,
                    current_value,
                    0
                )
            else:
                #print(variable.id)
                widget = self.stages.stages[idx-1].widgets[variable.id]
                current_value = self._ramp_to_constant(widget.get_value())
                run_variable = RunVariable(
                    self.stages.stages[idx-1].id,
                    variable.id,
                    current_value,
                    current_value,
                    0
                )
        self.add_run_variable(run_variable)

    # helper: build a labelled from→to range widget for ramp sweeps
    def _make_ramp_range(self, variable, label_text, from_val, to_val):
        container = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        container.setLayout(vbox)
        vbox.addWidget(QLabel(label_text))
        hbox = QHBoxLayout()
        from_spin = QDoubleSpinBox()
        from_spin.setMinimum(variable.minimum)
        from_spin.setMaximum(variable.maximum)
        from_spin.setSingleStep(variable.step)
        from_spin.setValue(from_val)
        to_spin = QDoubleSpinBox()
        to_spin.setMinimum(variable.minimum)
        to_spin.setMaximum(variable.maximum)
        to_spin.setSingleStep(variable.step)
        to_spin.setValue(to_val)
        hbox.addWidget(from_spin)
        hbox.addWidget(QLabel("→"))
        hbox.addWidget(to_spin)
        vbox.addLayout(hbox)
        return container, from_spin, to_spin

    # add a run variable row to the grid
    def add_run_variable(self, run_variable):
        row = self.grid.rowCount()
        _, variable = self.stages.get_variable(run_variable.variable_id)
        is_float = isinstance(variable, VariableTypeFloat)

        # col 0: stage label
        try:
            stage = self.stages.get_stage(run_variable.stage_id)
            self.grid.addWidget(QLabel(stage.label()), row, 0)
        except Exception:
            self.grid.addWidget(QLabel('DC Value'), row, 0)

        # col 1: variable label + optional ramp checkbox / mode
        label_box = QWidget()
        label_lay = QVBoxLayout()
        label_lay.setContentsMargins(0, 0, 0, 0)
        label_box.setLayout(label_lay)
        label_lay.addWidget(QLabel(variable.label))
        if is_float:
            ramp_cb = QCheckBox("Ramp")
            label_lay.addWidget(ramp_cb)
            ramp_mode = QComboBox()
            ramp_mode.addItems(["linear", "exponential"])
            ramp_mode.setCurrentText(run_variable.ramp_mode)
            ramp_mode.setVisible(run_variable.is_ramp)
            label_lay.addWidget(ramp_mode)
            run_variable._ramp_cb = ramp_cb
            run_variable._ramp_mode_combo = ramp_mode
        self.grid.addWidget(label_box, row, 1)

        # col 2 & 3: start / end value widgets
        start_w = variable.widget()
        start_w.set_value(run_variable.start)
        end_w = variable.widget()
        end_w.set_value(run_variable.end)
        run_variable._start_w = start_w
        run_variable._end_w = end_w

        if is_float:
            # stacked widget: page 0 = constant, page 1 = ramp
            start_stack = QStackedWidget()
            start_stack.addWidget(start_w)
            rs_container, rs_from, rs_to = self._make_ramp_range(
                variable, "Ramp Start", run_variable.ramp_start_start, run_variable.ramp_start_end)
            start_stack.addWidget(rs_container)
            self.grid.addWidget(start_stack, row, 2)

            end_stack = QStackedWidget()
            end_stack.addWidget(end_w)
            re_container, re_from, re_to = self._make_ramp_range(
                variable, "Ramp End", run_variable.ramp_end_start, run_variable.ramp_end_end)
            end_stack.addWidget(re_container)
            self.grid.addWidget(end_stack, row, 3)

            run_variable._ramp_start_from = rs_from
            run_variable._ramp_start_to = rs_to
            run_variable._ramp_end_from = re_from
            run_variable._ramp_end_to = re_to

            def toggle_ramp(checked, ss=start_stack, es=end_stack, rm=ramp_mode):
                ss.setCurrentIndex(1 if checked else 0)
                es.setCurrentIndex(1 if checked else 0)
                rm.setVisible(checked)
            ramp_cb.toggled.connect(toggle_ramp)
            if run_variable.is_ramp:
                ramp_cb.setChecked(True)
        else:
            self.grid.addWidget(start_w, row, 2)
            self.grid.addWidget(end_w, row, 3)

        # col 4: steps (optional)
        if self.steps:
            steps_w = QSpinBox()
            steps_w.setMinimum(1)
            steps_w.setValue(run_variable.steps)
            self.grid.addWidget(steps_w, row, 4)
            run_variable._steps_w = steps_w

        # col 5: remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda _, rv=run_variable: self._remove(rv))
        self.grid.addWidget(remove_btn, row, self.button_column)

        self.run_variables.append(run_variable)

    # remove a run variable and rebuild the grid
    def _remove(self, run_variable):
        if run_variable in self.run_variables:
            self.run_variables.remove(run_variable)
        self._rebuild()

    # wipe all variable rows (row 2+) from the grid
    def _clear_rows(self):
        for row in range(2, self.grid.rowCount()):
            for col in range(self.grid.columnCount()):
                item = self.grid.itemAtPosition(row, col)
                if item and item.widget():
                    item.widget().setParent(None)

    # rebuild variable rows from the current list
    def _rebuild(self):
        self._clear_rows()
        existing = self.run_variables[:]
        self.run_variables = []
        for rv in existing:
            self.add_run_variable(rv)
    
    # opens a dialog for saving run variables
    def save_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Run Variables", "", "FITS File (*.fits)")
        if file_path:
            from src.gui.fits import save_run_variables
            try:
                save_run_variables(file_path, self.get_run_variables())
            except Exception as e:
                print(f"Error saving run variables: {e}")

    # opens a dialog for loading run variables
    def load_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Run Variables", "", "FITS File (*.fits)")
        if file_path:
            from src.gui.fits import load_run_variables
            try:
                run_variables = load_run_variables(file_path)
            except Exception as e:
                print(f"Error loading run variables: {e}")
                return

            # replace all existing run variables with the loaded ones
            self._clear_rows()
            self.run_variables = []
            for rv in run_variables:
                self.add_run_variable(rv)