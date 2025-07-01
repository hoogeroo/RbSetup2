#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:47:35 2019

@author: lab
"""

from Either import *
from dataTypes import *

def eatWhiteSpace(data):
    while (len(data)>0):
        if data[0] in ['\t',' ']:
            data = data[1:]
        else:
            break
    return data

def eatEOL(data):
    while (len(data)>0):
        if data[0] == '\n':
            data = data[1:]
        else:
            break
    return data

def eatChar(char,data):
    if char == data[0]:
        return data[1:]
    else:
        return data

def untilWhiteSpace(data):
    return untilChars(['\n','\t',' '],data)

def untilEOL(data):
    return untilChars(['\n'],data)

def untilChars(delimiters,data):
    value = ''
    while (not data[0] in delimiters):
        value += data[0]
        data = data[1:]
        
    return value, data

def takeN(num,data):
    output = ''
    for ii in range(num):
        output += data[0]
        data = data[1:]
        
    return output, data

def readString(st,data):
    dat = data
    value, dat = takeN(len(st),dat)
    if st == value:
        return Just(st), dat
    else:
        return Nothing, data
    
def readInteger(data):
    value, data = untilWhiteSpace(data)
    return int(value), data

def readFloat(data):
    value, data = untilWhiteSpace(data)
    return float(value), data

def readBoolean(data):
    if data[0] == 'T':
        _, data = readString('True',data)
        value = True
    elif data[0] == 'F':
        _, data = readString('False',data)
        value = False
    else:
        value = None
    return value, data

def stringToNetwork(data):
    operations = []

    data = data[1:]
    data = eatWhiteSpace(data)
    start, data = readInteger(data) # start time
    data = eatWhiteSpace(data)
    duration, data = readInteger(data)
    while data[0] != 'N' and data[0] != '\n':
        data = eatWhiteSpace(data)
        channel, data = readInteger(data)
        data = eatWhiteSpace(data)
        function, data = readInteger(data)
        data = eatWhiteSpace(data)
        value, data = readInteger(data)
        operations.append(Operation(channel,function,value))
        data = eatWhiteSpace(data)
    return Just(Network(start,duration,operations)), data
    
def stringToDigital(data):
    data = data[1:]
    data = eatWhiteSpace(data)
    start, data = readInteger(data)
    data = eatWhiteSpace(data)
    duration, data = readInteger(data)
    data = eatWhiteSpace(data)
    value, data = readBoolean(data)
    return Just(Digital(start,duration,value)), data

def stringToAnalog(data):
    event_type = data[0]
    data = data[1:]
    data = eatWhiteSpace(data)
    if event_type == 'C':
        start, data = readInteger(data)
        data = eatWhiteSpace(data)
        duration, data = readInteger(data)
        data = eatWhiteSpace(data)
        value, data = readFloat(data)
        return Just(Constant(start,duration,value)), data   
    elif event_type == 'P':
        start, data = readInteger(data)
        data = eatWhiteSpace(data)
        duration, data = readInteger(data)
        data = eatWhiteSpace(data)
        initial, data = readFloat(data)
        data = eatWhiteSpace(data)
        length, data = readFloat(data)  
        return Just(Pulse(start,duration,initial,length)), data
    elif event_type == 'L':
        start, data = readInteger(data)
        data = eatWhiteSpace(data)
        duration, data = readInteger(data)
        data = eatWhiteSpace(data)
        initial, data = readFloat(data)
        data = eatWhiteSpace(data)
        final, data = readFloat(data)
        return Just(Linear(start,duration,initial,final)), data   
    elif event_type == 'E':
        start, data = readInteger(data)
        data = eatWhiteSpace(data)
        duration, data = readInteger(data)
        data = eatWhiteSpace(data)
        initial, data = readFloat(data)
        data = eatWhiteSpace(data)
        final, data = readFloat(data)
        data = eatWhiteSpace(data)
        ampl, data = readFloat(data)                                   
        return Just(Exponential(start,duration,initial,final,ampl)), data  
    elif event_type == 'Z':
        start, data = readInteger(data)
        data = eatWhiteSpace(data)
        duration, data = readInteger(data)
        data = eatWhiteSpace(data)
        initial, data = readFloat(data)
        data = eatWhiteSpace(data)
        final, data = readFloat(data)
        data = eatWhiteSpace(data)
        rise, data = readFloat(data)
        data = eatWhiteSpace(data)
        wave, data = readFloat(data)
        data = eatWhiteSpace(data)
        exponent, data = readFloat(data)                                   
        return Just(Lorentzian(start,duration,rise,wave,exponent)), data   
    else:
        print("Error parsing Events\n")
        return Nothing(), data
    
def stringToAnalogLine(data):
    events = []

    while (data[0] != '\n'):
        data = eatWhiteSpace(data)
        event, data = stringToAnalog(data)
        events.append(event.value())
    data = eatEOL(data)
    return events, data
    
def stringToDigitalLine(data):
    events = []

    while (data[0] != '\n'):
        data = eatWhiteSpace(data)
        event, data = stringToDigital(data)
        events.append(event.value())
    data = eatEOL(data)
    return events, data

def stringToNetworkLine(data):
    events = []

    while (data[0] != '\n'):
        data = eatWhiteSpace(data)
        event, data = stringToNetwork(data)
        events.append(event.value())
    data = eatEOL(data)
    return events, data

def stringToModule(data,module):
    _, data = readString('Name:',data)
    data = eatWhiteSpace(data)
    name, data = untilEOL(data)
    data = eatEOL(data)    
    _, data = readString('Start time:',data)
    data = eatWhiteSpace(data)
    start, data = untilWhiteSpace(data)
    data = eatEOL(data)
    _, data = readString('Duration:',data)
    data = eatWhiteSpace(data)
    duration, data = untilWhiteSpace(data)
    data = eatEOL(data)

    analog_lines = {}
    digital_lines = {}
    network_lines = {}    
        
    while len(data) > 0:
        line_type = data[0]
        if line_type == 'A':
            data = data[1:]
            data = eatWhiteSpace(data)
            channel, data = readInteger(data)
            data = eatWhiteSpace(data)
            events, data = stringToAnalogLine(data)
    
            analog_lines[channel] = events
        elif line_type == 'D':
            data = data[1:]
            data = eatWhiteSpace(data)
            channel, data = readInteger(data)
            data = eatWhiteSpace(data)
            events, data = stringToDigitalLine(data)
    
            digital_lines[channel] = events
        elif line_type == 'N':
            data = data[1:]
            data = eatWhiteSpace(data)
            channel, data = readInteger(data)
            data = eatWhiteSpace(data)
            events, data = stringToNetworkLine(data)
    
            network_lines[channel] = events            
        else:
            break
    while data:
        data = eatWhiteSpace(data)
        data = eatEOL(data)
    
    module.populateModule(name,int(start),int(duration),analog_lines,digital_lines,network_lines)            

    return data

