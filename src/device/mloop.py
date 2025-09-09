# imports for M-LOOP
import mloop.interfaces as mli

# other imports
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np
import time
import threading
import pickle
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QObject, pyqtSignal
import re
from src.device.device_types import Stages
from src.device import device

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Default path for MLOOP files
# Use local paths that work on both macOS and Linux
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
mloop_default_path = os.path.join(current_dir, 'MLOOP_files')
mloop_run_parameter_path = os.path.join(current_dir, 'mloop_config.txt')

# Ensure MLOOP directory exists
os.makedirs(mloop_default_path, exist_ok=True)

class AiCancel:
    pass


#Declare your custom class that inherits from the Interface class
class MLOOPInterface(mli.Interface):
    #Initialization of the interface
    def __init__(self, params, device, stages: Stages, pre_training_steps, fluorescence_threshold, trainingsteps = 100, filename=None, folder=None):
        mli.Interface.__init__(self)        
        # Condition used to wait for experiment to return data
        self.continue_mloop = threading.Event()
        self.device = device
        self.stages = stages
        self.fluorescence_threshold = fluorescence_threshold
        self.fluorescence = device.read_fluorescence()

        # populating parameters
        if filename:
            self.param_fname = filename
        else:
            # Default filename if none provided
            self.param_fname = f"mloop_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if trainingsteps:
            self.trainingsteps = trainingsteps
        if pre_training_steps:
            self.pre_training_steps = pre_training_steps
        self.optimise_guesses = 1000
        self.params = params
        self.niter = 0
        self.run_num = 0
        self.cost_array = np.zeros(self.trainingsteps)

        for p in self.params:
          p.history = []
          p.current_value = None  # Store the current parameter value being tested


        self.history = {'trials':[],  # This is history on a per-trial basis
                        'cost':[] }

        self.reset_model()

        name = "tab10"
        cmap = plt.get_cmap(name)  # type: matplotlib.colors.ListedColormap
        colors = cmap.colors  # type: list
        self.colors = colors

        # Now that we've decided on the parameter set, decide where to shove the resulting .fits files of our runs.
        if folder:
          self.model_location = folder
          # Handle potential attribute error
          try:
              figloc_fragment = folder.split('/')[-2:] if '/' in folder else folder.split('\\')[-2:]
              figloc_fragment = '/'.join(figloc_fragment)
              self.figure_location = f'{self.parent_gui.datapath}/{figloc_fragment}'
          except AttributeError:
              self.figure_location = folder
        else:
            self.create_folders(filename = self.param_fname)

    def get_next_cost_dict(self, params_dict):
        """
       Improved error handling and logic flow
        """
        try:
            self.check_stop()  # Check if we should stop before processing new parameters

            #Get parameters from the provided dictionary
            mloop_params = params_dict['params']
            print(f"MLOOP Run {self.run_num + 1}: Testing parameters {mloop_params}")

            # Put parameters into form for pyqtgui program
            self.MLOOP_parameters_to_pyqtgui_parameters(mloop_params)

            # Initialize results
            n_atoms_list = []
            od_peak_list = []
            
            # Start the timer to begin the experiment
            # For MLOOP, we typically run a single experiment per iteration
            # If multiple experiments per iteration are needed, this could be made configurable
            num_experiments = 1  # Single experiment per MLOOP iteration
            
            for i in range(num_experiments):
                print(f'Beginning experiment iteration {i+1}/{num_experiments}')
                
                # THIRD HALT CHECK: Before each experiment iteration
                self.check_stop()
                    
                if self.continue_mloop.is_set():
                    self.continue_mloop.clear()
                
                # Shorter timeout with frequent halt checking
                experiment_completed = False
                timeout_duration = 120.0  # Total timeout
                check_interval = 0.5    # Check halt every 0.5 seconds
                elapsed_time = 0.0
                
                while elapsed_time < timeout_duration and not experiment_completed:
                    experiment_completed = self.continue_mloop.wait(timeout=check_interval)
                    elapsed_time += check_interval
                    
                    # Update fluorescence reading
                    self.fluorescence = self.device.read_fluorescence()
                    
                    if self.fluorescence >= self.fluorescence_threshold:
                        print(f"Fluorescence threshold reached: {self.fluorescence} >= {self.fluorescence_threshold}")
                        experiment_completed = True  # Mark experiment as successful
                        self.continue_mloop.set()  # Signal completion
                        self.device.run_experiment(self.stages)
                        break
                    else:
                        # Experiment still running, continue waiting
                        print(f"Fluorescence: {self.fluorescence}, waiting for threshold: {self.fluorescence_threshold}")
                        experiment_completed = False  # Not successful yet

                if not experiment_completed:
                    print("Experiment timeout - no response within 120 seconds")
                    experiment_completed = False
                    self.continue_mloop.set()  # Signal completion even on timeout
                    break
                    
                self.continue_mloop.clear()
                self.check_stop()

                if experiment_completed:
                    try:
                        # Get experiment results from the princeton camera interface
                        # Note: blackfly/bfcam is no longer in use
                        n_atoms = self.device.n_atoms[-1]
                        od_peak = self.device.od_peak[-1]
                        n_atoms_list.append(n_atoms)
                        od_peak_list.append(od_peak)
                        print(f"MLOOP: Acquired data - n_atoms: {n_atoms:.2e}, od_peak: {od_peak:.3f}")
                    except (IndexError, AttributeError) as e:
                        print(f'Error getting experiment data from princeton camera: {e}')
                        # Use default/fallback values if data extraction fails
                        n_atoms = 0.0
                        od_peak = 0.0
                        n_atoms_list.append(n_atoms)
                        od_peak_list.append(od_peak)
                        break
                else:
                    print('Ending experiment due to no data from experiment')
                    break

            # Calculate cost based on results
            if experiment_completed and n_atoms_list and od_peak_list:
                # Use average if multiple iterations
                avg_n_atoms = np.mean(n_atoms_list)
                avg_od_peak = np.mean(od_peak_list)
                cost, uncer, bad = self.cost_function(avg_n_atoms, avg_od_peak)
            else:
                cost, uncer, bad = self.cost_function(0, 0)

            # Update history
            histvec = []
            for p in self.params:
                if p.current_value is not None:
                    histvec.append(p.current_value)
                    p.history.append(p.current_value)
                else:
                    # Fallback if no current value
                    histvec.append(0.0)
                    p.history.append(0.0)
            bad = bool(bad)
            print(f'bad = {bad}')
            if not bad:  # Only record good results
                print('iteration success, plotting cost')
                self.history['trials'].append(histvec)
                # Store results consistently
                self.history['cost'].append([cost, avg_n_atoms if 'avg_n_atoms' in locals() else 0, 
                                           avg_od_peak if 'avg_od_peak' in locals() else 0, uncer])
                self.plotcost()

            # FINAL HALT CHECK: Before returning results
            self.check_stop()

            #The cost, uncertainty and bad boolean must all be returned as a dictionary
            cost_dict = {'cost': cost, 'uncer': uncer, 'bad': bad}
            self.run_num += 1
            
            print(f"Run {self.run_num} completed: cost={cost}, bad={bad}")
            
            return cost_dict
            
        except Exception as e:
            print(f"Error in get_next_cost_dict: {e}")
            import traceback
            traceback.print_exc()
            return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

    def cost_function(self, N, od_peak):
        """
        Improved cost function with better handling
        """
        is_bad_result = False
        maximum_cost = 9e99
        
        if (N <= 0) or (od_peak <= 0): # Guarantees that faulty determinations of N, od_peak won't be optimal
            is_bad_result = True
            cost = maximum_cost
            uncertainty = 0.0
        else:
            # See cost function form: https://arxiv.org/abs/2205.08057, page 3
            alpha = 1 # normally 0.5 or 1
            normaliser_lowN = 2 / (1 + np.exp(1e3/N)) # avoid divergences at small N
            
            cost = -normaliser_lowN * (od_peak**3) * N**(alpha - 1.8) * 1e6
            self.cost_array = np.append(self.cost_array, cost)
            if self.run_num > self.pre_training_steps:
              uncertainty = np.abs(np.std(self.cost_array))
            else:
              uncertainty = 0.0
            #uncertainty = 0.0   

        return cost, uncertainty, is_bad_result

    def iterate_start(self, n_iterations=None):
        """Called when MLOOP starts optimization"""
        print('Starting MLOOP optimization...')
        # Get parameters required for the machine learning controller
        self.check_stop()  # Check if we should stop before starting
        self.Populate_MLOOP_parameters()

    def iterate_end(self):
        """Called when MLOOP ends optimization"""
        print('MLOOP optimization completed')
        self.continue_mloop.set()

    def check_stop(self):
        """Called when MLOOP is stopped"""
        print('Stopping MLOOP optimization...')
        self.continue_mloop.set()
        if self.device.device_pipe.poll():
            msg = self.device.device_pipe.recv()
            if not isinstance(msg, AiCancel):
                print(f"Non AI cancel message received while running: {type(msg)}")
            raise AiCancel

    def MLOOP_parameters_to_pyqtgui_parameters(self, mloop_parameters):
        for i, param in enumerate(self.params):
            if i < len(mloop_parameters):
                value = mloop_parameters[i]
                
                # Get the stage and variable to update
                stage_id = param.stage_id
                variable_id = param.variable_id
                stage = self.stages.get_stage(stage_id)
                
                # Apply the MLOOP parameter value to the stage
                setattr(stage, variable_id, value)
                
                # Store the current value for history tracking
                param.current_value = value

                print(f"Applied MLOOP parameter: stage_id={stage_id}, variable_id={variable_id}, value={value}")


    def Populate_MLOOP_parameters(self):
        self.mloop_parameter_dict = {}

        for i, param in enumerate(self.params):
            # For RunVariable objects, use start/end values as boundaries
            rangemin = min(param.start.constant_value(), param.end.constant_value())
            rangemax = max(param.start.constant_value(), param.end.constant_value())
            param_name = f"{param.stage_id}_{param.variable_id}"  # Create descriptive name
            
            self.param_names.append(param_name)
            self.max_boundary.append(rangemax)
            self.min_boundary.append(rangemin)
            self.num_params = i + 1

        self.mloop_parameter_dict['max_boundary'] = self.max_boundary
        self.mloop_parameter_dict['min_boundary'] = self.min_boundary
        self.mloop_parameter_dict['num_params'] = self.num_params
        self.mloop_parameter_dict['param_names'] = self.param_names

        # Load additional parameters from config file
        try:
            with open(mloop_run_parameter_path) as open_file:
                mloop_file_lines = open_file.read().splitlines()

            for i, line in enumerate(mloop_file_lines):
                split_line = line.split(' = ')
                if len(split_line) == 2 and split_line[0][0] not in ['#', '', ' ']:
                    if split_line[0] != 'controller_type':
                        if split_line[1][0] == '[':
                            split_second = [float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", split_line[1])]
                        elif split_line[1][0] == '(':
                            split_second = tuple([float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", split_line[1])])
                        elif re.match(r'^-?\d+(?:\.\d+)$', split_line[1]) is not None:
                            split_second = float(split_line[1])
                        elif is_number(split_line[1]):
                            split_second = int(split_line[1])
                        else:
                            split_second = split_line[1]
                        self.mloop_parameter_dict[split_line[0]] = split_second
                    else:
                        self.controller_type = split_line[1]
        except FileNotFoundError:
            print(f"Warning: Config file not found at {mloop_run_parameter_path}")
            self.controller_type = 'gaussian_process'  # Default controller

        # paths for saving output
        self.mloop_parameter_dict['controller_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_controller'
        self.mloop_parameter_dict['learner_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_learner'
    # Keep all your other methods (plotcost, normalize_parameter, reset_model, etc.) as they are

    def plotcost(self):
        """Send plot data to GUI process instead of plotting directly"""
        try:
            # Get the latest cost and parameters
            cost = self.history['cost'][-1][0]  # Latest cost
            cost_uncer = self.history['cost'][-1][3]  # Latest uncertainty
            all_parameters = self.history['trials'][-1]  # Latest parameter values
            
            # Import here to avoid circular imports
            from src.gui.ai import AiPlotData
            
            # Create plot data message
            plot_data = AiPlotData(
                cost=cost,
                cost_uncer=cost_uncer,
                parameters=all_parameters,
                param_names=self.param_names,
                min_boundary=self.min_boundary,
                max_boundary=self.max_boundary
            )
            
            # Send plot data to GUI process via device pipe
            self.device.device_pipe.send(plot_data)
            print('AI plot data sent to GUI')
            
        except Exception as e:
            print(f"Error sending plot data: {e}")

    def normalize_parameter(self, param, pmin, pmax):
        norm_param = (param - pmin)/(pmax - pmin)
        return norm_param

    def reset_model(self):
        self.max_boundary = []
        self.min_boundary = []
        self.num_params = 0
        self.param_names = []
        for p in self.params:
            if not hasattr(p,'history'): 
                p.history = []

        self.history = {'trials':[], 'cost':[]}

    # Keep your other methods as they are...
    def create_folders(self, filename=None):
        self.mydate = datetime.now().strftime('%Y%m%d%H%M')
        if filename:
            self.param_fname = filename
            self.mydate += f'_{filename.replace(" ","-")}'

        self.model_location = f'{os.getcwd()}/models/{self.mydate}'
        
        self.figure_location = f'{os.getcwd()}/figures/{self.mydate}'

        nfolds = len([f for f in os.listdir(os.path.dirname(self.figure_location)) if f.startswith(self.mydate.split('_')[0])])
        if nfolds:
            self.figure_location += f'_{nfolds}'
        
        print(f'Making folder at location {self.model_location}')
        os.makedirs(self.model_location, exist_ok=True)
        os.makedirs(self.figure_location, exist_ok=True)
