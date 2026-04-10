import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import os

from src.device.ai import AiProgress, AiSettings, AiCancel
from src.gui.run_variables import RunVariableWidget
from src.device.mloop import mloop_default_path

class AiPlotData:
    """Message class for sending AI plot data from device to GUI"""
    def __init__(self, cost, cost_uncer, parameters, param_names, min_boundary, max_boundary):
        self.cost = cost
        self.cost_uncer = cost_uncer
        self.parameters = parameters
        self.param_names = param_names
        self.min_boundary = min_boundary
        self.max_boundary = max_boundary

# dialog for changing AI settings
class AiDialog(QDialog):
    def __init__(self, stages):
        super().__init__()

        self.stages = stages

        self.setWindowTitle("AI Settings")
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add settings
        form_layout = QFormLayout()
        self.pre_training_steps = QSpinBox()
        self.pre_training_steps.setRange(0, 10000)
        self.training_steps = QSpinBox()
        self.training_steps.setRange(0, 10000)
        self.num_runs_per_parameter_set = QSpinBox()
        self.num_runs_per_parameter_set.setRange(1, 100)

        # Steps rows
        form_layout.addRow("Pre-Training Steps:", self.pre_training_steps)
        form_layout.addRow("Training Steps:", self.training_steps)
        form_layout.addRow("Number of Runs per Parameter Set:", self.num_runs_per_parameter_set)

        # Group box titled "Learner" containing the two model dropdowns
        learner_group = QGroupBox("Learner")
        learner_layout = QFormLayout()
        self.pre_training_model = QComboBox()
        self.pre_training_model.addItems(['differential_evolution', 'nelder_mead'])

        self.training_model = QComboBox()
        self.training_model.addItems(['neural_net', 'gaussian_process'])
        learner_layout.addRow("Pre-Training Model:", self.pre_training_model)
        learner_layout.addRow("Training Model:", self.training_model)

        learner_group.setLayout(learner_layout)

        layout.addLayout(form_layout)
        layout.addWidget(learner_group)

        # Seed from previous runs
        resume_group = QGroupBox("Resume/Seed")
        resume_layout = QFormLayout()

        self.resume_checkbox = QCheckBox("Resume")
        self.resume_path = QLineEdit()
        self.resume_path.setPlaceholderText("Path to previous run data")
        self.resume_path.setPlaceholderText("Archive path")
        self.resume_browse_btn = QPushButton("Browse")
        self.resume_browse_btn.clicked.connect(self.browse_resume_archive)

        resume_path_row = QHBoxLayout()
        resume_path_row.addWidget(self.resume_path)
        resume_path_row.addWidget(self.resume_browse_btn)

        resume_layout.addRow(self.resume_checkbox)
        resume_layout.addRow("Archive file:", resume_path_row)
        resume_group.setLayout(resume_layout)
        layout.addWidget(resume_group)

        self.resume_checkbox.toggled.connect(self.set_resume_enabled)

        # add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.save_ai_settings)
        layout.addWidget(self.button_box)

        # load the current settings
        ai_settings = self.stages.ai_settings
        self.pre_training_steps.setValue(ai_settings.pre_training_steps)
        self.pre_training_model.setCurrentText(ai_settings.pre_training_model)

        self.training_steps.setValue(ai_settings.training_steps)
        self.training_model.setCurrentText(ai_settings.training_model)



    def set_resume_enabled(self, enabled: bool):
        self.resume_path.setEnabled(enabled)
        self.resume_browse_btn.setEnabled(enabled)

    def browse_resume_archive(self):
        # Defaults to current archive directory
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'device', 'MLOOP_files')

        fname, _ = QFileDialog.getOpenFileName(self, "Select Archive File", default_dir, "M-LOOP controller archives (*_controller*)")
        if fname:
            self.resume_path.setText(fname)
            self.resume_checkbox.setChecked(True)

    # saves the settings currently in the gui into the `StagesGui`'s ai_settings
    def save_ai_settings(self):
        pre_training_steps = self.pre_training_steps.value()
        training_steps = self.training_steps.value()
        training_model = self.training_model.currentText()
        pre_training_model = self.pre_training_model.currentText()
        num_runs_per_parameter_set = self.num_runs_per_parameter_set.value()

        load_file_path = None
        if self.resume_checkbox.isChecked():
            load_file_path = self.resume_path.text().strip()

        # update the AI settings with the new run variables
        self.stages.ai_settings = AiSettings(pre_training_steps, training_steps, pre_training_model, training_model, load_file_path = load_file_path, num_runs_per_parameter_set=num_runs_per_parameter_set)

        # close the dialog
        self.accept()

class AiProgressDialog(QDialog):
    def __init__(self, window):
        super().__init__()

        self.window = window

        self.setWindowTitle("AI Progress")
        self.setModal(True)
        self.resize(1000, 700)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # add a label to show the progress
        self.progress_label = QLabel("Submitting to device...")
        layout.addWidget(self.progress_label)

        # add a progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Initialize plotting data
        self.cost_history = []
        self.parameter_history = []
        self.legend_added = set()  # track which parameter names have legend entries
        
        # Create matplotlib figure for AI plots
        self.ai_canvas = FigureCanvas(Figure(figsize=(12, 8)))
        self.ai_figure = self.ai_canvas.figure
        layout.addWidget(self.ai_canvas)
        
        self.setup_plots()
        
        import matplotlib.pyplot as plt
        name = "tab10"
        cmap = plt.get_cmap(name)
        self.colors = cmap.colors

        # add a button to cancel the operation
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.rejected.connect(self.cancel_ai)
        layout.addWidget(self.button_box)

    def cancel_ai(self):
        self.window.gui_pipe.send(AiCancel())

    def update_progress(self, received: AiProgress):
        self.progress_label.setText(f"Running step {received.current_step} of {received.total_steps}")
        self.progress_bar.setValue(int(received.current_step / received.total_steps * 100))

        if received.current_step == received.total_steps:
            self.accept()
    
    def setup_plots(self):
        """Initialize the AI plot layout"""
        self.ai_figure.clf()
        self.ax_cost_vs_run = self.ai_figure.add_subplot(221)
        self.ax_param_vs_run = self.ai_figure.add_subplot(223) 
        self.ax_cost_vs_param = self.ai_figure.add_subplot(224)
        
        # Set labels
        self.ax_cost_vs_run.set_xlabel('Experiment Number')
        self.ax_cost_vs_run.set_ylabel('Cost')
        self.ax_param_vs_run.set_xlabel('Experiment Number')
        self.ax_param_vs_run.set_ylabel('Parameter Value (%)')
        self.ax_cost_vs_param.set_xlabel('Parameter Value (%)')
        self.ax_cost_vs_param.set_ylabel('Cost')
        
        self.ai_figure.tight_layout()
    
    def update_ai_plots(self, plot_data: AiPlotData):
        """Update AI plots with new data from device process"""
        try:
            # Store the new data
            self.cost_history.append(plot_data.cost)
            self.parameter_history.append(plot_data.parameters)
            
            # Normalize parameters to a percentage
            normed_params = self.normalize_parameters(
                np.array(plot_data.parameters), 
                np.array(plot_data.min_boundary), 
                np.array(plot_data.max_boundary)
            ) * 100
            
            experiment_num = len(self.cost_history) - 1
            
            # Cost vs Run Number
            self.ax_cost_vs_run.errorbar(
                experiment_num, plot_data.cost, plot_data.cost_uncer,
                fmt='o', capsize=5, markersize=4, elinewidth=2, 
                color=self.colors[0]
            )
            
            # Parameter vs Run Number  
            for i, param_value in enumerate(normed_params):
                name = plot_data.param_names[i] if i < len(plot_data.param_names) else f"p{i}"
                label = name if name not in self.legend_added else None
                self.ax_param_vs_run.plot(
                    experiment_num, param_value, 'o', 
                    color=self.colors[i % 10],
                    label=label,
                )
                self.legend_added.add(name)
            
            # Cost vs Parameter
            for i, param_value in enumerate(normed_params):
                self.ax_cost_vs_param.errorbar(
                    param_value, plot_data.cost, plot_data.cost_uncer,
                    fmt='o', capsize=5, markersize=4, elinewidth=2,
                    color=self.colors[i % 10],
                )
            
            # Update legends and plot limits, then redraw
            self.ax_param_vs_run.legend(fontsize='small', loc='best')
            for ax in [self.ax_cost_vs_run, self.ax_param_vs_run, self.ax_cost_vs_param]:
                ax.relim()
                ax.autoscale_view()
            
            self.ai_canvas.draw_idle()
            print('AI plots updated in progress dialog')
            
        except Exception as e:
            print(f"Error updating AI plots: {e}")
    
    def normalize_parameters(self, param, pmin, pmax):
        return (param - pmin) / (pmax - pmin)
    
    def clear_plots(self):
        self.cost_history = []
        self.parameter_history = []
        self.legend_added = set()
        self.setup_plots()
        self.ai_canvas.draw()
