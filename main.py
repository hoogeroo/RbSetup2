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
    from artiq.coredevice import sampler

    class Device(AbstractDevice, EnvExperiment):
        def build(self):
            AbstractDevice.build(self)

            coil_current_calibration = lambda percentage: 5.0 * percentage / 100.0

            percentage = np.concatenate((np.arange(3, 10, 1), np.arange(10, 70, 10))) 
            dipole_powers = np.array([23.3E-3, 59E-3, 0.165, 0.377, 0.715, 1.18, 1.79, 2.51, 14.6, 31, 49.3, 65.4, 71.1]) # in milliWatts
            dipole_powers *= 100 / max(dipole_powers)
            dipole_volts = 3.4 * percentage / max(percentage) # in Volts
            dipole_calibration = np.poly1d(np.polyfit(dipole_powers, dipole_volts, 5)) # We want to put in a desired power and get back a voltage

            sheet_powers = np.array([0.75,0.96,1.62,2.65,3.95,5.43,6.99,8.49,9.81,10.83,11.57,11.97,12.01])
            sheet_powers -= min(sheet_powers)
            sheet_powers *= 100.0 / max(sheet_powers)
            sheet_volts = np.linspace(0, 1.3, len(sheet_powers))
            sheet_calibration = np.poly1d(np.polyfit(sheet_powers, sheet_volts, 5))

            # initializes the variables for the device and gui
            self.variables = [
                VariableTypeFloat("Time (ms)", "time", 0.0, 10000.0, 10.0),
                VariableTypeInt("Samples", "samples", 1, 10000, 100),
                VariableTypeBool("Camera", "camera"),
                VariableTypeFloat("Analog", "analog", -10.0, 10.0, 0.1),
                VariableTypeFloat("Dipole Amplitude", "dipole_amplitude", 0.0, 100.0, 0.5, calibration=dipole_calibration),
                VariableTypeFloat("MOT 2 coils current", "mot2_coils_current", 0.0, 100.0, 0.5, calibration=coil_current_calibration),
                VariableTypeFloat("x Field", "x_field", -5.0, 5.0, 0.01, hidden=True),
                VariableTypeFloat("y Field", "y_field", -5.0, 5.0, 0.01),
                VariableTypeFloat("z Field", "z_field", -5.0, 5.0, 0.01, hidden=True),
                VariableTypeFloat("Repump Amplitude", "repump_amplitude"),
                VariableTypeFloat("Repump Frequency (MHz)", "repump_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("1st MOT Amplitude", "mot1_amplitude", hidden=True),
                VariableTypeFloat("1st MOT Frequency (MHz)", "mot1_frequency", 55.0, 120.0, 1.0, hidden=True),
                VariableTypeFloat("2nd MOT Amplitude", "mot2_amplitude"),
                VariableTypeFloat("2nd MOT Frequency (MHz)", "mot2_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Push Amplitude", "push_amplitude", hidden=True),
                VariableTypeFloat("Push Frequency (MHz)", "push_frequency", 55.0, 120.0, 1.0, hidden=True),
                VariableTypeFloat("Shadow Amplitude", "shadow_amplitude"),
                VariableTypeFloat("Shadow Frequency (MHz)", "shadow_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Optical Pump Amplitude", "optical_pump_amplitude"),
                VariableTypeFloat("Optical Pump Frequency (MHz)", "optical_pump_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("Sheet Amplitude", "sheet_amplitude", 0.0, 100.0, 0.5, calibration=sheet_calibration),
                VariableTypeFloat("Sheet Frequency (MHz)", "sheet_frequency", 55.0, 120.0, 1.0),
                VariableTypeFloat("RF Amplitude", "rf_amplitude", hidden=True),
                VariableTypeFloat("RF Frequency (MHz)", "rf_frequency", 0, 100.0, 1.0),
                VariableTypeBool("Shutter", "shutter"),
                VariableTypeBool("Grey Molasses Shutter", "grey_molasses_shutter"),
                VariableTypeBool("RF Disable", "rf_disable"),
                VariableTypeBool("Flip Mirror", "flip_mirror"),
            ]

            self.setattr_device("core")
            self.setattr_device("ttl0")   # SLM sync input 
            self.setattr_device("ttl4")
            self.setattr_device("ttl5")
            self.setattr_device("ttl7")   # SLM frame-advance trigger
            self.setattr_device('fastino0')
            self.setattr_device("sampler0")
            self.setattr_device('urukul0_ch0')
            self.setattr_device('urukul0_ch1')
            self.setattr_device('urukul0_ch2')
            self.setattr_device('urukul0_ch3')
            self.setattr_device('urukul1_ch0')
            self.setattr_device('urukul1_ch1')
            self.setattr_device('urukul1_ch2')
            self.setattr_device('urukul1_ch3')

        @host_only
        def run(self):
            self.init_device()

            # runs the gui in a separate process
            AbstractDevice.run(self)

        @kernel
        def init_device(self):
            self.core.reset()
            self.ttl0.input()  # configure TTL0 as SLM sync input
            self.fastino0.init()
            self.sampler0.init()
            self.sampler0.set_gain_mu(0, 0)
            self.urukul0_ch0.cpld.init()
            self.urukul0_ch0.init()
            self.urukul0_ch0.cfg_sw(True)
            self.urukul0_ch0.set_att(6.0 * dB)
            self.urukul0_ch1.cpld.init()
            self.urukul0_ch1.init()
            self.urukul0_ch1.set_att(6.0 * dB)
            self.urukul0_ch1.cfg_sw(False) # allows for fast switching using ttl
            self.urukul0_ch2.cpld.init()
            self.urukul0_ch2.init()
            self.urukul0_ch2.cfg_sw(True)
            self.urukul0_ch2.set_att(6.0 * dB)
            self.urukul0_ch3.cpld.init()
            self.urukul0_ch3.init()
            self.urukul0_ch3.set_att(6.0 * dB)
            self.urukul0_ch3.cfg_sw(False) # allows for fast switching using ttl
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
            self.urukul1_ch3.cpld.init()
            self.urukul1_ch3.init()
            self.urukul1_ch3.cfg_sw(True)
            self.urukul1_ch3.set_att(6.0 * dB)

        @kernel
        def _run_slm_phase(self, slm_hold_times, n_slm_frames):
            """
            Waits for a single sync pulse on TTL0 at the start to confirm
            the SLM is ready on the first frame, then runs through all
            frames using fixed hold durations and TTL7 advance pulses.
            """

            gate_end_mu = self.ttl0.gate_rising(50.0 * ms)
            sync_ts = self.ttl0.timestamp_mu(gate_end_mu)

            if sync_ts >= 0:
                at_mu(sync_ts)
                delay(10.0 * us)  # small margin after the edge
            else:
                # No sync pulse — SLM is not responding, abort the phase
                return

            # run through each frame
            for frame in range(n_slm_frames):
                # Hold for this frame's configured duration
                delay(slm_hold_times[frame] * ms)

                # Pulse TTL7 to advance the SLM to the next frame
                if frame < n_slm_frames - 1:
                    self.ttl7.pulse(1.0 * ms)
                    delay(1.0 * ms)  # settling time

        @kernel
        def run_experiment_device(self, flattened_stages, slm_hold_times, slm_insertion_index, slm_enabled):
            # reset the cores timer for the new experiment
            self.core.break_realtime()

            self.ttl7.off()

            # determine whether an SLM phase is active
            n_slm_frames = len(slm_hold_times)
            has_slm = slm_enabled and n_slm_frames > 0

            # iterate through the stages and get their values
            s = flattened_stages
            for i in range(len(s.time)):
                if has_slm and i == slm_insertion_index:
                    self._run_slm_phase(slm_hold_times, n_slm_frames)

                # update camera trigger
                if s.camera[i]:
                    self.ttl4.on()
                else:
                    self.ttl4.off()

                # update flip mirror and camera shutter
                if s.flip_mirror[i]:
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
                dac[8] = s.analog[i]
                self.fastino0.set_group(0, dac)

                # update rf output
                self.urukul0_ch0.set(
                    s.repump_frequency[i] * MHz,
                    amplitude=s.repump_amplitude[i] * 0.6
                )
                self.urukul0_ch1.set(
                    s.mot1_frequency[i] * MHz,
                    amplitude=s.mot1_amplitude[i] * 0.6
                )
                self.urukul0_ch2.set(
                    s.mot2_frequency[i] * MHz,
                    amplitude=s.mot2_amplitude[i] * 0.6
                )
                self.urukul0_ch3.set(
                    s.push_frequency[i] * MHz,
                    amplitude=s.push_amplitude[i] * 0.6
                )
                self.urukul1_ch0.set(
                    s.shadow_frequency[i] * MHz,
                    amplitude=s.shadow_amplitude[i] * 0.6
                )
                self.urukul1_ch1.set(
                    s.optical_pump_frequency[i] * MHz,
                    amplitude=s.optical_pump_amplitude[i] * 0.6
                )
                self.urukul1_ch2.set(
                    s.sheet_frequency[i] * MHz,
                    amplitude=s.sheet_amplitude[i] * 0.6
                )
                self.urukul1_ch3.set(
                    s.rf_frequency[i] * MHz,
                    amplitude=s.rf_amplitude[i] * 0.6
                )

                # wait for the duration of the stage
                delay(s.time[i] * ms)

            # SLM phase after all stages
            if has_slm and slm_insertion_index >= len(s.time):
                self._run_slm_phase(slm_hold_times, n_slm_frames)

            # make sure experiment is finished before returning
            self.core.wait_until_mu(now_mu() + 1 * ms)

        @kernel
        def pulse_push_laser(self):
            # push the laser for a short time
            self.core.break_realtime()

            self.urukul0_ch3.sw.on()
            self.urukul0_ch1.sw.off()

            delay(10*ms)

            self.urukul0_ch3.sw.off()
            self.urukul0_ch1.sw.on()

        @kernel
        def read_fluorescence(self) -> float:
            # read the fluorescence signal
            self.core.break_realtime()
            sample = [0.0]*8
            self.sampler0.sample(sample)
            return -1000.0 * sample[3]

# if artiq isn't available run the gui without it
except ImportError:
    if __name__ == "__main__":
        device = AbstractDevice()
        device.build()
        device.run()
