#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 09:51:18 2018

@author: lab
"""

freqFIFO = 100000
waitFIFO = 5000
chanFIFO = 24
largest_chunk_size = 524288
timeIncrement = 10
networkTriggerVoltage = 3300
channelsPerDDS = 4
defaultDuration = 100000
maximumDuration = 10000000
maximumStartTime = maximumDuration*10
maximumBackgrounds = 50

scanTick = 50

data_file_root = "/home/lab/mydata/Data"

DDS_2_IP = "130.216.51.242"
DDS_2_port = 8833

DDS_3_IP = "130.216.51.179"
DDS_3_port = 8833
#daq.getChannelNumber("Push Beam")
