from artiq.experiment import *
from artiq.language import *
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
        self.setattr_device('urukul1_cpld')
        self.setattr_device('urukul1_ch0')
        self.setattr_device('urukul1_ch1')
        self.setattr_device('urukul1_ch2')
        self.setattr_device('urukul1_ch3')
        self.setattr_device('ttl4')
    def prepare(self):
        with open("stages.json", "r") as f:
            stages = json.load(f)
        #self.voltage_array = stages[]
        self.voltage_arrays = [np.array(stage[0], dtype=float) for stage in stages]
        self.AOM_arrays = [np.array(stage[1],dtype=float) for stage in stages]
        
        self.stage_values = stages
    @kernel
    def run(self):
        #voltage_array = self.voltage_arrays
       # AOM_array = self.AOM_arrays
        #print(voltage_array)
        self.core.reset()
        self.urukul0_cpld.init()
        self.urukul0_ch0.sw.on()
        self.core.break_realtime()
        #delay(2*ms)
       # t1 = now_mu()
        #delay(1*us)
        ##t2 = now_mu()
        #delay(1*ms)
        #print(self.core.mu_to_seconds(t2-t1))
       # delay(1*ms)
        #t111 = now_mu()
        for i in range(len(self.voltage_arrays)):
            voltages = self.voltage_arrays[i]
            #timestep = timesteps[i]
            AOM_array = self.AOM_arrays[i]  # Get frequency/amplitude/channel data
            #array = [0.0] * 32  # Create array to set voltages to Fastino
            u0_ch0_freq, u0_ch0_amp = AOM_array[0][0],AOM_array[0][1]
            u0_ch1_freq, u0_ch1_amp = AOM_array[1][0],AOM_array[1][1]
            u0_ch2_freq, u0_ch2_amp = AOM_array[2][0],AOM_array[2][1]
            u0_ch3_freq, u0_ch3_amp = AOM_array[3][0],AOM_array[3][1]
            u1_ch0_freq, u1_ch0_amp = AOM_array[4][0],AOM_array[4][1]
            u1_ch1_freq, u1_ch1_amp = AOM_array[5][0],AOM_array[5][1]
            u1_ch2_freq, u1_ch2_amp = AOM_array[6][0],AOM_array[6][1]
            u1_ch3_freq, u1_ch3_amp = AOM_array[7][0],AOM_array[7][1]
            #delay(20*ms)
            #t1=now_mu()
            """self.ttl4.on()
            with parallel:
                
                for i in range(len(voltages)):
                    self.fastino0.set_group(0, voltages[i])
                    delay(10*ms)
                    #self.ttl4.pulse(4*us)
                #delay(1*ms)
                if True:
                    
                    self.urukul0_ch0.set(frequency = int(u0_ch0_freq)*MHz, amplitude = u0_ch0_amp)
                    #delay(1*ms)
                    self.urukul0_ch1.set(frequency = int(u0_ch1_freq)*MHz, amplitude = u0_ch1_amp)
                    #delay(1*ms)

                    self.urukul0_ch2.set(frequency = int(u0_ch2_freq)*MHz, amplitude = u0_ch2_amp)
                    #delay(1*ms)

                    self.urukul0_ch3.set(frequency = int(u0_ch3_freq)*MHz, amplitude = u0_ch3_amp)
                    
                    self.urukul1_ch0.set(frequency = int(u1_ch0_freq)*MHz, amplitude = u1_ch0_amp)
                    #delay(1*ms)
                    self.urukul1_ch1.set(frequency = int(u1_ch1_freq)*MHz, amplitude = u1_ch1_amp)
                    #delay(1*ms)

                    self.urukul1_ch2.set(frequency = int(u1_ch2_freq)*MHz, amplitude = u1_ch2_amp)
                    #delay(1*ms)

                    self.urukul1_ch3.set(frequency = int(u1_ch3_freq)*MHz, amplitude = u1_ch3_amp)
                    #delay(5*ms)
                    #self.ttl4.pulse(6*us)
            #t2=now_mu()
            #print(self.core.mu_to_seconds(t2-t1))
            #delay(2*ms)
            self.ttl4.off()
            #delay(20*ms)"""
            #print(self.core.mu_to_seconds(1*ns))
            self.ttl4.on()
                
            for i in range(len(voltages)):
                self.fastino0.set_group(0, voltages[i])
                delay(10*ns)
                #self.ttl4.pulse(4*us)
            #delay(1*ms)
            if True:
                
                self.urukul0_ch0.set(frequency = int(u0_ch0_freq)*MHz, amplitude = u0_ch0_amp)
                #delay(1*ms)
                self.urukul0_ch1.set(frequency = int(u0_ch1_freq)*MHz, amplitude = u0_ch1_amp)
                #delay(1*ms)

                self.urukul0_ch2.set(frequency = int(u0_ch2_freq)*MHz, amplitude = u0_ch2_amp)
                #delay(1*ms)

                self.urukul0_ch3.set(frequency = int(u0_ch3_freq)*MHz, amplitude = u0_ch3_amp)
                
                self.urukul1_ch0.set(frequency = int(u1_ch0_freq)*MHz, amplitude = u1_ch0_amp)
                #delay(1*ms)
                self.urukul1_ch1.set(frequency = int(u1_ch1_freq)*MHz, amplitude = u1_ch1_amp)
                #delay(1*ms)

                self.urukul1_ch2.set(frequency = int(u1_ch2_freq)*MHz, amplitude = u1_ch2_amp)
                #delay(1*ms)

                self.urukul1_ch3.set(frequency = int(u1_ch3_freq)*MHz, amplitude = u1_ch3_amp)
                    #delay(5*ms)
                    #self.ttl4.pulse(6*us)
            #t2=now_mu()
            #print(self.core.mu_to_seconds(t2-t1))
            #delay(2*ms)
            self.ttl4.off()
            #delay(20*ms)
            
"""        rstart = 0.0
        rend = 1.0
        timesteps = 600
        t_range = np.arange(timesteps)
        #print(t_range)
        t1 = rstart + ((rend-rstart)/timesteps) * t_range
        #[[-30,[]]]

        array = np.ones((len(t_range),32),dtype=float)
        array[:,9]= t1"""