from artiq.experiment import *
from artiq.coredevice import ad9910
from artiq.coredevice.ad9910 import RAM_MODE_CONT_RAMPUP
class Fastino_Multi_Output(EnvExperiment):
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul0_cpld')
        self.setattr_device('urukul0_ch1')

    def prepare(self):
    # Reversed Order
        self.amp = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
        self.asf_ram = [0] * len(self.amp)

    @kernel
    def init_dds(self, dds):
        self.core.break_realtime()
        dds.init()
        dds.set_att(0.*dB)
        dds.cfg_sw(True)
    @kernel
    def configure_ram_mode(self, dds):
        self.core.break_realtime()
        dds.set_cfr1(ram_enable=0)
        self.urukul0_cpld.io_update.pulse_mu(8)
        self.urukul0_cpld.set_profile(0) # Enable the corresponding RAM profile
        # Profile 0 is the default
        dds.set_profile_ram(start=0, end=len(self.asf_ram)-1,
        step=250, profile=0, mode=RAM_MODE_CONT_RAMPUP)
        self.urukul0_cpld.io_update.pulse_mu(8)
        dds.amplitude_to_ram(self.amp, self.asf_ram)
        dds.write_ram(self.asf_ram)
        self.core.break_realtime()
        dds.set(frequency=5*MHz, ram_destination=2)
        # Pass osk_enable=1 to set_cfr1() if it is not an amplitude RAM
        dds.set_cfr1(ram_enable=1, ram_destination=2)
        self.urukul0_cpld.io_update.pulse_mu(20)
    @kernel
    def run(self):
        dds=self.urukul0_ch1
        self.core.reset()
        self.core.break_realtime()
        self.urukul0_cpld.init()
        self.init_dds(self.urukul0_ch1)
        self.configure_ram_mode(self.urukul0_ch1)
        self.urukul0_ch1.cfg_sw(True)
        self.urukul0_ch1.set_cfr1(ram_enable=0)
        self.urukul0_cpld.io_update.pulse_mu(20)
