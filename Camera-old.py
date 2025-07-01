#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 12:56:27 2019

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from astropy.io import fits

import numpy as np

import socket

from Either import *
from Parsers import *

class Camera(object):
    def __init__(self):
        pass
    
    def shoot(self,num_triggers,filename):
        pass
    
    def setTriggers(self,num_triggers,filename):
        pass
    
    def getImage(self):
        pass
    
camera = Camera()


def readLUT(fileName):
    inputFile = open(fileName,"r")
    data = inputFile.read()
    inputFile.close()

    LUT=np.zeros((256),dtype=int)

    if data:
        _, data = untilEOL(data)
        data = eatEOL(data)
        for ii in range(256):
            data = eatWhiteSpace(data)
            t1, data = readInteger(data)
            data = eatWhiteSpace(data)
            t2, data = readInteger(data)
            data = eatWhiteSpace(data)
            t3, data = readInteger(data)
            data = eatWhiteSpace(data)
            t4, data = readInteger(data)
            data = eatWhiteSpace(data)
            t5, data = readInteger(data)
            data = eatEOL(data)
            
            LUT[ii] = (t5 << 24) + (t2 << 16) + (t3 << 8) + (t4)
    else:
        print("Could not read LUT file")
        
    return LUT

class MouseGraphicsView(QtWidgets.QGraphicsView):

    pressEvent = QtCore.pyqtSignal(QtCore.QPointF, name = "pressEvent")
    releaseEvent = QtCore.pyqtSignal(QtCore.QPointF, name = "releaseEvent")
    statusEvent = QtCore.pyqtSignal(QtCore.QPointF, name = "statusEvent")
        
    def __init__(self,parent=None):
        super(MouseGraphicsView,self).__init__(parent)
        
    def mousePressEvent(self,event):
        pos = self.mapToScene(event.pos())
        print("Mouse Pressed %d %d\n" % (int(pos.x(),int(pos.y()))))
        self.pressEvent.emit(pos)
        
    def mouseReleaseEvent(self,event):
        pos = self.mapToScene(event.pos())
        print("Mouse Released %d %d\n" % (int(pos.x()),int(pos.y())))
        self.pressEvent.emit(pos)

    def mouseMoveEvent(self,event):
        pos = self.mapToScene(event.pos())
        self.statusEvent.emit(pos)

class Picture(QtWidgets.QFrame):
    def __init__(self,xs,ys,parent=None):
        super(Picture,self).__init__(parent)

        self.parent = parent

        self.XSize = xs
        self.YSize = ys
       
        self.data = np.zeros((xs,ys),dtype=np.uint16)
        self.noAtoms = np.zeros((xs,ys),dtype=np.uint16)
        self.noLaser = np.zeros((xs,ys),dtype=np.uint16)

        self.Backgrounds = np.zeros((maximumBackgrounds,xs,ys),dtype=np.uint16)
        self.BackgroundID = 0
        self.numBackgrounds = 0
        self.correctBG = False
        
        self.Display = np.zeros((xs,ys),dtype=float)
        self.CorImage = np.zeros((xs,ys),dtype=float)

        self.ROIx1 = 200
        self.ROIx2 = 350
        self.ROIy1 = 30
        self.ROIy2 = 150
        
        self.numAtoms = 0

        self.isFocussing = False
       
        self.image = QtGui.QImage(512,512,QtGui.QImage.Format_RGB32)
        
        self.LUT = readLUT("Fire.lut")
        
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = MouseGraphicsView(self)
        self.view.setMouseTracking(True)
        pixmap = QtGui.QPixmap.fromImage(self.image)
        self.pixmap = self.scene.addPixmap(pixmap)
        self.view.setScene(self.scene)
    
    def loadFile(self,fileName):
        hdu_list = fits.open(fileName)
        
        data = hdu_list[0].data
        
        self.data = data[0]
        self.noAtoms = data[1]
        self.noLaser = data[2]
        
        hdu_list.close()
        
        self.image.loadFromData(self.data.tobytes())
        
        
    def display(self):
        pass
