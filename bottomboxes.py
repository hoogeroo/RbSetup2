
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *




class BottomWindow(QWidget):
    def __init__(self):
        super(BottomWindow, self).__init__(parent=parent)
        initial=True
        self.makeRFwindow(initial)
        self.makeEDACwindow(initial)
        self.makeGOLOADbuttons(initial)
        self.makeMGwindow(initial)
        self.makeStageButtons(initial)
        self.makeMLbuttons(initial)
        
    def makeRFwindow(self,initial=False):
      if initial:
        self.tek=afg.TekAFG()
        self.tek.layout.setContentsMargins(5, 0, 5, 0)
        self.tek.layout.setVerticalSpacing(5)
        if self.RFinit:
          stop_f,start_f,amp,stageind,sweepind = self.RFinit[:5]
        else:
          stop_f,start_f,amp,stageind,sweepind = [1.,4.5,100,0,0]
          
        self.tek.RF_stop_freq.setValue(stop_f)
        self.tek.RF_start_freq.setValue(start_f)
        self.tek.RF_amplitude.setValue(amp)
        self.loadRFStages()
        self.tek.RF_stage_select.currentIndexChanged.connect(self.change_RF_stage)
      else:
        stageind,sweepind=self.tek.RF_stage_select.currentIndex(),self.tek.RF_sweepstyle.currentIndex()
      
      self.loadRFStages()
      self.tek.RF_stage_select.setCurrentIndex(stageind)
      self.tek.RF_sweepstyle.setCurrentIndex(sweepind)
      self.layout.addWidget(self.tek,self.hlines+self.devicelines,0,2,5) 
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def makeEDACwindow(self,initial=False):
      if initial:
        self.eagledac=eagle.EaglePanel()
        self.eagledac.setFlat(True)
        self.eagledac.layout.setContentsMargins(5, 0, 5, 0)
        self.eagledac.layout.setVerticalSpacing(5)
        for i in range(24):
          self.eagledac.Eagle_boxes[i].setToolTip(EDnames[i])
          try:
            self.eagledac.Eagle_boxes[i].setValue(self.eagledata[i][0])
          except:
            self.eagledac.Eagle_boxes[i].setValue(0)
      self.layout.addWidget(self.eagledac,self.hlines+self.devicelines+2,0,3,5)
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def makeMGwindow(self,initial=False):
      if initial:
        self.MGPanel=mg.MultiGoPanel()
        self.MGPanel.setFlat(True)
        self.MultiGoButton=QPushButton('MultiGo')
        self.MultiGoButton.setCheckable(True)
        #self.MultiGoButton.setChecked(True)
        self.MultiGoButton.clicked.connect(self.MultiGo_pressed)
        self.MGParamButton=QPushButton('Parameters')
        self.MGParamButton.clicked.connect(self.mgmenu)
        
        self.MGPanel.layout.addWidget(self.MultiGoButton,3,0)
        self.MGPanel.layout.addWidget(self.MGParamButton,3,1)
        self.MGPanel.layout.setContentsMargins(5, 0, 5, 0)
        self.MGPanel.layout.setVerticalSpacing(5)
        
        self.fill_MG_files()
        if self.MGinit:
          self.MGPanel.sbExpFrom.setValue(self.MGinit[0])
          self.MGPanel.sbExpTo.setValue(self.MGinit[1])
          self.MGPanel.cbExpKind.setCurrentIndex(self.MGinit[2])
          self.MGPanel.sbNCycles.setValue(self.MGinit[3])
        else:
          self.MGPanel.sbExpFrom.setValue(0.)
          self.MGPanel.sbExpTo.setValue(1.)
          self.MGPanel.cbExpKind.setCurrentIndex(0)
          self.MGPanel.sbNCycles.setValue(11)
      
      self.layout.addWidget(self.MGPanel,self.hlines+self.devicelines,7,3,2)
      
    def makeStageButtons(self,initial=False):
      if initial:
        self.SCbox = QGroupBox()
        self.SCbox.setFlat(True)
        self.SClayout=QGridLayout()
        #self.SCbox.setTitle('Adjust Stages')
        self.stagechangetypebutton=QPushButton('Enact changes')
        self.stagechangetypebutton.clicked.connect(self.changeStages)
        self.combostagechange = QComboBox()
        self.combostagechange.currentIndexChanged.connect(self.stageboxaction)
        
        self.stagetargetlabel=QLabel("Which Stage?")
        self.combostagetarget=QComboBox()
        self.stageposlabel=QLabel("To where?")
        self.combostagepos=QComboBox()
        
        self.combostagechange.clear()
        self.combostagechange.addItems(["[Stage options]","Add Stage", "Delete Stage", "Duplicate Stage", "Move Stage", "Swap Stages"])   
      
        self.SClayout.addWidget(self.stagechangetypebutton,0,0)
        self.SClayout.addWidget(self.combostagechange,0,1)
        self.SClayout.addWidget(self.stagetargetlabel,1,0)
        self.SClayout.addWidget(self.combostagetarget,1,1)
        self.SClayout.addWidget(self.stageposlabel,2,0)
        self.SClayout.addWidget(self.combostagepos,2,1)
        
        self.SClayout.setContentsMargins(5, 0, 5, 0)
        self.SClayout.setVerticalSpacing(5)
        self.SCbox.setLayout(self.SClayout)
      
      self.layout.addWidget(self.SCbox, self.hlines+self.devicelines, 5, 3,2)
      self.setStageChangeBoxes('')
      
    def stageboxaction(self):
      self.setStageChangeBoxes(self.combostagechange.currentText())
      
    def makeMLbuttons(self,initial=False):
      if initial:
        default_NSteps = 100
        
        self.MLBox = QGroupBox()
        self.MLBox.setFlat(True)
        self.MLLayout = QGridLayout()
        
        self.MLTitle = QLabel('UNFINISHED, DONT USE * ML Optim.')#'Bayesian Optimisation')
        self.MLTrainLabel = QLabel(f'Training in progress: 0/{default_NSteps}')
        self.MLBayesLabel = QLabel('Bayesian iterations: 0; min cost = 0')
        
        self.ParamSetLabel = QLabel('ML Param Set')
        self.cbParamSet=QComboBox()
        self.fill_MG_files(mgo_combobox=self.cbParamSet)
        #self.cbParamSet.currentIndexChanged.connect(self.MLParamSetAction)
        
        self.MLStepsLabel = QLabel('Training Steps')
        self.sbMLNSteps = QSpinBox()
        self.sbMLNSteps.setRange(1, 1000)
        self.sbMLNSteps.setValue(default_NSteps)
        self.sbMLNSteps.setToolTip(f'Range: {self.sbMLNSteps.minimum} -> {self.sbMLNSteps.maximum}')  
        
        self.OptimiseButton=QPushButton('Optimise')
        self.OptimiseButton.setCheckable(True)
        self.OptimiseButton.clicked.connect(self.Optimise_pressed)
        
        self.MLResetButton=QPushButton('Reset Model')
        self.MLResetButton.clicked.connect(self.MLResetAction)
        
        self.MLSaveButton=QPushButton('Save Model')
        self.MLSaveButton.clicked.connect(self.MLSaveAction)
        
        self.MLLoadButton=QPushButton('Load Model')
        self.MLLoadButton.clicked.connect(partial(self.MLLoadAction,load_from_file=True))
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
        self.MLLayout.addWidget(self.MLTitle,0,0,1,2)
        
        self.MLLayout.addWidget(self.ParamSetLabel,1,0)
        self.MLLayout.addWidget(self.cbParamSet,1,1)
        
        self.MLLayout.addWidget(self.MLSaveButton,2,1)
        self.MLLayout.addWidget(self.MLLoadButton,3,1)
        
        self.MLLayout.addWidget(self.OptimiseButton,2,0)
        self.MLLayout.addWidget(self.MLResetButton,3,0)
        
        self.MLLayout.addWidget(self.MLStepsLabel,4,0,1,2)
        self.MLLayout.addWidget(self.sbMLNSteps,4,1,1,2)
        
        self.MLLayout.addWidget(self.MLTrainLabel,5,0,1,2)
        self.MLLayout.addWidget(self.MLBayesLabel,6,0,1,2)
        
        self.MLLayout.setContentsMargins(0, 0, 0, 0)
        self.MLLayout.setVerticalSpacing(0)
        self.MLBox.setLayout(self.MLLayout)
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
      
      self.layout.addWidget(self.MLBox,self.hlines+self.devicelines, 9, 6, 2)
        
    def makeGOLOADbuttons(self,initial=False):
      if initial:
        self.GoBox=QGroupBox()
        self.GoBox.setFlat(True)
        self.GoLayout=QGridLayout()
        
        self.cbMOTLoad=QCheckBox()
        self.cbMOTLoad.stateChanged.connect(self.TimerChange)
        self.MOTLoadLabel=QLabel('Load MOT')
        
        self.cbGOSave=QCheckBox()
        self.GOSaveLabel=QLabel('Save \'MultiGo\' images?')
        self.cbGOSave.setChecked(True)
        
        self.GoButton=QPushButton('Go')
        self.GoButton.clicked.connect(self.GoAction)
        
        self.FluoButton=QPushButton('Fluo. Settings')
        self.FluoButton.clicked.connect(self.FluoAction)
        #self.CycleButton=QPushButton('Cycle')
        #self.CycleButton.clicked.connect(self.CycleAction)
                
        self.MOTTimer=QTimer(self)
        self.MOTTimer.timeout.connect(self.MOTTimerAction)
        self.MOTTimer.start(500)
        self.fluo=QLCDNumber()
        
        self.fluorescence = 0
        self.fluo_continue = False
        self.fluo_zero = 400 # Use in future to set zero point
        self.fluo_max = 1100
        self.fluo_percentage = 0.8 # Must be number between 0 and 1
        self.fluo_timeout = 60 # units: seconds
        self.fluo_sampletime = 0.1 # units: seconds
        
        self.cbPictype=QComboBox()
        for label in ["No picture","One shot","Fluorescence","Shadow image"]: self.cbPictype.addItem(label)
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
        
        self.GoLayout.addWidget(self.MOTLoadLabel,0,0)
        self.GoLayout.addWidget(self.cbMOTLoad,0,1,alignment=Qt.AlignCenter)
        
        self.GoLayout.addWidget(self.GOSaveLabel,1,0)
        self.GoLayout.addWidget(self.cbGOSave,1,1,alignment=Qt.AlignCenter)
        
        self.GoLayout.addWidget(self.GoButton,0,2)
        self.GoLayout.addWidget(self.FluoButton,1,2)
        #self.GoLayout.addWidget(self.CycleButton,1,2)
        
        self.GoLayout.addWidget(self.cbPictype,0,3)
        self.GoLayout.addWidget(self.fluo,1,3)
        
      #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ 
      
        self.camera=camera_test.camera()
        self.cycling=False
        
      #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        self.GoLayout.setContentsMargins(0, 0, 0, 0)
        self.GoLayout.setVerticalSpacing(0)
        self.GoBox.setLayout(self.GoLayout)
      
      self.layout.addWidget(self.GoBox,self.hlines+self.devicelines+3, 5, 2, 4)
import sys
def main():
    app = QApplication(sys.argv)
    mw = BottomWindow()
    mw.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
