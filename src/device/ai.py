# AI experiment execution code
import os

from src.device.device_types import Stages
from src.device.multigo import MultiGoSettings

# settings for the AI experiment
class AiSettings:
    def __init__(self, pre_training_steps, training_steps, pre_training_model, training_model, load_file_path=None, num_runs_per_parameter_set=1):
        self.pre_training_steps = pre_training_steps
        self.training_steps = training_steps
        self.pre_training_model = pre_training_model
        self.training_model = training_model
        self.load_file_path = load_file_path  # Path to load existing model, if any
        self.num_runs_per_parameter_set = num_runs_per_parameter_set

# message to indicate AI progress to the gui
class AiProgress:
    def __init__(self, current_step, total_steps):
        self.current_step = current_step
        self.total_steps = total_steps

# message to cancel the AI experiment
class AiCancel(Exception):
    pass

class AiExecuter:
    def __init__(self, device, multigo_settings: MultiGoSettings, ai_settings: AiSettings, stages: Stages):
        self.device = device
        self.multigo_settings = multigo_settings
        self.ai_settings = ai_settings
        self.stages = stages
        self.fluorescence_threshold = multigo_settings.fluorescence_threshold
        self.total_steps = ai_settings.pre_training_steps + ai_settings.training_steps
        self.training_steps = ai_settings.training_steps
        self.pre_training_steps = ai_settings.pre_training_steps
        self.pre_training_model = ai_settings.pre_training_model
        self.training_model = ai_settings.training_model
        self.run_variables = multigo_settings.run_variables
        self.load_file_path = ai_settings.load_file_path
        self.current_step = 0
        self.optimiser = None
        self.num_runs_per_parameter_set = ai_settings.num_runs_per_parameter_set

    def run_ai_experiment(self): 
        print("Starting AI experiment...")
        try:
            self.create_mloop_interface_for_optimization()
            if not self.optimiser:
                print("Failed to create MLOOP interface, aborting AI experiment")
                raise AiCancel

            self.optimiser.iterate_start()

            self.run_mloop_optimization()  # Starts MLOOP Controller
        except AiCancel:
            print("AI experiment cancelled or failed")
            self.device.device_pipe.send(AiProgress(self.total_steps, self.total_steps))

    def start_mloop_controller(self, controller_dict):
        """Start the MLOOP controller"""
        try:
            # defer importing to speedup startup
            import mloop.controllers as mlc

            # Ensure we have a fresh interface for this optimization run
            print(f"Interface type: {type(self.optimiser)}")
            print(f"Interface boundaries: min={self.optimiser.min_boundary}, max={self.optimiser.max_boundary}")
            print(f"Number of parameters: {self.optimiser.num_params}")

            self.mloop_controller = mlc.create_controller(**controller_dict)
            print("MLOOP controller created successfully using mlc.create_controller")

        except AiCancel:
            raise
        except Exception as e:
            print(f'Error starting MLOOP controller: {e}')
            import traceback
            traceback.print_exc()
            raise AiCancel

    def run_mloop_optimization(self):
        """Run MLOOP optimization"""
        try:
            print(f'MLOOP controller starting optimization, current learner is {self.training_model}')

            # Start with config file parameters as the base, then override with explicit settings
            controller_dict = dict(self.optimiser.mloop_parameter_dict)
            controller_dict.update({
                'interface': self.optimiser,
                'max_num_runs': self.total_steps,
                'controller_type': self.training_model,
                'max_boundary': self.optimiser.max_boundary,
                'min_boundary': self.optimiser.min_boundary,
                'num_params': self.optimiser.num_params,
                'controller_archive_file_type': 'txt',
                'cost_has_noise': True,
            })

            # Only set archive filename if a load path was explicitly provided
            if self.load_file_path:
                if os.path.isfile(self.load_file_path):
                    controller_dict['training_filename'] = self.load_file_path
                    print(f'Seeding from archive file: {self.load_file_path}')
                else:
                    print(f'Warning: specified load file path does not exist: {self.load_file_path}')
                    
            if self.pre_training_steps > 0:
                print(f'Running {self.pre_training_steps} training runs for cost exploration')
                controller_dict['training_type'] = self.pre_training_model
                controller_dict['num_training_runs'] = self.pre_training_steps

            self.start_mloop_controller(controller_dict)
            self.mloop_controller.optimize()
            print('MLOOP optimization completed')
            
            # Send completion notification to GUI
            self.device.device_pipe.send(AiProgress(self.total_steps, self.total_steps))
            
        except AiCancel:
            raise
        except Exception as e:
            print(f'Error during MLOOP optimization: {e}')
            import traceback
            traceback.print_exc()
            # Send error notification to GUI
            self.device.device_pipe.send(AiProgress(self.current_step, self.total_steps))

    def create_mloop_interface_for_optimization(self):
        """Create MLOOP interface specifically for optimization run"""
        try:
            import src.device.mloop as ML

            print(f"Creating MLOOP interface with {len(self.run_variables)} parameters")
            self.optimiser = ML.MLOOPInterface(
                params = self.run_variables,
                device = self.device,
                stages = self.stages,
                pre_training_steps=self.pre_training_steps,
                fluorescence_threshold=self.fluorescence_threshold,
                trainingsteps=self.total_steps,
                num_runs_per_parameter_set=self.num_runs_per_parameter_set
            )

            print(f"Created fresh MLOOP interface: {type(self.optimiser)}")
            
        except Exception as e:
            print(f"Error creating MLOOP interface: {e}")
            import traceback
            traceback.print_exc()
            raise AiCancel