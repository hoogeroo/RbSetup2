'''
main.py: connects to the artiq device and starts the gui
'''

import numpy as np
import scipy as sp

from src.device.device import AbstractDevice
from src.gui import *
from src.value_types import *

try:
    from artiq.experiment import *

    class Device(AbstractDevice, EnvExperiment):
        def build(self):
            # initializes the variables for the device and gui
            AbstractDevice.build(self)

            self.setattr_device("core")
            self.setattr_device("ttl5")
            self.setattr_device("ttl6")
            self.setattr_device('fastino0')
            self.setattr_device("sampler0")
            self.setattr_device('urukul0_ch0')
            self.setattr_device('urukul0_ch1')
            self.setattr_device('urukul0_ch2')
            self.setattr_device('urukul0_ch3')
            self.setattr_device('urukul1_ch0')
            self.setattr_device('urukul1_ch1')
            self.setattr_device('urukul1_ch2')

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
            self.urukul0_ch0.cpld.init()
            self.urukul0_ch0.init()
            self.urukul0_ch0.cfg_sw(True)
            self.urukul0_ch0.set_att(6.0 * dB)
            self.urukul0_ch1.cpld.init()
            self.urukul0_ch1.init()
            self.urukul0_ch1.cfg_sw(True)
            self.urukul0_ch1.set_att(6.0 * dB)
            self.urukul0_ch2.cpld.init()
            self.urukul0_ch2.init()
            self.urukul0_ch2.cfg_sw(True)
            self.urukul0_ch2.set_att(6.0 * dB)
            self.urukul0_ch3.cpld.init()
            self.urukul0_ch3.init()
            self.urukul0_ch3.cfg_sw(True)
            self.urukul0_ch3.set_att(6.0 * dB)
            self.urukul1_ch0.cpld.init()
            self.urukul1_ch0.init()
            self.urukul1_ch0.cfg_sw(True)
            self.urukul1_ch0.set_att(6.0 * dB)
            self.urukul1_ch1.cpld.init()
            self.urukul1_ch1.init()
            self.urukul1_ch1.cfg_sw(True)
            self.urukul1_ch1.set_att(6.0 * dB)
            self.urukul1_ch2.cpld.init()
            self.urukul1_ch2.init()
            self.urukul1_ch2.cfg_sw(True)
            self.urukul1_ch2.set_att(6.0 * dB)

        # for some reason the `Dc` class type hint doesn't work but at runtime it works
        @kernel
        def update_dc(self, dc):
            self.core.break_realtime()

            # update digital output
            if dc.digital:
                self.ttl5.on()
            else:
                self.ttl5.off()

            # update analog outputs
            dac = [0.0] * 32
            dac[0] = 5.0 if dc.shutter else 0.0
            dac[1] = 5.0 if dc.grey_molasses_shutter else 0.0
            dac[2] = dc.mot2_coils_current 
            dac[3] = dc.x_field
            dac[4] = dc.y_field
            dac[5] = dc.z_field
            dac[6] = dc.dipole_amplitude
            self.fastino0.set_group(0, dac)

            # update rf output
            self.urukul0_ch0.set(
                dc.repump_frequency * MHz,
                amplitude=dc.repump_amplitude * 0.6
            )
            self.urukul0_ch1.set(
                dc.mot1_frequency * MHz,
                amplitude=dc.mot1_amplitude * 0.6
            )
            self.urukul0_ch2.set(
                dc.mot2_frequency * MHz,
                amplitude=dc.mot2_amplitude * 0.6
            )
            self.urukul0_ch3.set(
                dc.push_frequency * MHz,
                amplitude=dc.push_amplitude * 0.6
            )
            self.urukul1_ch0.set(
                dc.shadow_frequency * MHz,
                amplitude=dc.shadow_amplitude * 0.6
            )
            self.urukul1_ch1.set(
                dc.sheet_frequency * MHz,
                amplitude=dc.sheet_amplitude * 0.6
            )
            self.urukul1_ch2.set(
                dc.optical_pump_frequency * MHz,
                amplitude=dc.optical_pump_amplitude * 0.6
            )

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

                # update analog output
                self.fastino0.set_dac(0, s.analog[i])

                # update rf output
                self.urukul0_ch0.set(s.rf_freq[i] * MHz, amplitude=s.rf_magnitude[i])

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
