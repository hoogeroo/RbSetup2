# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class moduleForm(QtWidgets.QWidget):
           
    def __init__(self, parent = None):

        super(moduleForm,self).__init__(parent)
        
        self.parent = parent
                
        self.setObjectName("moduleForm")
        self.resize(300, 400)
       
        self.fModule = QtWidgets.QFrame(self)
        self.fModule.resize(300,400)
        self.fModule.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fModule.setFrameShadow(QtWidgets.QFrame.Raised)   
        
        self.pbModule = QtWidgets.QPushButton("Test",self.fModule)
        self.pbModule.setGeometry(QtCore.QRect(0, 0, 80, 20))

        self.lopbModule = QtWidgets.QVBoxLayout(self.fModule)
        self.lopbModule.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)       
        
        self.lopbModule.addWidget(self.pbModule)
        
        self.loModule = QtWidgets.QVBoxLayout(self)
        self.loModule.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        
        self.loModule.addWidget(self.fModule)

        width = self.fModule.width()
        height = self.fModule.height()

        self.setMinimumSize(width,height)
        self.setMaximumSize(width,height)
        
#    def sizeHint(self):
#        width = self.fModule.width()
#        height = self.fModule.height()
#        return QtCore.QSize(width,height)

#    def minimumSizeHint(self):
#        width = self.fModule.width()
#        height = self.fModule.height()
#        return QtCore.QSize(width,height)        

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        self.x = 0
        self.y = 0
        
        MainWindow.setObjectName("Rb Controller")
        MainWindow.resize(900, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.loMainTab = QtWidgets.QHBoxLayout(self.centralwidget)
        self.centralwidget.setLayout(self.loMainTab)
    
        self.saChannels = QtWidgets.QScrollArea(self.centralwidget)
        self.saChannels.setWidgetResizable(True)
        self.saChannels.setGeometry(QtCore.QRect(10,10,10,10))
        
        self.fButtons = QtWidgets.QFrame(self.centralwidget)
        self.fButtons.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.pbAddModule = QtWidgets.QPushButton(self.fButtons)
        self.pbAddModule.setGeometry(QtCore.QRect(10, 10, 80, 20))
        self.pbAddModule.setObjectName("pbAddModule")
        self.loButtons = QtWidgets.QHBoxLayout(self.fButtons)
        self.loButtons.addWidget(self.pbAddModule)
        self.loButtons.addStretch()
        self.fButtons.setLayout(self.loButtons)

        self.hlwChannelsContents = QtWidgets.QWidget()
        self.hlwChannelsContents.setObjectName("hlwChannelsContents")
        self.hloChannelsContents = QtWidgets.QHBoxLayout(self.hlwChannelsContents)
        self.hloChannelsContents.setObjectName("hloChannelsContents")
        self.gloChannelsContents = QtWidgets.QGridLayout()
        self.hloChannelsContents.addLayout(self.gloChannelsContents)
        self.saChannels.setWidget(self.hlwChannelsContents)
        
        self.loMainTab.addWidget(self.fButtons)
        self.loMainTab.addWidget(self.saChannels,1)

#        for ii in range(10):
#            for jj in range(10):
#                self.r_button = QtWidgets.QPushButton("Element %s,%s " % (ii, jj))
#                self.gloChannelsContents.addWidget(self.r_button,ii,jj)
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.pbAddModule.clicked.connect(self.createModule)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Rb Controller"))
        self.pbAddModule.setText(_translate("MainWindow", "Add Module"))
       
    def createModule(self):
        createModule = moduleForm()
        self.gloChannelsContents.addWidget(createModule,self.x,self.y)
        self.x += 1
        if self.x > 10:
            self.x = 0
            self.y += 1
            
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()            