import mloop.interfaces as mli

import numpy as np
import threading
import os
import re
from datetime import datetime

from src.device.device_types import Stages, Stage
from src.device.ai import AiCancel, AiProgress
from src.value_types import FloatValue, IntValue, BoolValue
from src.gui.plots import FluorescenceSample



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


current_dir = os.path.dirname(os.path.abspath(__file__))
mloop_default_path = os.path.join(current_dir, 'MLOOP_files')
mloop_run_parameter_path = os.path.join(current_dir, 'mloop_config.txt')
os.makedirs(mloop_default_path, exist_ok=True)


class MLOOPInterface(mli.Interface):
    """Custom M-LOOP interface.
    Each iteration: applies parameters -> waits for fluorescence -> runs experiment -> computes cost.
    """

    def __init__(self, params, device, stages: Stages, pre_training_steps,
                 fluorescence_threshold, trainingsteps=100, num_runs_per_parameter_set=1, filename=None, folder=None):
        mli.Interface.__init__(self)

        self.device = device
        self.stages = stages
        self.fluorescence_threshold = fluorescence_threshold
        self.continue_mloop = threading.Event()

        if filename:
            self.param_fname = filename
        else:
            self.param_fname = f"mloop_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.trainingsteps = trainingsteps
        self.pre_training_steps = pre_training_steps
        self.num_runs_per_parameter_set = num_runs_per_parameter_set
        self.params = params
        self.run_num = 0
        self.cost_list = []

        for p in self.params:
            p.history = []
            p.current_value = None

        self.history = {'trials': [], 'cost': []}
        self.reset_model()

        if folder:
            self.model_location = folder
            self.figure_location = folder
        else:
            self.create_folders(filename=self.param_fname)
    
    def get_noise_floor(self, num = 10):
        """Estimate standard deviation of cost function for a fixed parameter set."""
        noise_costs = []
        for _ in range(num):
            n_atoms, od_peak = self.wait_for_fluorescence_and_run()
            cost, uncer, bad = self.cost_function(n_atoms, od_peak)
            if not bad:
                noise_costs.append(cost)

        

    # ── MLOOP interface methods ──────────────────────────────────────────

    def get_next_cost_dict(self, params_dict, num_runs = 1):
        """Called by MLOOP on each iteration. Runs one experiment and returns cost."""
        try:
            self.check_stop()

            mloop_params = params_dict['params']
            print(f"MLOOP Run {self.run_num + 1}: Testing parameters {mloop_params}")

            self.MLOOP_parameters_to_pyqtgui_parameters(mloop_params)
            if num_runs != 1:
                cost_temp = []
                for n in range(num_runs):
                    n_atoms, od_peak = self.wait_for_fluorescence_and_run()
                    cost, bad = self.cost_function(n_atoms, od_peak)
                    cost_temp.append(cost)
                cost = np.mean(cost_temp)
                if num_runs > 2:
                    uncer = np.std(cost_temp)
                else:
                    uncer = 2 * (max(cost_temp) - min(cost_temp))
            
            else:
                n_atoms, od_peak = self.wait_for_fluorescence_and_run()
                cost, bad = self.cost_function(n_atoms, od_peak)
                uncer = 1e-8

            self.record_history(cost, n_atoms, od_peak, uncer, bad)

            self.check_stop()

            self.run_num += 1
            print(f"Run {self.run_num} completed: cost={cost}, bad={bad}")

            # Send progress update to GUI
            self.device.device_pipe.send(AiProgress(self.run_num, self.trainingsteps))

            return {'cost': cost, 'uncer': uncer, 'bad': bool(bad)}

        except AiCancel:
            raise
        except Exception as e:
            print(f"Error in get_next_cost_dict: {e}")
            import traceback
            traceback.print_exc()
            return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

    # ── Experiment execution ─────────────────────────────────────────────

    def wait_for_fluorescence_and_run(self) -> tuple[float, float]:
        """Block until fluorescence threshold is reached, then run the experiment.

        Returns (n_atoms, od_peak) if successful, (0.0, 0.0) on timeout.
        """
        if self.continue_mloop.is_set():
            self.continue_mloop.clear()

        timeout_duration = 120.0
        check_interval = 0.1
        elapsed = 0.0

        while elapsed < timeout_duration:
            self.continue_mloop.wait(timeout=check_interval)
            elapsed += check_interval

            self.fluorescence = self.device.read_fluorescence()
            self.device.device_pipe.send(FluorescenceSample(self.fluorescence))

            if self.fluorescence >= self.fluorescence_threshold:
                print(f"Fluorescence threshold reached: {self.fluorescence} >= {self.fluorescence_threshold}")
                n_atoms, od_peak, _ = self.device.run_experiment(self.stages)
                print(f"Experiment completed: n_atoms={n_atoms:.2e}, od_peak={od_peak:.3f}")
                self.continue_mloop.clear()
                return n_atoms, od_peak

            self.check_stop()

        print("Experiment timeout — no fluorescence within 120s")
        return 0.0, 0.0

    # ── Cost function ────────────────────────────────────────────────────

    def cost_function(self, N, od_peak, multiple_runs = False):
        """Compute cost from atom number and OD peak.
        
        See: https://arxiv.org/abs/2205.08057
        """
        maximum_cost = 1e6

        if N <= 0 or od_peak <= 0.3 or not np.isfinite(N) or not np.isfinite(od_peak):
            return maximum_cost, True

        alpha = -1/5 # alpha = -1/5 is for thermal cloud. proportional to N/T^3, which is a PSD proxy. But cant condense at alpha = -1/5, alpha > 0 for condensation.
        normaliser_lowN = 2 / (1 + np.exp(1e5 / N))

        # cost = -normaliser_lowN * (od_peak ** 3) * N ** (alpha - 1.8) * 1e6
        cost = - np.log(N*od_peak**3)
        self.cost_list.append(cost)
        
        return cost, False

    # ── Cancel handling ──────────────────────────────────────────────────

    def check_stop(self):
        """Poll the pipe for an AiCancel message. Raise AiCancel if one is found."""
        while self.device.device_pipe.poll():
            msg = self.device.device_pipe.recv()
            if isinstance(msg, AiCancel):
                print("Cancel received — stopping MLOOP optimization")
                raise AiCancel
            elif isinstance(msg, Stage):
                self.device.run_stage(msg)
            else:
                print(f"Ignoring non-cancel message during AI: {type(msg).__name__}")

    # ── Parameter handling ───────────────────────────────────────────────

    def MLOOP_parameters_to_pyqtgui_parameters(self, mloop_parameters):
        """Write MLOOP parameter values into the experiment stages.
            param map handles ramp variables, each ramp variable occupies two 
            MLOOP parameters
        """
        # collect ramp parts: run_var_idx → {'ramp_start': val, 'ramp_end': val}
        ramp_parts = {}

        for mloop_idx, (rv_idx, component) in enumerate(self.param_map):
            if mloop_idx >= len(mloop_parameters):
                break
            val = mloop_parameters[mloop_idx]
            param = self.params[rv_idx]

            if component == 'constant':
                stage = self.stages.get_stage(param.stage_id)
                current = getattr(stage, param.variable_id)
                if isinstance(current, FloatValue):
                    new_val = FloatValue.constant(val)
                elif isinstance(current, IntValue):
                    new_val = IntValue.constant(val)
                elif isinstance(current, BoolValue):
                    new_val = BoolValue.constant(val)
                else:
                    new_val = val
                setattr(stage, param.variable_id, new_val)
                param.current_value = val
                print(f"  {param.stage_id}.{param.variable_id} = {val}")
            else:
                ramp_parts.setdefault(rv_idx, {})[component] = val

        # write reconstructed ramp values
        for rv_idx, parts in ramp_parts.items():
            param = self.params[rv_idx]
            rs = parts.get('ramp_start', 0.0)
            re = parts.get('ramp_end', 0.0)
            mode = getattr(param, 'ramp_mode', 'linear')
            stage = self.stages.get_stage(param.stage_id)
            setattr(stage, param.variable_id, FloatValue.ramp(rs, re, mode=mode))
            param.current_value = (rs, re)
            print(f"  {param.stage_id}.{param.variable_id} = ramp({rs}, {re}, {mode})")

    def iterate_start(self):
        """Called before the MLOOP controller starts. Populates parameter boundaries."""
        print('Starting MLOOP optimization...')
        self.check_stop()
        self.Populate_MLOOP_parameters()

    # ── History & plotting ───────────────────────────────────────────────

    def record_history(self, cost, n_atoms, od_peak, uncer, bad):
        """Record parameter values and send plot data to GUI if the result was good."""
        histvec = []
        for p in self.params:
            cv = p.current_value if p.current_value is not None else 0.0
            if isinstance(cv, tuple):
                # ramp variable → two entries matching MLOOP parameter order
                histvec.extend(cv)
            else:
                histvec.append(cv)
            p.history.append(cv)

        if not bad:
            self.history['trials'].append(histvec)
            self.history['cost'].append([cost, n_atoms, od_peak, uncer])
            self.plotcost()

    def plotcost(self):
        """Send the latest cost/parameter snapshot to the GUI for plotting."""
        try:
            from src.gui.ai import AiPlotData

            cost_entry = self.history['cost'][-1]
            plot_data = AiPlotData(
                cost=cost_entry[0],
                cost_uncer=cost_entry[3],
                parameters=self.history['trials'][-1],
                param_names=self.param_names,
                min_boundary=self.min_boundary,
                max_boundary=self.max_boundary,
            )
            self.device.device_pipe.send(plot_data)
        except Exception as e:
            print(f"Error sending plot data: {e}")

    # ── Model / parameter setup ──────────────────────────────────────────

    def reset_model(self):
        self.max_boundary = []
        self.min_boundary = []
        self.num_params = 0
        self.param_names = []
        # maps each MLOOP param index → (run_variable_index, 'constant'|'ramp_start'|'ramp_end')
        self.param_map = []
        for p in self.params:
            if not hasattr(p, 'history'):
                p.history = []
        self.history = {'trials': [], 'cost': []}

    def Populate_MLOOP_parameters(self):
        """Build the parameter dict that MLOOP needs (boundaries, names, config).
        """
        self.mloop_parameter_dict = {}

        for i, param in enumerate(self.params):
            base_name = f"{param.stage_id}_{param.variable_id}"

            if getattr(param, 'is_ramp', False):
                # ramp → two MLOOP parameters
                rs_min = min(param.ramp_start_start, param.ramp_start_end)
                rs_max = max(param.ramp_start_start, param.ramp_start_end)
                self.param_names.append(f"{base_name}_ramp_start")
                self.min_boundary.append(rs_min)
                self.max_boundary.append(rs_max)
                self.param_map.append((i, 'ramp_start'))

                re_min = min(param.ramp_end_start, param.ramp_end_end)
                re_max = max(param.ramp_end_start, param.ramp_end_end)
                self.param_names.append(f"{base_name}_ramp_end")
                self.min_boundary.append(re_min)
                self.max_boundary.append(re_max)
                self.param_map.append((i, 'ramp_end'))
            else:
                # constant → one MLOOP parameter
                rangemin = min(param.start.constant_value(), param.end.constant_value())
                rangemax = max(param.start.constant_value(), param.end.constant_value())
                self.param_names.append(base_name)
                self.min_boundary.append(rangemin)
                self.max_boundary.append(rangemax)
                self.param_map.append((i, 'constant'))

        self.num_params = len(self.param_names)

        self.mloop_parameter_dict['max_boundary'] = self.max_boundary
        self.mloop_parameter_dict['min_boundary'] = self.min_boundary
        self.mloop_parameter_dict['num_params'] = self.num_params
        self.mloop_parameter_dict['param_names'] = self.param_names

        self._load_config_file()

        self.mloop_parameter_dict['controller_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_controller'
        self.mloop_parameter_dict['learner_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_learner'

    def _load_config_file(self):
        """Parse the mloop_config.txt file for extra controller parameters."""
        try:
            with open(mloop_run_parameter_path) as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            print(f"Warning: Config file not found at {mloop_run_parameter_path}")
            self.controller_type = 'gaussian_process'
            return

        for line in lines:
            parts = line.split(' = ')
            if len(parts) != 2 or parts[0][0] in ('#', '', ' '):
                continue

            key, raw_value = parts
            if key == 'controller_type':
                self.controller_type = raw_value
                continue

            if raw_value.startswith('['):
                value = [float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", raw_value)]
            elif raw_value.startswith('('):
                value = tuple(float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", raw_value))
            elif re.match(r'^-?\d+(?:\.\d+)$', raw_value) is not None:
                value = float(raw_value)
            elif is_number(raw_value):
                value = int(raw_value)
            else:
                value = raw_value

            self.mloop_parameter_dict[key] = value

    # ── Folder management ────────────────────────────────────────────────

    def create_folders(self, filename=None):
        self.mydate = datetime.now().strftime('%Y%m%d%H%M')
        if filename:
            self.param_fname = filename
            self.mydate += f'_{filename.replace(" ", "-")}'

        self.model_location = f'{os.getcwd()}/models/{self.mydate}'
        self.figure_location = f'{os.getcwd()}/figures/{self.mydate}'

        fig_parent = os.path.dirname(self.figure_location)
        os.makedirs(fig_parent, exist_ok=True)
        nfolds = len([f for f in os.listdir(fig_parent) if f.startswith(self.mydate.split('_')[0])])
        if nfolds:
            self.figure_location += f'_{nfolds}'

        print(f'Making folder at location {self.model_location}')
        os.makedirs(self.model_location, exist_ok=True)
        os.makedirs(self.figure_location, exist_ok=True)