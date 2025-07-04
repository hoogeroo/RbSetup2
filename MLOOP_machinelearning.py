#Imports for M-LOOP
import mloop.interfaces as mli
import mloop.controllers as mlc
import mloop.visualizations as mlv

#Other imports
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np
import time
import threading
import pickle
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal
import re


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

#Declare your custom class that inherits from the Interface class
class MLOOPInterface(mli.Interface, QObject):
    # Signal for thread-safe GUI updates
    progress_updated = pyqtSignal(int, int, float, bool)  # run_num, total_steps, cost, is_bad

    #Initialization of the interface
    def __init__(self, params, trainingsteps = 100, filename=None, folder=None, parent_gui=None):
        #You must include the super command to call the parent class, Interface, constructor
        mli.Interface.__init__(self)
        QObject.__init__(self)
        
        self.parent_gui = parent_gui #store parent reference

        # Connect signal to parent GUI if available
        if self.parent_gui and hasattr(self.parent_gui, 'updateMLProgress'):
            self.progress_updated.connect(self.parent_gui.updateMLProgress)

        # Initialize user_halt_event
        self.user_halt_event = threading.Event()
        
        # Condition used to wait for experiment to return data
        self.continue_mloop = threading.Event()

        # populating parameters
        if filename:
            self.param_fname = filename
        if trainingsteps:
            self.trainingsteps = trainingsteps
        self.optimise_guesses = 1000
        self.params = params
        self.niter = 0
        self.run_num = 0

        for p in self.params:
          p.vals_to_try = []
          p.history = []
          p.bestval = 0
        self.lowcost = 0

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
          # FIXED: Handle potential attribute error
          if hasattr(self.parent_gui, 'datapath'):
              figloc_fragment = folder.split('/')[-2:] if '/' in folder else folder.split('\\')[-2:]
              figloc_fragment = '/'.join(figloc_fragment)
              self.figure_location = f'{self.parent_gui.datapath}/{figloc_fragment}'
          else:
              self.figure_location = folder
        else:
          self.create_folders(filename = self.param_fname)

        #Attributes of the interface can be added here
        #If you want to precalculate any variables etc. this is the place to do it
        #In this example we will just define the location of the minimum
        self.minimum_params = np.array([0,0.1,-0.1])

    def get_next_cost_dict(self, params_dict):
        """
        FIXED: Improved error handling and logic flow
        """
        try:
            # IMMEDIATE HALT CHECK: Check before any processing
            if self.user_halt_event.is_set():
                print("User halt detected immediately, aborting experiment request")
                # Set a flag to prevent repeated halt messages
                self._halt_message_printed = True
                return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

            #Get parameters from the provided dictionary
            mloop_params = params_dict['params']
            print(f"MLOOP Run {self.run_num + 1}: Testing parameters {mloop_params}")

            # Put parameters into form for pyqtgui program
            self.MLOOP_parameters_to_pyqtgui_parameters(mloop_params)

            # SECOND HALT CHECK: After parameter processing
            if self.user_halt_event.is_set():
                if not getattr(self, '_halt_message_printed', False):
                    print("User halt detected, stopping optimization")
                    self._halt_message_printed = True
                return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

            # Initialize results
            Natoms_list = []
            OD_peak_list = []
            
            # Start the timer to begin the experiment
            # For MLOOP, we typically run a single experiment per iteration
            # If multiple experiments per iteration are needed, this could be made configurable
            num_experiments = 1  # Single experiment per MLOOP iteration
            
            for i in range(num_experiments):
                print(f'Beginning experiment iteration {i+1}/{num_experiments}')
                
                # THIRD HALT CHECK: Before each experiment iteration
                if self.user_halt_event.is_set():
                    if not getattr(self, '_halt_message_printed', False):
                        print("User halt detected during experiment iterations")
                        self._halt_message_printed = True
                    return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}
                    
                if self.continue_mloop.is_set():
                    self.continue_mloop.clear()
                    
                self.parent_gui.t_initial = time.time()
                self.parent_gui.ML_active = True
                
                # ENHANCED: Shorter timeout with frequent halt checking
                experiment_completed = False
                timeout_duration = 30.0  # Total timeout
                check_interval = 0.5    # Check halt every 0.5 seconds
                elapsed_time = 0.0
                
                while elapsed_time < timeout_duration and not experiment_completed:
                    # FREQUENT HALT CHECK: During experiment wait
                    if self.user_halt_event.is_set():
                        if not getattr(self, '_halt_message_printed', False):
                            print("User halt detected while waiting for experiment")
                            self._halt_message_printed = True
                        return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}
                    
                    experiment_completed = self.continue_mloop.wait(timeout=check_interval)
                    elapsed_time += check_interval
                
                if not experiment_completed:
                    print("Experiment timeout - no response within 30 seconds")
                    self.parent_gui.experiment_success = False
                    break
                    
                self.continue_mloop.clear()
                
                # FOURTH HALT CHECK: After experiment completion
                if self.user_halt_event.is_set():
                    if not getattr(self, '_halt_message_printed', False):
                        print("User halt detected after experiment completion")
                        self._halt_message_printed = True
                    return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}
                
                if self.parent_gui.experiment_success:
                    try:
                        # Get experiment results from the princeton camera interface
                        # Note: blackfly/bfcam is no longer in use
                        Natoms = self.parent_gui.camera.Natoms[-1]
                        OD_peak = self.parent_gui.camera.ODpeak[-1]
                        Natoms_list.append(Natoms)
                        OD_peak_list.append(OD_peak)
                        print(f"MLOOP: Acquired data - Natoms: {Natoms:.2e}, OD_peak: {OD_peak:.3f}")
                    except (IndexError, AttributeError) as e:
                        print(f'Error getting experiment data from princeton camera: {e}')
                        # Use default/fallback values if data extraction fails
                        Natoms = 0.0
                        OD_peak = 0.0
                        Natoms_list.append(Natoms)
                        OD_peak_list.append(OD_peak)
                        self.parent_gui.experiment_success = False
                        break
                else:
                    print('Ending experiment due to no data from experiment')
                    break

            # Calculate cost based on results
            if self.parent_gui.experiment_success and Natoms_list and OD_peak_list:
                # Use average if multiple iterations
                avg_Natoms = np.mean(Natoms_list)
                avg_OD_peak = np.mean(OD_peak_list)
                cost, uncer, bad = self.cost_function(avg_Natoms, avg_OD_peak)
            else:
                cost, uncer, bad = self.cost_function(0, 0)

            # Update history
            histvec = []
            for p in self.params:
                ptype = type(p.vals_to_try)

                if (ptype is int or ptype is np.float64 or ptype is float):
                    histvec.append(p.vals_to_try)
                    p.history.append(p.vals_to_try)
                    p.vals_to_try = None
                elif p.vals_to_try is not None and len(p.vals_to_try) > 0:
                    histvec.append(p.vals_to_try[0])
                    p.history.append(p.vals_to_try[0])
                    p.vals_to_try = np.delete(p.vals_to_try, 0)

            if cost > 0 and not bad:  # Only record good results
                self.history['trials'].append(histvec)
                # FIXED: Store results consistently
                self.history['cost'].append([cost, avg_Natoms if 'avg_Natoms' in locals() else 0, 
                                           avg_OD_peak if 'avg_OD_peak' in locals() else 0, uncer])
                self.plotcost()

            # FINAL HALT CHECK: Before returning results
            if self.user_halt_event.is_set():
                print("User halt detected before returning results")
                return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

            #The cost, uncertainty and bad boolean must all be returned as a dictionary
            cost_dict = {'cost': cost, 'uncer': uncer, 'bad': bad}
            self.run_num += 1
            
            print(f"Run {self.run_num} completed: cost={cost}, bad={bad}")
            
            # Emit signal for thread-safe GUI update
            self.progress_updated.emit(self.run_num, self.trainingsteps, cost, bad)
            
            return cost_dict
            
        except Exception as e:
            print(f"Error in get_next_cost_dict: {e}")
            import traceback
            traceback.print_exc()
            return {'cost': float('inf'), 'uncer': 0.0, 'bad': True}

    def cost_function(self, N, OD_peak):
        """
        FIXED: Improved cost function with better handling
        """
        is_bad_result = False
        maximum_cost = 9e99
        
        if (N <= 0) or (OD_peak <= 0): # Guarantees that faulty determinations of N, OD_peak won't be optimal
            is_bad_result = True
            cost = maximum_cost
            uncertainty = 0.0
        else:
            # See cost function form: https://arxiv.org/abs/2205.08057, page 3
            alpha = 2 # normally 0.5 or 1
            normaliser_lowN = 2 / (1 + np.exp(1e3/N)) # avoid divergences at small N

            # FIXED: Make cost negative for maximization (MLOOP minimizes)
            cost = -normaliser_lowN * OD_peak**3 * N**(alpha - 1.8)
            uncertainty = np.sqrt(abs(cost))

        return cost, uncertainty, is_bad_result

    def iterate_start(self, n_iterations=None):
        """Called when MLOOP starts optimization"""
        print('Starting MLOOP optimization...')
        self.user_halt_event.clear()
        # Get parameters required for the machine learning controller
        self.Populate_MLOOP_parameters()

    def iterate_end(self):
        """Called when MLOOP ends optimization"""
        print('MLOOP optimization completed')
        self.parent_gui.ML_active = False
        self.continue_mloop.set()

    def iterate_stop(self, cancelled=False):
        """Called when MLOOP is stopped"""
        print('Stopping MLOOP optimization...')
        self.parent_gui.ML_active = False
        self.continue_mloop.set()
        self.user_halt_event.set()
        if cancelled:
            print('Machine learning cancelled by user')
        self.parent_gui.OptimiseButton.setText('Optimise')
        self.parent_gui.OptimiseButton.setChecked(False)
    
    def reset_halt_state(self):
        """Reset halt state for new optimization run"""
        self.user_halt_event.clear()
        self._halt_message_printed = False

    def MLOOP_parameters_to_pyqtgui_parameters(self, mloop_parameters):
        """
        FIXED: Better parameter handling
        """
        for i, p in enumerate(self.params):
            if i < len(mloop_parameters):
                temp = mloop_parameters[i]
                stepsize = p.Startbox.singleStep()
                temp = round(temp/stepsize) * stepsize
                p.vals_to_try = [temp]

    def Populate_MLOOP_parameters(self):
        """
        FIXED: Ensure boundaries are properly set
        """
        self.mloop_parameter_dict = {}

        for i, p in enumerate(self.params):
            rangemin = min([p.Startbox.value(), p.Stopbox.value()])
            rangemax = max([p.Startbox.value(), p.Stopbox.value()])
            self.param_names.append(p.title.text())
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

    def load_params(self, params):
        """Load parameters into the MLOOP interface"""
        self.params = params
        for p in self.params:
            if not hasattr(p, 'vals_to_try'):
                p.vals_to_try = []
            if not hasattr(p, 'history'):
                p.history = []
            if not hasattr(p, 'bestval'):
                p.bestval = 0
        print(f"Loaded {len(params)} parameters into MLOOP interface")

    def save(self):
        """Save the current MLOOP model and history"""
        try:
            # Create save data dictionary
            save_data = {
                'params': self.params,
                'history': self.history,
                'run_num': self.run_num,
                'trainingsteps': self.trainingsteps,
                'param_fname': self.param_fname,
                'lowcost': self.lowcost
            }
            
            # Save to pickle file
            save_path = f'{self.model_location}/{self.param_fname}.pkl'
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            print(f"MLOOP model saved to {save_path}")
            
        except Exception as e:
            print(f"Error saving MLOOP model: {e}")

    def load(self, params, name=None):
        """Load a previously saved MLOOP model"""
        try:
            if name is None:
                # Load fresh parameters
                self.load_params(params)
                return
                
            # Load from pickle file
            with open(name, 'rb') as f:
                save_data = pickle.load(f)
            
            # Restore saved data
            self.params = save_data.get('params', params)
            self.history = save_data.get('history', {'trials': [], 'cost': []})
            self.run_num = save_data.get('run_num', 0)
            self.trainingsteps = save_data.get('trainingsteps', 100)
            self.param_fname = save_data.get('param_fname', 'untitled')
            self.lowcost = save_data.get('lowcost', 0)
            
            print(f"MLOOP model loaded from {name} - {self.run_num} previous runs")
            
        except Exception as e:
            print(f"Error loading MLOOP model: {e}")
            # Fall back to loading fresh parameters
            self.load_params(params)

    # Keep all your other methods (plotcost, normalize_parameter, reset_model, etc.) as they are
    def plotcost(self):
        """Your existing plotcost method - keeping as is"""
        try:
            cost = [x[0] for x in self.history['cost']]
            cost_uncer = [x[3] for x in self.history['cost']]
            all_parameters = np.array(self.history['trials'][-1])

            exptnum = list(range(len(cost)))

            fig = self.parent_gui.figure_MachineLearning
            if self.run_num == 0:
                fig.clf()
                self.parent_gui.ax_ML_ax_costVsRunNumber = fig.add_subplot(221)
                self.parent_gui.ax_ML_ax_NormParamVsRunNumber = fig.add_subplot(222)
                self.parent_gui.ax_ML_ax_ParamVsRunNumber = fig.add_subplot(223)
                self.parent_gui.ax_ML_ax_CostVsParam = fig.add_subplot(224)
            
            ax_costVsRunNumber = self.parent_gui.ax_ML_ax_costVsRunNumber
            ax_NormParamVsRunNumber = self.parent_gui.ax_ML_ax_NormParamVsRunNumber
            ax_ParamVsRunNumber = self.parent_gui.ax_ML_ax_ParamVsRunNumber
            ax_CostVsParam = self.parent_gui.ax_ML_ax_CostVsParam

            # Cost Vs Run number
            ax_costVsRunNumber.errorbar(exptnum[-1], cost[-1], cost_uncer[-1], fmt='o', capsize=5, markersize=4, elinewidth=2, color=self.colors[0])
            ax_costVsRunNumber.set_xlabel('Expt. Number')
            ax_costVsRunNumber.set_ylabel('Cost')

            # Normalized Parameter vs Run number
            for i in range(0, len(all_parameters)):
                norm_param_vec = self.normalize_parameter(all_parameters[i], self.min_boundary[i], self.max_boundary[i])
                ax_NormParamVsRunNumber.plot(exptnum[-1], norm_param_vec, 'o', color=self.colors[i%10])
            ax_NormParamVsRunNumber.set_xlabel('Expt. Number')
            ax_NormParamVsRunNumber.set_ylabel('Normalized Parameter value')
            ax_NormParamVsRunNumber.legend(self.param_names)

            # Parameter vs Run number
            for i in range(0, len(all_parameters)):
                ax_ParamVsRunNumber.plot(exptnum[-1], all_parameters[i], 'o', color=self.colors[i%10])
            ax_ParamVsRunNumber.set_xlabel('Expt. Number')
            ax_ParamVsRunNumber.set_ylabel('Parameter value')

            # Cost vs Parameter
            for i in range(0, len(all_parameters)):
                ax_CostVsParam.errorbar(all_parameters[i], cost[-1], cost_uncer[-1], fmt='o', capsize=5, markersize=4, elinewidth=2, color=self.colors[i%10])
            ax_CostVsParam.set_ylabel('Cost')
            ax_CostVsParam.set_xlabel('Parameter value')

            fig.tight_layout()
            self.parent_gui.canvas_MachineLearning.draw_idle()
            print('Cost plot updated')
        except Exception as e:
            print(f"Error in plotcost: {e}")

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
        
        if hasattr(self.parent_gui, 'datapath'):
            self.figure_location = f'{self.parent_gui.datapath}/models/{self.mydate}'
        else:
            self.figure_location = f'{os.getcwd()}/figures/{self.mydate}'

        nfolds = len([f for f in os.listdir(os.path.dirname(self.figure_location)) if f.startswith(self.mydate.split('_')[0])])
        if nfolds:
            self.figure_location += f'_{nfolds}'
        
        print(f'Making folder at location {self.model_location}')
        os.makedirs(self.model_location, exist_ok=True)
        os.makedirs(self.figure_location, exist_ok=True)