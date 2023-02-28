# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 10:44:09 2019

@author: Tim Koorey
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from astropy.io import fits

import numpy as np

import socket

from Either import *
from Parsers import *

#import kicklib as kl

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm


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

def doCutoff(ratio):       
    if np.isinf(ratio):
        ratio = 1
    elif np.isnan(ratio):
        ratio = 1
    return ratio

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

class Picture(QtWidgets.QWidget):
    def __init__(self, xs=512, ys=512, dpi=90, parent=None):
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
       
        self.figure =  Figure(figsize=(xs, ys), dpi=dpi) #QtGui.QImage(512,512,QtGui.QImage.Format_RGB32)
        
        self.canvas = FigureCanvas(self.figure)

        self.imWidget = QtWidgets.QWidget(self)
        self.imWidget.setGeometry(0, 0 ,512, 512)
        self.imLayout = QtWidgets.QVBoxLayout(self.imWidget)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.imWidget)
        self.imLayout.addWidget(self.canvas)
        self.imLayout.addWidget(self.mpl_toolbar)
        self.ax = self.figure.add_subplot(111)
#        self.figure.tight_layout()
        self.ax.axis("off")

#        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))
#        self.updateGeometry()
#        self.plot()
        
        
#        self.LUT = readLUT("Fire.lut")
        
        self.PicShow = False
        self.IsShadow = False
        
        #self.scene = QtWidgets.QGraphicsScene(self)
        #self.view = MouseGraphicsView(self)
        #self.view.setMouseTracking(True)
        #pixmap = QtGui.QPixmap.fromImage(self.image)
        #self.pixmap = self.scene.addPixmap(pixmap)
        #self.view.setScene(self.scene)
    
    def loadFile(self,fileName):
        hdu_list = fits.open(fileName)
        
        data = hdu_list[0].data
        
        self.data = data[0]
        self.noAtoms = data[1]
        self.noLaser = data[2]
        
        hdu_list.close()

        self.plot()
        
    def loadData(self,data):
        
        self.data = data[0]
        self.noAtoms = data[1]
        self.noLaser = data[2]


        self.plot()
       
        #Start edit
        
    def GetBG(self):
        pass
        
    def GetImage(self,scale):
        
        MaxVal = -1.0e9
        MinVal = 1.0e9
        MaxXInd = 0
        MaxYInd = 0
        MinXInd = 0
        MinYInd = 0
        intfluo=0.0
        
        if self.PicShow == 5 and self.IsShadow:
            GetBG()
            
        if scale == 0:
        
            if self.IsShadow:
                            
                if self.PicShow == 1:
                    t2 = self.noAtoms - self.noLaser
                    t1 = self.data - self.noLaser
                    if t2 != 0.0:
                        t1 = t1/t2
                    if t1 > 0.0:
                        t1 = -np.log(t1)
                    else:
                        t1 = 0.0

                elif self.PicShow == 2:
                    t1 = self.data
                elif self.PicShow == 3:
                    t1 = self.noAtoms
                elif self.PicShow == 4:
                    t1 = self.noLaser
                elif self.PicShow == 5:
                    t1 = self.noAtoms
                        
            elif self.isFocussing:
                t1 = self.data
                            
            else:
                t1 = self.data-self.noAtoms
                intfluo = intfluo + t1
                    
            self.Display=t1
                    
        else:
            MaxVal = scale
            MinVal = 2000
            self.Display=self.data
                    
        if self.DisplayLowPass:
            self.Display = kl.filter2(self.Display,self.XSize,self.YSize)
            
        MaxVal = -1e9
        MinVal = 1e9
        
        #for i in range(self.YSize):
            #for j in range(self.XSize):
                #ti=i*self.XSize+j
                
        self.Display[np.isnan(self.Display)] =0.01

        MaxVal = np.amax(self.Display)
        ind = np.where(self.Display==MaxVal)
        MaxXInd = ind[1]
        MaxYInd = ind[0]
            
        print("Min of %g at %d %d Max of %g at %d %d\n" % (MinVal,MinXInd,MinYInd,MaxVal,MaxXInd,MaxYInd))
        
        contrast = MaxVal-MinVal
    
        if contrast == 0.0:
            contrast = 1.0
            print("Noooo!")
        
        tt1 =self.Display - MinVal
        ratio = tt1/contrast
        
        cutoff = np.array(list(map(doCutoff, ratio)))
        
        tt1=255*ratio
        temp = np.floor(tt1)
                
        
        ROIactive = True #Set to false to disable the following sequence
        
        if ROIactive and self.picShow == 5:
            
            for i in range(self.ROIx1,self.ROIx2):
                self.data[i,self.ROIy1] = 0x00000000 #self.image.setPixel(i,self.ROIy1,0x00000000)
                self.data[i,self.ROIy2]=0x00000000 #self.image.setPixel(i,self.ROIy2,0x00000000)
            
            for j in range(self.ROIy1,self.ROIy2):
                self.data[j,self.ROIx1] = 0x00000000 #self.image.setPixel(self.ROIx1,j,0x00000000)
                self.data[j,self.ROIx2] = 0x00000000 #self.image.setPixel(self.ROIx2,j,0x00000000)
                
            mysum = 0.0
            for i in range(self.ROIx1,self.ROIx2):
                for j in range(self.ROIy1,self.ROIy2):
                    mysum=mysum+self.Display[j*self.XSize+i]
                
            pixSize = 2.1e-6
            pixArea = pixSize*pixSize
            sigma=1.4e-13
                
            self.numAtoms = np.floor(mysum*pixArea/sigma)
            return MaxVal, self.numAtoms
        
        
    def plot(self):
        self.ax.imshow(self.data, cmap=cm.jet, aspect='auto')
#        self.canvas.draw()

    
