#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 13:49:39 2024

@author: rabi
"""

class DC_AOM_Ampl_Box(AOM_Ampl_Box):
    def __init__(self,i,j,val=0.2):
        super().__init__(i,j,val=0.2)
        self.valueChanged.connect(self.update_aom_amp)
        self.setValue(val)
def update_aom_amp(self):
    AOMid = self.AOMid
    self.updatecolor()
    with open("update_aom_amp.py","w") as a:
        a.write("from artiq.experiment import *\n")
        a.write("class Update_AOM_Freq(EnvExperiment):\n")
        a.write("    def build(self):\n")
        a.write("        self.setattr_device('core')\n")
        a.write("        self.setattr_device('urukul0_cpld')\n")
        a.write(f"        self.setattr_device('urukul0_ch{AOMid}')\n")
       # a.write(f"        self.dds = self.urukul0_cpld.init()\n")
      #  a.write("        self.cpld = self.urukul0_cpld\n")
        a.write("    @kernel\n")
        a.write("    def run(self):\n")
        
        a.write("        self.core.reset()\n")
        a.write("        self.urukul0_cpld.init()\n")
        a.write("        self.core.break_realtime()\n")
        a.write(f"        self.urukul0_ch{AOMid}.set_cfr1(ram_enable=0)\n")  # Disable RAM mode
        a.write(f"        self.urukul0_cpld.io_update.pulse_mu(20)\n")
        a.write(f"        self.urukul0_ch{AOMid}.sw.on()\n")
        a.write(f"        self.urukul0_ch{AOMid}.set(amplitude = {self.value()})\n")
        a.write("        self.core.wait_until_mu(now_mu())\n")
        a.flush()
        a.close()
        #time.sleep(0.1)
        subprocess.run(["artiq_run","update_aom_amp.py"])