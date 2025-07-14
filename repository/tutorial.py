from artiq.experiment import *
import time

class TimedTutorial(EnvExperiment):
    """Timed tutorial"""
    def build(self):
        pass  # no devices used

    def run(self):
        print("Hello World")
        time.sleep(10)
        print("Goodnight World")
