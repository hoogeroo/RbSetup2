#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 08:54:22 2018

@author: lab
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from PyQt5.QtGui import QIcon
import ModuleLineElement


class ModuleLineElementPlugin(QPyDesignerCustomWidgetPlugin):
    
    def __init__(self, parent = None):
        
       QPyDesignerCustomWidgetPlugin.__init__(self)
       self.initialized = False
       
    def initialize(self, formEditor):
        
        if self.initialized:
            return
        
#        manager = formEditor.extensionManager()
#        if manager:
#            self.factory = ModuleLineElementFactory(manager)
#            manager.registerExtensions(
#                    self.factory,
#                    "com.trolltech.Qt.Designer.TaskMenu")
        
        self.initialized = True
        
    def isInitialized(self):
        return self.initialized
        
    def createWidget(self, parent):
        return ModuleLineElement(parent)
    
    def name(self):
        return "ModuleLineElement"
    
    def group(self):
        return "RbController Widgets"
    
    def icon(self):
        return QIcon()
    
    def toolTip(self):
        return "RbController Module Line Element Widget"
    
    def whatsThis(self):
        return "ModuleLineElement is a widget that provides a single block "\
                "of a Module Line"
                
    def isContainer(self):
        return False
    
    def domXml(self):
        return '<widget class="ModuleLineElement" name="moduleLineElement">\n' \
               ' <property name="toolTip" >\n' \
               '  <string>RbController Module Line Element</string>\n' \
               ' </property>\n' \
               ' <property name="whatsThis" >\n' \
               '  <string>ModuleLineElement is a custom widget for the ' \
               'RbCOntroller program.</string>\n' \
               ' </property>\n ' \
               '</widget>\n'
               
    def includeFile(self):
        return "module_line_element"
    

