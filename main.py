'''
main.py: connects to the artiq device and starts the gui
'''

import numpy as np
import scipy as sp

from src.device.device import AbstractDevice
from src.gui import *
from src.value_types import *
from src.variable_types import *

try:
    from artiq.experiment import *

    class Device(AbstractDevice, EnvExperiment):
        def build(self):
            AbstractDevice.build(self)

            # coil_current_calibration = lambda percentage: 5.0 * percentage / 100.0

            # percentage = np.concatenate((np.arange(3, 10, 1), np.arange(10, 70, 10))) 
            # dipole_powers = np.array([23.3E-3, 59E-3, 0.165, 0.377, 0.715, 1.18, 1.79, 2.51, 14.6, 31, 49.3, 65.4, 71.1]) # in milliWatts
            # dipole_powers *= 100 / max(dipole_powers)
            # dipole_volts = 3.4 * percentage / max(percentage) # in Volts
            # dipole_calibration = np.polyfit(dipole_powers, dipole_volts, 5) # We want to put in a desired power and get back a voltage

            # initializes the variables for the device and gui
            self.variables = [
                VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 100.0),
                VariableTypeInt("Samples", "samples", 1, 10000, 100),
                VariableTypeBool("Digital", "digital"),
                VariableTypeFloat("Dipole Amplitude", "dipole_amplitude", 0.0, 3.0, 0.1),
                VariableTypeFloat("MOT 2 coils current", "mot2_coils_current", 0.0, 5.0, 0.5),
                VariableTypeFloat("x Field", "x_field", 0.0, 5.0, 0.01, hidden=True),
                VariableTypeFloat("y Field", "y_field", 0.0, 5.0, 0.01),
                VariableTypeFloat("z Field", "z_field", 0.0, 5.0, 0.01, hidden=True),
                VariableTypeFloat("Repump Amplitude", "repump_amplitude"),
                VariableTypeFloat("Repump Frequency (MHz)", "repump_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("1st MOT Amplitude", "mot1_amplitude"),
                VariableTypeFloat("1st MOT Frequency (MHz)", "mot1_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("2nd MOT Amplitude", "mot2_amplitude"),
                VariableTypeFloat("2nd MOT Frequency (MHz)", "mot2_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Push Amplitude", "push_amplitude"),
                VariableTypeFloat("Push Frequency (MHz)", "push_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Shadow Amplitude", "shadow_amplitude"),
                VariableTypeFloat("Shadow Frequency (MHz)", "shadow_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Optical Pump Amplitude", "optical_pump_amplitude"),
                VariableTypeFloat("Optical Pump Frequency (MHz)", "optical_pump_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Sheet Amplitude", "sheet_amplitude"),
                VariableTypeFloat("Sheet Frequency (MHz)", "sheet_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("RF Amplitude", "RF_amplitude"),
                VariableTypeFloat("RF Frequency (MHz)", "RF_frequency", 0, 100.0, 1.0),
                VariableTypeBool("Shutter", "shutter"),
                VariableTypeBool("Grey Molasses Shutter", "grey_molasses_shutter"),
                VariableTypeBool("RF Disable", "rf_disable"),

                # VariableTypeBool("RF Freq Ramp", "rf_freq_ramp"),
            ]

            self.setattr_device("core")
            self.setattr_device("ttl5")
            self.setattr_device("ttl6")
            self.setattr_device('fastino0')
            self.setattr_device("sampler0")
            # self.setattr_device('urukul0_ch0')
            # self.setattr_device('urukul0_ch1')
            # self.setattr_device('urukul0_ch2')
            # self.setattr_device('urukul0_ch3')
            # self.setattr_device('urukul1_ch0')
            # self.setattr_device('urukul1_ch1')
            # self.setattr_device('urukul1_ch2')

        @host_only
        def run(self):
            self.init_device()

            # runs the gui in a separate process
            AbstractDevice.run(self)

        @kernel
        def init_device(self):
            self.core.reset()
            self.fastino0.init()
            self.sampler0.init()
            self.sampler0.set_gain_mu(0, 0)
            # urukul_channels = ["urukul0_ch0", "urukul0_ch1", "urukul0_ch2", "urukul0_ch3", "urukul1_ch0", "urukul1_ch1", "urukul1_ch2"]
            # for ch in urukul_channels:
            #     getattr(self, ch).cpld.init()
            #     getattr(self, ch).init()
            #     getattr(self, ch).cfg_sw(True)
            #     getattr(self, ch).set_att(6.0 * dB)

        @kernel
        def run_experiment_device(self, flattened_stages):
            # reset the cores timer for the new experiment
            self.core.break_realtime()

            # iterate through the stages and get their values
            s = flattened_stages
            for i in range(len(s.time)):
                # update digital output
                if s.digital[i]:
                    self.ttl5.on()
                else:
                    self.ttl5.off()

                # update analog outputs
                dac = [0.0] * 32
                dac[0] = 5.0 if s.shutter[i] else 0.0
                dac[1] = 5.0 if s.grey_molasses_shutter[i] else 0.0
                dac[2] = s.mot2_coils_current[i] 
                dac[3] = s.x_field[i]
                dac[4] = s.y_field[i]
                dac[5] = s.z_field[i]
                dac[6] = s.dipole_amplitude[i]
                dac[7] = 5.0 if s.rf_disable[i] else 0.0
                self.fastino0.set_group(0, dac)

                # update rf output
                # self.urukul0_ch0.set(
                #     s.repump_frequency[i] * MHz,
                #     amplitude=s.repump_amplitude[i] * 0.6
                # )
                # self.urukul0_ch1.set(
                #     s.mot1_frequency[i] * MHz,
                #     amplitude=s.mot1_amplitude[i] * 0.6
                # )
                # self.urukul0_ch2.set(
                #     s.mot2_frequency[i] * MHz,
                #     amplitude=s.mot2_amplitude[i] * 0.6
                # )
                # self.urukul0_ch3.set(
                #     s.push_frequency[i] * MHz,
                #     amplitude=s.push_amplitude[i] * 0.6
                # )
                # self.urukul1_ch0.set(
                #     s.shadow_frequency[i] * MHz,
                #     amplitude=s.shadow_amplitude[i] * 0.6
                # )
                # self.urukul1_ch1.set(
                #     s.sheet_frequency[i] * MHz,
                #     amplitude=s.sheet_amplitude[i] * 0.6
                # )
                # self.urukul1_ch2.set(
                #     s.optical_pump_frequency[i] * MHz,
                #     amplitude=s.optical_pump_amplitude[i] * 0.6
                # )

                # wait for a short time to simulate the experiment duration
                delay(s.time[i] * ms)

        @kernel
        def pulse_push_laser(self):
            # push the laser for a short time
            self.core.break_realtime()
            self.ttl6.on()
            delay(10 * ms)
            self.ttl6.off()

        @kernel
        def read_fluorescence(self) -> float:
            # read the fluorescence signal
            self.core.break_realtime()
            sample = [0.0]*8
            self.sampler0.sample(sample)
            return -1000.0 * sample[0]

# if artiq isn't available run the gui without it
except ImportError:
    if __name__ == "__main__":
        device = AbstractDevice()
        device.build()
        device.run()
