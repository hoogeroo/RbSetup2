from artiq.experiment import *

class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device("hello")
    def run(self):
        self.hello.message("Hello World!")