from artiq.experiment import *
from artiq.coredevice.core import Core

# @compile
# class NAC3Devices(EnvExperiment):
#     core: KernelInvariant[Core]

#     def build(self):
#         self.setattr_device("core")

#     @kernel
#     def run(self):
#         self.core.reset()

#         print_message("NAC3 device initialized")
    
# @rpc
# def print_message(message: str):
#     print(f"Message from kernel: {message}")

import time

class IdleKernel(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("led0")
        self.setattr_device('urukul0_ch1')
        self.setattr_device('urukul0_ch3')

    @kernel
    def init_device(self):
        self.core.reset()

        self.urukul0_ch1.cpld.init()
        self.urukul0_ch1.init()
        self.urukul0_ch1.set_att(6.0 * dB)
        self.urukul0_ch1.cfg_sw(False)
        self.urukul0_ch3.cpld.init()
        self.urukul0_ch3.init()
        self.urukul0_ch3.set_att(6.0 * dB)
        self.urukul0_ch3.cfg_sw(False)

        self.urukul0_ch1.set(
            80.0 * MHz,
            amplitude=0.6
        )
        self.urukul0_ch3.set(
            80.0 * MHz,
            amplitude=0.6
        )

    def run(self):
        self.init_device()

        while True:
            now = time.time()

            self.pulse()

            print(f"Pulse took {time.time() - now} seconds")

            time.sleep(0.04)

    @kernel
    def pulse(self):
        self.core.break_realtime()

        # self.led0.on()
        # self.urukul0_ch1.set(95*MHz, amplitude=0.6)
        # self.ttl_urukul0_io_update.on()
        self.urukul0_ch3.sw.on()
        self.urukul0_ch1.sw.off()

        delay(10*ms)

        # self.led0.off()
        # self.urukul0_ch1.set(95*MHz,amplitude=0.0)
        # self.ttl_urukul0_io_update.off()
        self.urukul0_ch3.sw.off()
        self.urukul0_ch1.sw.on()
