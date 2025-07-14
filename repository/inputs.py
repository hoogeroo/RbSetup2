from artiq.experiment import *
import time

class TimedTutorial(EnvExperiment):
    """Input output test"""
    def build(self):
        self.setattr_argument("count", NumberValue(precision=0, step=1))
        self.setattr_argument("freq", NumberValue(precision=0, step=1))
        self.setattr_argument("other", NumberValue(precision=0, step=1))
        self.setattr_argument("idk", NumberValue(precision=0, step=1))

    def run(self):
        print("Hello World", self.count)
