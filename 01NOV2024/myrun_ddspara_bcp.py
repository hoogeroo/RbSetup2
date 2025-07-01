from artiq.experiment import *
import numpy as np
import json

class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('core_dma')
        self.setattr_device('fastino0')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch0')
        self.setattr_device('urukul0_ch1')
        self.setattr_device('urukul0_ch2')
        self.setattr_device('urukul0_ch3')
        # Add channels as needed

    def prepare(self):
        with open("stages.json", "r") as f:
            stages = json.load(f)
        self.voltage_arrays = [np.array(stage[0]) for stage in stages]
        self.timesteps = [stage[2] for stage in stages]
        self.channel_settings = [stage[1] for stage in stages]  # Channel settings

    @kernel
    def record(self):
        with self.core_dma.record("test"):
            for i in range(len(self.voltage_arrays)):
                voltages = self.voltage_arrays[i]
                timestep = self.timesteps[i]
                channels = self.channel_settings[i]  # Get frequency/amplitude/channel data
                array = [0.0] * 32  # Create array to set voltages to Fastino
                ch0_freq, ch0_amp = channels[0][0],channels[0][1]
                ch1_freq, ch1_amp = channels[1][0],channels[1][1]
                ch2_freq, ch2_amp = channels[2][0],channels[2][1]
                ch3_freq, ch3_amp = channels[3][0],channels[3][1]
                # Set first 8 values to Fastino DAC
                delay(20*ms)
                for j in range(8):  
                    array[j] = voltages[j]
                with parallel:
                  
                    self.fastino0.set_group(0, array)
                    #delay(1*ms)
                    if True:
                        self.urukul0_ch0.set(frequency = int(ch0_freq)*MHz, amplitude = ch0_amp)
                        #delay(1*ms)
                        self.urukul0_ch1.set(frequency = int(ch1_freq)*MHz, amplitude = ch1_amp)
                        #delay(1*ms)
    
                        self.urukul0_ch2.set(frequency = int(ch2_freq)*MHz, amplitude = ch2_amp)
                        #delay(1*ms)
    
                        self.urukul0_ch3.set(frequency = int(ch3_freq)*MHz, amplitude = ch3_amp)
                #print(array)
                #delay(1000*ms)
                #print(channels[0])
                """# Set frequency and amplitude for each Urukul channel based on the new data
                for setting in channels:
                    frequency, amplitude, channel = setting
                    if channel == 0:
                        self.urukul0_ch0.set(frequency * MHz, amplitude)
                    elif channel == 1:
                        self.urukul0_ch1.set(frequency * MHz, amplitude)
                    elif channel == 2:
                        self.urukul0_ch2.set(frequency * MHz, amplitude)
                    elif channel == 3:
                        self.urukul0_ch3.set(frequency * MHz, amplitude)

                delay(timestep * ms)
                for settings in channels:"""
                    

    @kernel
    def run(self):
        self.core.reset()
        self.record()

        test = self.core_dma.get_handle("test")
        self.core.break_realtime()
        self.core_dma.playback_handle(test)