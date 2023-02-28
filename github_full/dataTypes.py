#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 15:24:40 2018

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np

from Either import *

from constants import *

#------------------------------------------------------------------------------

class Event():
    def __init__(self, start):
        self.startTime = start

    def createList(self):
        pass
    
    def toString(self):
        return ''

class Extended(Event):
    def __init__(self,start, duration):
        super(Extended,self).__init__(start)
        self.Duration = duration

class Operation():
    def __init__(self,channel,function,value):
        self.channel = channel
        self.function = function
        self.value = value        
        
    def getValues(self,start):
        
        if self.function == 0:
            function = 'FREQ'
        else:
            function = 'AMPL'
            
        return str(start)+','+function+','+str(self.channel)+','+str(self.value)
    
    def toString(self):
        return str(self.channel)+' '+str(self.function)+' '+str(self.value)
    
class Network(Extended):
    def __init__(self, start, duration, operations):
        super(Network,self).__init__(start,duration)

        self.operations = operations
    
    def createList(self):
        points = self.Duration//timeIncrement

        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points,endpoint=False)
        ys = np.zeros((points))
        ys[0] = networkTriggerVoltage
        
        l = list(zip(map(lambda x: int(x),xs),ys))
        
        o = list(map(lambda x: x.getValues(self.startTime),self.operations))
        
        return (l,o)

    def toString(self):
        strings = list(map(Operation.toString,self.operations))
        s = []
        while strings:
            s += strings.pop(0)
            if strings:
                s += ' '
        return 'N '+str(self.startTime)+' '+str(self.Duration)+' '+''.join(s)

class Digital(Extended):
    def __init__(self,start,duration,value):
        super(Digital,self).__init__(start,duration)
        self.DigitalValue = value

    def createList(self):
        points = self.Duration//timeIncrement

        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points,endpoint=False)
        ys = np.ones((points))*self.DigitalValue
                
        return list(zip(map(lambda x: int(x),xs),ys))
    
    def toString(self):
        return 'D '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.DigitalValue)

class Analog(Extended):
    def __init__(self, start, duration, initial):
        super(Analog,self).__init__(start, duration)
        self.InitialValue = initial

    def containsTime(self,time_point):
        if (time_point >= self.startTime) and (time_point <= self.startTime + self.Duration):
            return True
        else: return False

class Constant(Analog):
    def __init__(self, start, duration, initial):
        super(Constant,self).__init__(start,duration,initial)

    def sample(self,points):
        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points,endpoint=False)
        ys = np.ones((points))*self.InitialValue
                
        return (xs,ys)

    def createList(self):
        num_points = self.Duration//timeIncrement

        (xs,ys) = self.sample(num_points)

        return list(zip(map(lambda x: int(x),xs),ys))
    
    def toString(self):
        return 'C '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.InitialValue)

class Pulse(Analog):
    def __init__(self,start,duration,initial,length):
        super(Pulse,self).__init__(start,duration,initial)
        self.Length = length
        
    def sample(self,points):
        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points,endpoint=False)
        ys = np.zeros((points))
        
        ys[0:(self.Length//timeIncrement)] = self.InitialValue
        
        return (xs,ys)
    
    def createList(self):
        num_points = self.Duration//timeIncrement
        
        (xs,ys) = self.sample(num_points)
        
        return list(zip(map(lambda x:int(x),xs),ys))

    def toString(self):
        return 'P '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.InitialValue)+' '+str(self.Length)
    
class Variable(Analog):
    def __init__(self,start,duration, initial, final):
        super(Variable,self).__init__(start,duration,initial)
        self.FinalValue = final
    
class Linear(Variable):
    def __init__(self, start, duration, initial, final):
        super(Linear,self).__init__(start,duration,initial,final)

    def sample(self, points):
        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points,endpoint=False)
        ys = np.linspace(self.InitialValue,self.FinalValue,num=points)
                         
        return (xs,ys)

    def createList(self):
        num_points = self.Duration//timeIncrement
        
        (xs,ys) = self.sample(num_points)
        
        return list(zip(map(lambda x: int(x),xs),ys))
    
    def toString(self):
        return 'L '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.InitialValue)+' '+str(self.FinalValue)
    
class Exponential(Variable):
    def __init__(self, start, duration, initial, final, amplitude):
        super(Exponential,self).__init__(start,duration,initial,final)
        self.Amplitude = amplitude
        
    def sample(self,points):
        xs = np.linspace(self.startTime,self.startTime+self.Duration,num=points)

        tau = (1/self.Duration)*(np.log((self.FinalValue+self.Amplitude-self.InitialValue)/self.FinalValue)) 
        
        if self.InitialValue > self.FinalValue:
            tau = -tau
            
        ys = self.Amplitude*np.exp(tau*np.linspace(0,self.Duration,num=points))+self.InitialValue-self.Amplitude

        return (xs,ys)
    
    def toString(self):
        return 'E '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.InitialValue)+' '+str(self.FinalValue)+' '+str(self.Amplitude)

class Lorentzian(Variable):
    def __init__(self, start, duration, initial, final, rise, wave, exponent):
        super(Lorentzian,self).__init__(start,duration,initial,final)
        self.riseTime = rise
        self.waveTime = wave
        self.Exponent = exponent

    def toString(self):
        return 'Z '+str(self.startTime)+' '+str(self.Duration)+' '+str(self.InitialValue)+' '+str(self.FinalValue)+' '+str(self.riseTime)+' '+str(self.waveTime)+' '+str(self.Exponent)

#------------------------------------------------------------------------------
  

    
