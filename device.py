from multiprocessing import Process, Pipe

from gui import Dc, DeviceSettings, run_gui
from gui_types import *

'''
Abstraction over the device to run the gui without artiq
'''
class AbstractDevice:
    def build(self):
        self.variables = [
            VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0, 'ms'),
            VariableTypeBool("Digital", "digital"),
            VariableTypeFloat("Analog", "analog"),
            VariableTypeFloat("Rf Magnitude", "rf_magnitude"),
            VariableTypeFloat("Rf Freq (MHz)", "rf_freq", 1.0, 100.0, 1.0, 'MHz')
        ]

    # spawns the gui in a separate process
    def run(self):
        # create a pipe for communication between the gui and the device
        receiver, sender = Pipe(False)

        # start the gui in a separate process
        self.gui_process = Process(target=run_gui, args=(self.variables, sender,))
        self.gui_process.daemon = True # so gui exits when main process exits
        self.gui_process.start()

        # initialize the device settings
        self.device_settings = DeviceSettings()

        # wait for the gui to send a message
        while True:
            # check for messages from the gui
            if receiver.poll(0.1):
                msg = receiver.recv()

                if type(msg) is Dc:
                    # update the device with the new values
                    self.update_dc(msg)
                elif type(msg) is list:
                    # run the experiment with the provided stages
                    self.run_experiment(msg)
                elif type(msg) is DeviceSettings:
                    # update the device settings
                    self.device_settings = msg
                elif not self.gui_process.is_alive():
                    print("GUI process has exited")
                    break
                else:
                    print(f"Received unknown message type: {type(msg)}")
                    break

            # pulse the push laser if requested
            if self.device_settings.load_mot:
                self.pulse_push_laser()

        print("Exiting...")

        # stop the gui process
        self.gui_process.terminate()
        self.gui_process.join()

    # dummy method to be overridden by the device
    def update_dc(self, dc):
        print("DC updated:", dc)

    # dummy method to be overridden by the device
    def run_experiment(self, stages):
        print("Experiment run with stages:", stages)
    
    # pulse push laser
    def pulse_push_laser(self):
        print("Pulsing push laser")

if __name__ == '__main__':
    device = AbstractDevice()
    device.build()
    device.run()

    exit(0)
