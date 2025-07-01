#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 11:28:11 2018

@author: lab
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class myGUI(QtWidgets.QWidget):
    def __init__(self):
        super(myGUI, self).__init__()
        self.horizontalLayout = QtWidgets.QVBoxLayout(self)
        
        lbl1 = QtWidgets.QLabel('This will eventually contain a paragraph of useful information', self)
        lbl1.move(17, 0)
        
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setGeometry(10,10,10,10)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 280))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.gridLayout = QtWidgets.QGridLayout()
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        self.btn1 = QtWidgets.QPushButton("Button 1")
        self.btn2 = QtWidgets.QPushButton("Button 2")
        self.btn3 = QtWidgets.QPushButton("Button 3")
        
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout.addWidget(self.btn1)
        self.horizontalLayout.addWidget(self.btn2)
        self.horizontalLayout.addWidget(self.btn3)
        
        self.btn1.clicked.connect(self.addButtons)
        self.setGeometry(300, 200, 500, 500)
        self.setWindowTitle('myGUI')

    def addButtons(self):
        for i in range(0, 50):
            self.r_button = QtWidgets.QPushButton("Element %s " % i)
            self.gridLayout.addWidget(self.r_button)

def run():

    app = QtWidgets.QApplication(sys.argv)
    ex = myGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
      run()