#Imports for M-LOOP
import mloop.interfaces as mli
import mloop.controllers as mlc
import mloop.visualizations as mlv

#Other imports
import matplotlib.pyplot as plt
import numpy as np
import time
import threading
import pickle
import os
from datetime import datetime
from PyQt5.QtWidgets import *
import re


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Default path for MLOOP files
mloop_default_path = '/home/lab/mydata/Data/MLOOP_files'
mloop_run_parameter_path = '/home/lab/mydata/Programming/newsetup/pyqtgui/mloop_config.txt'
#Declare your custom class that inherits from the Interface class
class MLOOPInterface(QWidget, mli.Interface):

    #Initialization of the interface, including this method is optional
    def __init__(self, params, trainingsteps = 100,filename=None, folder=None, parent=None):
        #You must include the super command to call the parent class, Interface, constructor
        super(MLOOPInterface, self).__init__(parent=parent)

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
          figloc_fragment = SPLIT_CHAR.join(folder.split(SPLIT_CHAR)[-2:])
          self.figure_location = f'{self.parent().datapath}/{figloc_fragment}'
        else:
          self.create_folders(filename = self.param_fname)

        #Attributes of the interface can be added here
        #If you want to precalculate any variables etc. this is the place to do it
        #In this example we will just define the location of the minimum
        self.minimum_params = np.array([0,0.1,-0.1])

    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

    #You must include the get_next_cost_dict method in your class
    #this method is called whenever M-LOOP wants to run an experiment
    def get_next_cost_dict(self,params_dict):

        #Get parameters from the provided dictionary
        mloop_params = params_dict['params']

        # Put parameters into form for pyqtgui program
        self.MLOOP_parameters_to_pyqtgui_parameters(mloop_params)


        # Start the timer to begin the experiment
        for i in range(0,self.parent().multitriggerspinbox.value()):
            print(f'begining experiment iteration {i}')
            if self.continue_mloop.is_set():
                self.continue_mloop.clear()
            self.parent().t_initial = time.time()
            self.parent().ML_active = True
            # Wait to get the experimental data
            self.continue_mloop.wait()
            self.continue_mloop.clear()
            if self.parent().experiment_success:
                #Times.append(self.parent().spcm.data[-1])
                #Count.append(self.parent().spcm.data_count[-1])
                Natoms, OD_peak = self.parent().parent().bfcam.Natoms[-1], \
                     self.parent().parent().bfcam.ODpeak[-1]#self.obtain_expt_result()
                  
            else:
                print('Ending experiment due to no data from experiment')

                self.user_halt_event.set()
        if self.parent().experiment_success:
            #cost, uncer, bad = self.cost_function(Times,Count)
            cost, uncer, bad = cost_function(Natoms, OD_peak)
        else:
            cost, uncer, bad = self.cost_function(0,0)
        histvec=[]
        for p in self.params:
          ptype = type(p.vals_to_try)

          if (ptype is int or ptype is np.float64 or ptype is float):
            histvec.append(p.vals_to_try)
            p.history.append(p.vals_to_try)
            p.vals_to_try = None
          elif ptype is not None or ptype:
            #print(p.vals_to_try)
            histvec.append(p.vals_to_try[0])
            p.history.append(p.vals_to_try[0])
            p.vals_to_try = np.delete(p.vals_to_try, 0)
        if cost > 0:#if Natoms > 1e4:
            self.history['trials'].append(histvec)
            self.history['cost'].append([cost,Natoms,OD_peak])
            #self.history['cost'].append([cost,Times,Count,uncer])

            self.plotcost()

        #The cost, uncertainty and bad boolean must all be returned as a dictionary
        #You can include other variables you want to record as well if you want
        cost_dict = {'cost':cost, 'uncer':uncer, 'bad':bad}
        self.run_num += 1
        return cost_dict


    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

    #def cost_function(self, arrival_times, photon_count):
        #is_bad_result = False
        #if any(np.array(photon_count)<0): # Guarantees that faulty determinations of N, OD_peak won't be optimal
            #print('Warning bad data from SPCM, data to cost function showing counts less than 0')
            #is_bad_result = True

        #if any(np.array(photon_count)==0):
            #print('Warning bad data from SPCM, data to cost function showing counts of 0')
            #is_bad_result = True

        #if len(photon_count)==1:
            #uncertainty = photon_count[0]**(1/2)
            #cost = photon_count[0]
        #else:
            #uncertainty = np.std(photon_count)
            #cost = np.mean(photon_count)

        #return cost, uncertainty, is_bad_result
        
    def cost_function(self, N, OD_peak):
        # !! Uncertainty is not correct, just using placeholder
        is_bad_result = False
        maximum_cost = 9e99
        
        if (N <= 0) or (OD_peak <= 0): # Guarantees that faulty determinations of N, OD_peak won't be optimal
            is_bad_result = True
            cost = maximum_cost

        # See cost function form: https://arxiv.org/abs/2205.08057, page 3
        # Needed parameters for cost:
        alpha = 2 # normally 0.5 or 1
        normaliser_lowN = 2 / (1 + np.exp(1e3/N)) # avoid divergences at small N

        # cost calculation drawn from above paper
        cost = normaliser_lowN * OD_peak**3 * N**(alpha - 1.8) # NOTE: negative so that cost can be minimised
        return cost, np.sqrt(cost), is_bad_result

    def iterate_start(self, n_iterations = None):
        print('Populating MLOOP parameters')
        # Get parameters required for the machine learning controller
        self.Populate_MLOOP_parameters()


    def iterate_end(self):
        print('ML Experiment was carried out')
        self.parent().ML_active = False
        self.continue_mloop.set()

    def iterate_stop(self, cancelled = False):
        self.parent().ML_active = False
        self.continue_mloop.set()
        self.user_halt_event.set()
        if cancelled:
            print('Machine learning cancelled by user')
        self.parent().OptimiseButton.setText('Optimise')
        self.parent().OptimiseButton.setChecked(False)


    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

    def load_params(self,params):
        # Currently this is standing in for just loading in a *fresh* set of parameters.
        # We also need to save/load prior models which includes the parameters involved.
        # Future job?
        self.params=params
        self.reset_model()

    def create_folders(self, filename=None):
        self.mydate=datetime.now().strftime('%Y%m%d%H%M')
        if filename:
          self.param_fname = filename
          self.mydate+=f'_{filename.replace(" ","-")}'

        self.model_location = f'{os.getcwd()}/models/{self.mydate}'
        self.figure_location = f'{self.parent().datapath}/models/{self.mydate}'

        nfolds=len([f for f in os.listdir(self.parent().datapath) if f.startswith(self.mydate)])
        if nfolds:
          self.figure_location+= '_{nfolds}'
        print(f'Making folder at location {self.model_location}')
        os.makedirs(self.model_location, exist_ok = True)
        os.makedirs(self.figure_location, exist_ok = True)

    def save(self, reload_params=False):
        """save class as self.name.txt"""
        fname=f'{self.model_location}/{self.param_fname.replace(" ","-")}'
        self.mgo_save(fname=fname)
        if hasattr(self, 'paramhistory'):
            for p in self.params:
                self.paramhistory.append(p.history)
                self.vals_to_try.append(p.vals_to_try)

        self.params = []

        if os.path.exists(f'{fname}.pkl'):
            print("File exists")
            os.remove(f'{fname}.pkl')
        with open(f'{fname}.pkl','wb') as f:
            pickle.dump(self.__dict__, f)

        if reload_params:
            if not fname.split('.')[-1]=='mgo':
              if fname.split('.')[-1]=='pkl':
                fname[-3:] = 'mgo'
              else:
                fname+='.mgo'
            mlpars = mg.Parameters(self.parent().devicenames,self.parent().stagenames,self.parent().tek)
            mlpars.newread(fname)
            self.params = mlpars.params
            #try:

            for p in self.params:
                p.history = self.paramhistory.pop(0)
                p.vals_to_try = self.vals_to_try.pop(0)
            #except:
            #    print('No prior history to include')


    def load(self, params, name = None):
        """try load self.name.txt"""
        if name:
            with open(name,'rb') as f:
                self.__dict__ = pickle.load(f)

            self.params = params

            for p in self.params:
                p.history = self.paramhistory.pop(0)
                p.vals_to_try = self.vals_to_try.pop(0)
        else:
          self.load_params(params)

    def plotcost(self):

        cost = [x[0] for x in self.history['cost']]
        cost_uncer = [x[3] for x in self.history['cost']]
        all_parameters = np.array(self.history['trials'][-1])
        #print(f'Length of trials is {len(all_parameters)} or {len(all_parameters[:][0])}, number of parameters is {len(all_parameters[0][:])}')

        exptnum = list(range(len(cost)))

        fig = self.parent().figure_MachineLearning
        if self.run_num == 0:
            fig.clf()
            self.parent().ax_ML_ax_costVsRunNumber = fig.add_subplot(221)
            self.parent().ax_ML_ax_NormParamVsRunNumber = fig.add_subplot(222)
            self.parent().ax_ML_ax_ParamVsRunNumber = fig.add_subplot(223)
            self.parent().ax_ML_ax_CostVsParam = fig.add_subplot(224)
        ax_costVsRunNumber = self.parent().ax_ML_ax_costVsRunNumber
        ax_NormParamVsRunNumber = self.parent().ax_ML_ax_NormParamVsRunNumber
        ax_ParamVsRunNumber = self.parent().ax_ML_ax_ParamVsRunNumber
        ax_CostVsParam = self.parent().ax_ML_ax_CostVsParam



        # Cost Vs Run number
        #ax_costVsRunNumber.plot(exptnum[-1], cost[-1],'o',color=self.colors[0])
        ax_costVsRunNumber.errorbar(exptnum[-1],cost[-1],cost_uncer[-1], fmt='o', capsize=5, markersize=4, elinewidth=2,color=self.colors[0])
        ax_costVsRunNumber.set_xlabel('Expt. Number')
        ax_costVsRunNumber.set_ylabel('Cost')

        # Normalized Parameter vs Run number
        for i in range(0, len(all_parameters)):
            norm_param_vec = self.normalize_parameter(all_parameters[i], self.min_boundary[i], self.max_boundary[i])
            ax_NormParamVsRunNumber.plot(exptnum[-1], norm_param_vec,'o',color=self.colors[i%10])
        ax_NormParamVsRunNumber.set_xlabel('Expt. Number')
        ax_NormParamVsRunNumber.set_ylabel('Normalized Parameter value')
        ax_NormParamVsRunNumber.legend(self.param_names)

        # Parameter vs Run number
        for i in range(0, len(all_parameters)):
            ax_ParamVsRunNumber.plot(exptnum[-1], all_parameters[i],'o',color=self.colors[i%10])
        ax_ParamVsRunNumber.set_xlabel('Expt. Number')
        ax_ParamVsRunNumber.set_ylabel('Parameter value')
        #ax_ParamVsRunNumber.legend(self.param_names)

        # Cost vs Parameter
        for i in range(0, len(all_parameters)):
            ax_CostVsParam.errorbar(all_parameters[i],cost[-1],cost_uncer[-1], fmt='o', capsize=5, markersize=4, elinewidth=2,color=self.colors[i%10])
            #ax_CostVsParam.plot(all_parameters[i], cost[-1],'o',color=self.colors[i%10])
        ax_CostVsParam.set_ylabel('Cost')
        ax_CostVsParam.set_xlabel('Parameter value')
        #ax_CostVsParam.legend(self.param_names)





        fig.tight_layout()
        self.parent().canvas_MachineLearning.draw_idle()
        print('costplot finished??')

    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

    def normalize_parameter(self,param,pmin,pmax):
        norm_param = (param - pmin)/(pmax - pmin)
        return norm_param

    def reset_model(self):
        self.max_boundary = []
        self.min_boundary = []
        self.num_params = 0
        self.param_names = []
        for p in self.params:
            if not hasattr(p,'history'): # Make sure we have space for an independent history for each parameter
                p.history=[]

        self.history = {'trials':[],  # This is history on a per-trial basis
                        'cost':[] }          # Parameter histories are attached to the relevant parameter.

    def MLOOP_parameters_to_pyqtgui_parameters(self,mloop_parameters):
        for i, p in enumerate(self.params):
            temp = mloop_parameters[i]
            stepsize = p.Startbox.singleStep()
            temp = np.array((round(temp/stepsize))*stepsize)
            p.vals_to_try = [temp]

    def Populate_MLOOP_parameters(self):

        self.mloop_parameter_dict = {}


        for i, p in enumerate(self.params):
            rangemin = min([p.Startbox.value(),p.Stopbox.value()])#p.rangemin
            rangemax = max([p.Startbox.value(),p.Stopbox.value()])#p.rangemax
            self.param_names.append(p.title.text())
            self.max_boundary.append(rangemax)
            self.min_boundary.append(rangemin)
            self.num_params = i + 1

        self.mloop_parameter_dict['max_boundary'] = self.max_boundary
        self.mloop_parameter_dict['min_boundary'] = self.min_boundary
        self.mloop_parameter_dict['num_params'] = self.num_params
        self.mloop_parameter_dict['param_names'] = self.param_names

        with open(mloop_run_parameter_path) as open_file:
            mloop_file_lines = open_file.read().splitlines()

        for i,line in enumerate(mloop_file_lines):
            split_line = line.split(' = ')
            if split_line[0][0] != '#' and split_line[0][0] != '' and split_line[0][0] != ' ':

                if len(split_line) > 2:
                    print('Error in reading mloop parameter file, a line was not formated correctly')

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

        # paths for saving output
        self.mloop_parameter_dict['controller_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_controller'
        self.mloop_parameter_dict['learner_archive_filename'] = f'{mloop_default_path}/{self.param_fname}_learner'

def main():
    #M-LOOP can be run with three commands

    #First create your interface
    interface = CustomInterface()
    #Next create the controller. Provide it with your interface and any options you want to set
    controller = mlc.create_controller(interface,
                                       max_num_runs = 1000,
                                       target_cost = -2.99,
                                       num_params = 3,
                                       min_boundary = [-2,-2,-2],
                                       max_boundary = [2,2,2])
    #To run M-LOOP and find the optimal parameters just use the controller method optimize
    controller.optimize()

    #The results of the optimization will be saved to files and can also be accessed as attributes of the controller.
    print('Best parameters found:')
    print(controller.best_params)

    #You can also run the default sets of visualizations for the controller with one command
    mlv.show_all_default_visualizations(controller)

def run_controller(custom_interface,max_runs):
    print('Creating Controller and starting optimize')
    #Next create the controller. Provide it with your interface and any options you want to set
    custom_interface.continue_mloop.clear()
    custom_interface.run_num = 0


    controller = mlc.create_controller(custom_interface,
                                    controller_type = custom_interface.controller_type,
                                    **custom_interface.mloop_parameter_dict)

    print('Creating Controller and starting optimize')
    #To run M-LOOP and find the optimal parameters just use the controller method optimize
    controller.optimize()

    #The results of the optimization will be saved to files and can also be accessed as attributes of the controller.
    print('Best parameters found:')
    print(controller.best_params)

    custom_interface.parent().ML_active = False
    custom_interface.parent().OptimiseButton.setText('Optimise')
    custom_interface.parent().OptimiseButton.setChecked(False)




#Ensures main is run when this code is run as a script
if __name__ == '__main__':
    main()
