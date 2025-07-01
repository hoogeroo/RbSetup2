import pickle
import os
import time
from PyQt5.QtWidgets import *
from datetime import datetime
import more_itertools as mi
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import multigo_window as mg
from warnings import catch_warnings
from warnings import simplefilter
from sklearn.neural_network import MLPRegressor


'''
Read:
    https://towardsdatascience.com/a-conceptual-explanation-of-bayesian-model-based-hyperparameter-optimization-for-machine-learning-b8172278050f
    https://machinelearningmastery.com/what-is-bayesian-optimization/
'''

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

class ExptOptimiser(QWidget):
    def __init__(self, params, trainingsteps = 100,filename=None, parent=None):
        super(ExptOptimiser, self).__init__(parent=parent)
        if filename:
            self.param_fname = filename
        if trainingsteps:
            self.trainingsteps = trainingsteps
            
        self.params = params
        
        for p in self.params:
          p.vals_to_try = []
          p.history = []
        
        self.reset_model()
        
        # Now that we've decided on the parameter set, decide where to shove the resulting .fits files of our runs.
        self.create_folders()
        
        self.paramhistory = []
        self.vals_to_try = []
          
        #self.doGo = self.parent().GoAction #hopefully this just pulls in the external function from allboxes.py
          # If it doesn't, we'll need to either use self.parent().GoAction() manually or rethink the order of operations.

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def create_folders(self, filename=None):
        self.mydate=datetime.now().strftime('%Y%m%d%H%M')
        if filename:
          self.param_fname = filename
          self.mydate+=f'_{filename}'
        self.model_location = f'./models/{self.mydate}'

        nfolds=len([f for f in os.listdir(self.parent().datapath) if f.startswith(self.mydate)])
        if not nfolds:
          self.foldstring = f'{self.parent().datapath}/{self.mydate}'
        else:
          self.foldstring = f'{self.parent().datapath}/{self.mydate}_{nfolds}'
        os.makedirs(self.foldstring,exist_ok = True)
        os.makedirs(self.model_location, exist_ok = True)

    def load_params(self,params):
        # Currently this is standing in for just loading in a *fresh* set of parameters.
        # We also need to save/load prior models which includes the parameters involved.
        # Future job?
        self.params=params
        self.reset_model()

    def reset_model(self):
        self.fit_model = MLPRegressor()
        self.niter = 0
        self.trainingsteps = 100
        self.training_complete = False
        for p in self.params:
            if not hasattr(p,'history'): # Make sure we have space for an independent history for each parameter
                p.history=[]

        self.history = {'trials':[],  # This is history on a per-trial basis
                        'cost':[] }          # Parameter histories are attached to the relevant parameter.

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def cost_function(self, N, OD_peak):
        if (N < 0) or (OD_peak < 0): # Guarantees that faulty determinations of N, OD_peak won't be optimal
            return 1

        # See cost function form: https://arxiv.org/abs/2205.08057, page 3
        # Needed parameters for cost:
        alpha = 2 # normally 0.5 or 1
        normaliser_lowN = 2 / (1 + np.exp(1e3/N)) # avoid divergences at small N

        # cost calculation drawn from above paper
        cost = -normaliser_lowN * OD_peak**3 * N**(alpha - 1.8) # NOTE: negative so that cost can be minimised

        return cost

    def train_model(self):
        # See https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html
        rawtrials = self.history['trials']
        if type(rawtrial[0]) is int:
          trials = mi.collapse(rawtrials)
        else:
          trials = [mi.collapse(trial) for trial in rawtrials]
        cost = self.history['cost']
        self.fit_model.fit(trials, cost) # might need np.array(self.history['trials'])

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|


    # 'surrogate', attempting to predict/approximate values determined by expt (our 'objective function')
    def get_predictions(self, X): # X = list of parameter sets - each parameter set should be list with len(params) entries.
    	# catch any warning generated when making a prediction
    	with catch_warnings():
    		# ignore generated warnings
            simplefilter("ignore")
            if type(X[0]) is int:
              #mi.collapse flattens parameter set (ramp start/end points come as lists)
                return [self.fit_model.predict(mi.collapse(X), return_std=True)] 
            else:
                 [self.fit_model.predict(mi.collapse(x), return_std=True) for x in X]
                 
    # probability of improvement acquisition function
    def sample_probabilities(self, X, Xsamples):
    	# calculate the best surrogate score found so far
    	yhat, _ = self.get_predictions(X)
    	best = max(yhat)
    	# calculate mean and stdev via surrogate function
    	mu, std = self.get_predictions(Xsamples)
    	mu = mu[:, 0]
    	# calculate the probability of improvement
    	probs = stats.norm.cdf((mu - best) / (std+1E-9))
    	return probs
     
    # optimize the acquisition function
    def suggest_optimal_params(self, X, N_psets = 1):
        N_guesses=self.trainingsteps
        if N_psets > 1:
            psets=[]
        
        for _ in range(N_psets):
        	# random search, generate random samples
            Xsamples = self.generate_params(N=N_guesses, return_trials = True)
            # calculate the acquisition function for each sample
            scores = self.sample_probabilities(X, Xsamples)
            # locate the index of the most negative scores
            ix = np.argmin(scores)
            if N_psets > 1:
                psets.append(Xsamples[ix])
                
        if N_psets == 1:
            return Xsamples[ix]
        else:
            return psets

    def generate_params(self, N=1, stdevs = None, return_trials = False):
        if return_trials:
            trials = [[] for _ in range(N)]
            
        if (stdevs != None) and (len(stdevs) != len(self.params)):
            stdevs = None
         
        for i, p in enumerate(self.params):
            # Stand-in functions to determine the min/max allowed values for the parameter
            # In reality, these will be drawn from the .mgo file
            rangemin = min([p.Startbox.value(),p.Stopbox.value()])#p.rangemin
            rangemax = max([p.Startbox.value(),p.Stopbox.value()])#p.rangemax
            stepsize = p.Startbox.singleStep()#p.stepsize # similarly, smallest unit distance between adjacent vals for the spinbox in question
            
            p_mean = (rangemin+rangemax)/2#self.get_current_value(p) # Stand-in function to retrieve current val; 
                                              #    assumes that current parameter value is 'best so far'
            if not stdevs:
              p_std = (rangemax - rangemin)/2
                #p_std = self.get_default_std(p) # I'm not sure what the best choice for a standard deviation
                                                 #     is, here. Will probably depend on type. AOM freq +-5, Power +- 0.25 etc?
            else:
                p_std = stdevs[i]
                
            a, b = (rangemin - p_mean) / p_std, (rangemax - p_mean) / p_std
                
            trunc_gaussian = stats.truncnorm(a, b, loc=p_mean, scale=p_std)
            data = trunc_gaussian.rvs(N, 1 + p.rampcheck.checkState())
            
            #if p.rampcheck.checkState():
            #    p_vals = [round(data[j,:]/stepsize)*stepsize for j in range(N)]
            #else:
            p_vals = np.around(data/stepsize)*stepsize#[round(data[j]/stepsize)*stepsize for j in range(N)]
                
            if N == 1:
              p.vals_to_try = [p_vals]
            else:
              p.vals_to_try = p_vals
            
            if return_trials:
                for j in range(N):
                    trials[j].append(p_vals[j])
        if return_trials:
            return trials

    def get_default_std(self, param):
        ptype = param.type

        if ptype is "A":
            std = 1
        elif ptype is "B":
            std = 2

        return std

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def obtain_training_data(self, n_iterations = None):
        
        # So the question is, do we draw our training samples independently,
        #       or sample randomly to begin with and then select new samples 
        #       for training based on results, to 'get best idea' of underlying model?
        # 
        # This arrangement draws all sets of parameters separately at the beginning,
        #       then iterates expt to establish costs for each set of parameters.
        #       Im not sure how to include cost variability/uncertainty in model
        #
        # Can also generate new training params during loop if we want something 'smarter'
        if not n_iterations:
            n_iterations = self.trainingsteps
        
        n_todo = n_iterations - self.niter
        if n_todo <= 0:
            print('Training has already been completed!')
            return False
        self.generate_params(N = n_todo)
        
        t_i = time.perf_counter()  
        for i in range(n_todo):
            cost, Natoms, OD_peak = self.run_expt() # Runs expt to find total atoms, peak optical density
            
            histvec=[]
            for p in self.params:
                histvec.append(p.vals_to_try[0])
                p.history.append(p.vals_to_try[0])
                p.vals_to_try = np.delete(p.vals_to_try, 0)
                
            self.history['trials'].append(histvec)
            self.history['cost'].append([cost, Natoms, OD_peak])
            
            self.niter+=1
            if self.niter <= n_iterations:
              self.parent().MLTrainLabel = QLabel(f'Training in progress: {self.niter}/{self.trainingsteps}')
            
            if not self.niter%5:
                self.save(reload_params = True)
            
            QApplication.processEvents()
            if self.parent().OptInterrupt:
                self.OptInterrupt=False
                t_f = time.perf_counter()  
                print(f'Training was stopped at the end of experiment {self.niter}, having worked for {t_f-t_i:.3f} seconds.')
                break
                return False
            time.sleep(10)
            if self.niter == n_iterations:
                self.parent().OptimiseButton.setText('Optimise')
                self.parent().OptimiseButton.setChecked(False)
                t_f = time.perf_counter()  
                print(f'Training successfully completed {npts} experiments in a time of {t_f-t_i:.3f} seconds.')
                
            
        self.train_model()
        return True

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def iterate(self, N = None):
        if not N:
            N=self.trainingsteps
        for _ in range(N):
            params_to_try = self.suggest_optimal_params(self.history['trials'])
            for i,p in enumerate(self.params):
                self.p.history.append(params_to_try[i])
            cost, Natoms, OD_peak = self.run_expt(params = params_to_try)
            
            self.history['trials'].append(params_to_try)
            self.history['cost'].append([cost,Natoms,OD_peak])
            self.train_model()
            
            self.niter+=1
            if self.niter <= self.trainingsteps:
              self.parent().MLTrainLabel = QLabel(f'Training in progress: {self.niter}/{self.optimiser.trainingsteps}')
            else:
              costvec = np.array(self.history['cost'])
              self.parent().MLBayesLabel = QLabel(f'Bayesian iterations: {self.niter-self.trainingsteps}; min cost = {np.amin(costvec[:,0])}')
            
            if not self.niter%5:
                self.save(reload_params = True)
            
            QApplication.processEvents()
            if self.parent().OptInterrupt:
                self.OptInterrupt=False
                t_f = time.perf_counter()  
                print(f'Optimisation was stopped at the end of experiment {self.niter}, having worked for {t_f-t_i:.3f} seconds.'
                      f'Final cost: {cost}; Final atom count: {Natoms}; Final peak optical density: {OD_peak}')
                break
                return False
            time.sleep(10)
        
        self.parent().OptimiseButton.setText('Optimise')
        self.parent().OptimiseButton.setChecked(False)
        t_f = time.perf_counter()  
        print(f'Optimisation successfully completed {N} experiments in a time of {t_f-t_i:.3f} seconds.\n'
              f'Final cost: {cost}; Final atom count: {Natoms}; Final peak optical density: {OD_peak}')

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def run_expt(self, params=None): 
        # Run expt and return the atom number, peak optical density
        # This is clearly a stand-in for interfacing with SEC to adjust stage values, run expt and extract numbers from the resulting image
        if not params:
          params = self.params
        self.parent().loadOptParams(params)
        self.parent().GoAction()
        
        N, OD_peak = self.parent().parent().bfcam.Natoms[-1], \
                     self.parent().parent().bfcam.ODpeak[-1]#self.obtain_expt_result()
        cost = self.cost_function(N, OD_peak) # Establishes associated cost, and saves it
        
        self.niter += 1
        
        self.parent().saveOptData(self.foldstring, self.niter)
        
        return cost, N, OD_peak
      
    def clear_params(self):
        pars=self.params.params
        for i in range(len(pars)):
            self.delpar()

#|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|
#|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|\|/|

    def save(self, reload_params=False):
        """save class as self.name.txt"""
        fname=f'{self.model_location}/{self.param_fname}'
        self.mgo_save(fname=fname)
        for p in self.params:
            self.paramhistory.append(p.history)
            self.vals_to_try.append(p.vals_to_try)
            
        self.params = []
        
        if os.path.exists(f'{fname}.pkl'):
            print("File exists")
            os.remove(name)
        with open(f'{fname}.pkl','wb') as f:
            pickle.dump(self.__dict__, f)
            
        if reload_params:
            if not fname.split('.')[-1]=='mgo':
              if fname.split('.')[-1]=='pkl':
                fname[-7:] = '.mgo'
              else:
                fname+='.mgo'
            mlpars = mg.Parameters(self.parent().devicenames,self.parent().stagenames,self.parent().tek)
            mlpars.newread(fname)
            self.params = mlpars.params
            
            for p in self.params:
                p.history = self.paramhistory.pop(0)
                p.vals_to_try = self.vals_to_try.pop(0)

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
            
            
    def mgo_save(self,fname = None):
        if not fname:
          fname = f'./{self.mydate}.mgo'
        
        if not fname.split('.')[-1]=='mgo':
          if fname.split('.')[-1]=='pkl':
            fname[-4:] = '.mgo'
          else:
            fname+='.mgo'
         
        
        if os.path.exists(fname):
           print("File exists")
           os.remove(fname)
        with open(fname,'w') as f:
          ps=self.params
          for p in ps:
            paramname = p.title.text()
            f.write(f'{paramname.replace(" ", "_")} {p.Startbox.value()} {p.Stopbox.value()} '
                    f'{p.time.currentIndex()} {p.channel.currentIndex()} {p.mytype.currentIndex()} {p.rampcheck.checkState()}\n')


    
    #def newread2(self):
        ##filename=self.namebox.text()
        #name,path = QFileDialog.getOpenFileName(self, 'Open file','./models/',"MultiGo files (*.mgo)")
        #self.newread(name)
        ##self.myread(filename)
        
    #def newread(self,filename):
        ##filename=filename+".mgo"
        ##print(filename)
        #name_root = filename[:-4]#removing the '.mgo' from the file name so that we can access other files
        #pset = mg.Parameters(self.parent().devicenames,self.parent().stagenames,self.parent().tek)
        #pset.newread(filename)
        #self.params = pset.params        

        ##print("Hello")
        
    #def mgo_save(self):
        
        
        #fn = f'{self.model_location}/{}.mgo'
        #if os.path.exists(fn):
           #print("File exists")
           #os.remove(fn)
        #f=open(fn,'w')
        #ps=self.params.params
        #for p in ps:
          #paramname = p.title.text()
          ##f.write("%s " % p.title.text())
          ##f.write("%g " % p.Startbox.value())
          ##f.write("%g " % p.Stopbox.value())
          ##f.write("%d " % p.time.currentIndex())
          ##f.write("%d " % p.channel.currentIndex())
          ##f.write("%d\n" % p.mytype.currentIndex())
          #f.write(f'{paramname.replace(" ", "_")} {p.Startbox.value()} {p.Stopbox.value()} {p.time.currentIndex()} {p.channel.currentIndex()} {p.mytype.currentIndex()}\n')
        #f.close()
        
    #def newsave(self):
        #fn=self.namebox.text()
        #if os.path.exists(fn):
           #print("File exists")
           #os.remove(fn)
        #f=open(fn,'w')
        #ps=self.params.params
        #for p in ps:
          #paramname = p.title.text()
          ##f.write("%s " % p.title.text())
          ##f.write("%g " % p.Startbox.value())
          ##f.write("%g " % p.Stopbox.value())
          ##f.write("%d " % p.time.currentIndex())
          ##f.write("%d " % p.channel.currentIndex())
          ##f.write("%d\n" % p.mytype.currentIndex())
          #f.write(f'{paramname.replace(" ", "_")} {p.Startbox.value()} {p.Stopbox.value()} {p.time.currentIndex()} {p.channel.currentIndex()} {p.mytype.currentIndex()}\n')
        #f.close()