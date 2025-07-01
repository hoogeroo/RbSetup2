#!/usr/local/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

This file creates the main window of the control program.
It reads and writes the data as fits files.


@author: mhoo027
"""
import cProfile
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
#from qmsbox import *
from allboxes import *
import DAQ
import blackfly
#import multigo_window as multigo
import glob
import multigo_window as mg
import kicklib as klb

datapath='/home/lab/mydata/Data'
defaultfilename="defaultb.fit"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Creating the main window

        self.setWindowTitle("Simple Experiment Controller")
        # filling up a menu bar
        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        
        # File menu
        file_menu = bar.addMenu(' File')
        # adding actions to file menu
        file_menu = self.menubutton_add(file_menu, \
          ['Open','Save as default','Save by date', 'Close'],\
            [self.myopenaction, self.mysaveaction, self.saveasaction, self.close])
        
        # Edit menu
        edit_menu = bar.addMenu(' Edit')
        # Due to the way the column menu options are populated, 
        # we have to create the column options *before* we make the central widget. 
        self.column_dup = edit_menu.addMenu('Duplicate Column')
        self.column_del = edit_menu.addMenu('Delete Column')
        
        # NOW we make the central widget
        blackflysetting=False; motloadsetting=False; phototype=0# Comes from headers
        if os.path.exists(defaultfilename):
        # First we see if the default file exists, and if yes, we take the number of rows and columns from it.
        # If no, we make assumptions
            tables=self.initload(defaultfilename)
            self.CW = allboxes(tables, datapath = datapath, parent = self)
            #~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~
            headers=tables[-1]
            try:            
              motloadsetting=headers['MOTLOAD']
              self.CW.cbMOTLoad.setChecked(motloadsetting)
            
              phototype=headers['SHOTTYPE']
              self.CW.cbPictype.setCurrentIndex(phototype)
            
              blackflysetting=headers['BLACKFLY']
            except:
              print('checkbox headers missing; skipping!')
              pass
            #~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~v~
            #self.myload(defaultfilename)
        else:
            self.CW = allboxes([[],[],[],[],[],[],[],[],[]])
        self.setCentralWidget(self.CW) # the central widget is everything in the main window
        
        # Load the names of stages that can be duplicated/deleted
        self.refreshDupcol()
        self.refreshDelcol()
        
        edit_menu = self.menubutton_add(edit_menu, \
          ['Add Column on Right'], [self.CW.AddCol]) 
#['Add Column on Right','Undo','Redo', 'Insert Column before Cursor', 'Remove Column at Cursor'],[self.CW.AddCol,None, None, None, None])            
        
        # adding Go menu
        go_menu=bar.addMenu('Go')
        go_menu = self.menubutton_add(go_menu,\
          ['Go','MultiGo','MultiGo Parameters','Improved Fringe Removal'],\ # 'Blackfly Options'],\
            [self.CW.GoAction, self.CW.MultiGo, self.mgmenu, self.ifr_menu])#, self.blackfly_option_menu])
        
        self.filename=defaultfilename
        option_menu=bar.addMenu('Options')
        self.bfcam=None
        self.blackfly_action=QAction('Blackfly_Camera',checkable=True)
        self.blackfly_action.setChecked(blackflysetting)
        if blackflysetting:
           self.bfcam=blackfly.blackfly()
        option_menu.addAction(self.blackfly_action)
        self.blackfly_action.triggered.connect(self.initblackfly)
        self.princeton_action=QAction('Princeton Camera',checkable=True)
        option_menu.addAction(self.princeton_action)
        blackfly_option_action=QAction('Blackfly Options')
        option_menu.addAction(blackfly_option_action)
        blackfly_option_action.triggered.connect(self.blackfly_option_menu)
      
        #self.setMaximumHeight(800)
        
    def menubutton_add(self,menu, actionnames, functions):
        for i in range(len(actionnames)):
           action = QAction(actionnames[i],self)
           menu.addAction(action)
           action.triggered.connect(functions[i])
        return menu
        
#==============================================================================================================
#==============================================================================================================
    def mgmenu(self):
        mg.multigomenu(self.CW.MGPanel,self.CW.devicenames,[self.CW.Stages.stages[i].name for i in range(self.CW.nstages)])

    def ifr_menu(self):
        self.frd = FringeRemoveDialog()
        self.frd.show()
        if self.frd.exec_():
            print('success')
            #self.frd.mysave()
            self.frd.close()
        else:
            print("fail")
            self.frd.close()
    
    def blackfly_option_menu(self):
        self.bfopt = BlackflyOptionDialog(blackfly=self.bfcam, CW = self.CW)
        self.bfopt.show()
        if self.bfopt.exec_():
            print('success')
            print(self.bfcam.roi)
            #self.frd.mysave()
            self.bfopt.close()
        else:
            print("fail")
            print(self.bfcam.roi)
            self.bfopt.close()

    def initblackfly(self):  # Blackfly camera initialisation
        if self.bfcam == None:
            self.bfcam=blackfly.blackfly()
            
#==============================================================================================================
#==============================================================================================================
        
    def refreshDupcol(self):
        self.column_dup.clear()
        self.coldup_actions=[]
        for i in range(self.CW.nstages):
            self.coldup_actions.append(QAction(self.CW.Stages.stages[i].name,self))
            self.column_dup.addAction(self.coldup_actions[-1])
            self.coldup_actions[-1].triggered.connect(partial(self.DupCol,copyloc=i))
    
    def DupCol(self,copyloc=-1):
        self.CW.DupCol(a=copyloc)
        self.refreshDupcol()
        self.refreshDelcol()
            
    def refreshDelcol(self):
        self.column_del.clear()
        self.coldel_actions=[]
        for i in range(self.CW.nstages):
            self.coldel_actions.append(QAction(self.CW.Stages.stages[i].name,self))
            self.column_del.addAction(self.coldel_actions[-1])
            self.coldel_actions[-1].triggered.connect(partial(self.DelCol,pos=i))
            
    def DelCol(self,pos=-1):
        self.CW.DelCol(position=pos)
        self.refreshDupcol()
        self.refreshDelcol()
#==============================================================================================================
#==============================================================================================================
    def myopenaction(self): # Action for file open
        fname,desc = QFileDialog.getOpenFileName(self, 'Open file', datapath,"FITS files (*.fit)")

        if os.path.exists(fname):
            self.myload(fname)
            self.filename=fname
#==============================================================================================================
#==============================================================================================================
    def mysaveaction(self): # Action for file save as default
        if os.path.exists(defaultfilename):
            os.remove(defaultfilename)
        self.mysave(defaultfilename)
#==============================================================================================================
#==============================================================================================================
    def saveasaction(self): # Action for file save
        mydate=datetime.now().strftime('%Y%m%d%H%M')
        path=datapath+'/'+mydate
        
        if not (os.path.exists(path)):
          os.mkdir(path)
          myid=0
        else:
          files=glob.glob(path)
          nfiles=len(files)
          myid=nfiles
          
        name=path+'/Data_'+str(myid)+'.fit'
        self.mysave(name)
#==============================================================================================================
#==============================================================================================================
    def mysave(self,filename):
        while os.path.exists(filename):
            fn1=filename.split('.')
            filename=fn1[0]+'_1.'+fn1[1]
            print('New filename:',filename)
        if (self.blackfly_action.isChecked()):
          Imhdu=fits.PrimaryHDU(self.bfcam.data)
        else:
          Imhdu=fits.PrimaryHDU(np.arange(100.0))
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/          
        prihdr=Imhdu.header
        prihdr['NCOLS']=(self.CW.nstages, 'Number of Columns')
        prihdr['NROWS']=(len(self.CW.devicenames['DAC'])+len(self.CW.devicenames['DIO'])+len(self.CW.devicenames['AOM']), 'Number of Rows')
        prihdr['NDACS']=(len(self.CW.devicenames['DAC']), 'Number of DACs')
        prihdr['NAOMS']=(len(self.CW.devicenames['AOM']), 'Number of AOMs')
        prihdr['MOTLOAD'] = (self.CW.cbMOTLoad.isChecked(),'MOT loading selected')
        prihdr['SHOTTYPE'] = (self.CW.cbPictype.currentIndex(),'Blackfly Photo Type')
        prihdr['BLACKFLY'] = (self.blackfly_action.isChecked(),'Blackfly Camera selected')
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        columns,curves,DIOstate,RFstate,MGstate,notes = self.CW.datastore()
        
        Tabhdu=fits.BinTableHDU.from_columns(columns)
        Tab2hdu=fits.BinTableHDU.from_columns(curves)
        Tab4hdu=fits.BinTableHDU.from_columns(DIOstate)
        
        names = Tabhdu.columns.names[1:]
        
        tabhdr = Tabhdu.header
        for i in range(len(RFstate)):
          tabhdr.append(('RF', RFstate[i]))
        for j in range(len(MGstate)):
          tabhdr.append(('MG', MGstate[j]))
        for k in range(len(names)):
          tabhdr.append((names[k], notes[k]))

        edvals=[self.CW.eagledac.Eagle_boxes[i].value() for i in range(24)]
            
        Tab3hdu=fits.BinTableHDU.from_columns(\
          [fits.Column('Eagle DAC values',array=np.array(edvals),format='E')])
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        hdu1=fits.HDUList([Imhdu,Tabhdu,Tab2hdu,Tab3hdu,Tab4hdu])
        hdu1.writeto(filename)
#==============================================================================================================
#==============================================================================================================
    def initload(self,filename):
        from astropy.table import Table
        fitsfile=fits.open(filename)
        headers=fitsfile[0].header
        tabledata=fitsfile[1].data
        curvedata=fitsfile[2].data
        eagledata=fitsfile[3].data
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/    
        try:
          DIOstate=fitsfile[4].data
          RFMGhdr = fitsfile[1].header
          RFdata=[[],[],[],[],[]]
          MGdata=[[],[],[],[]]
          for i in range(5):
            RFdata[i] = RFMGhdr[('RF',i)]
          for j in range(4):
            MGdata[j]=RFMGhdr[('MG',j)]
          cols=fitsfile[1].columns
          names=cols.names[1:]
          notes=[]
          for name in names:
            notes.append(RFMGhdr[name])
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        except:
          DIOstate = []
          RFdata = []
          MGdata = []
          names = []
          notes = []

    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        fitsfile.close()
        return [tabledata,curvedata,eagledata,DIOstate,RFdata,MGdata,names,notes,headers]
#==============================================================================================================
#==============================================================================================================
    def myload(self,filename):
        tabledata,curvedata,eagledata,DIOstate,RFdata,MGdata,names,notes,headers = self.initload(filename)
        if len(names)>len(notes): 
            notes=notes[:len(names)] + [""]*(len(names)-len(notes))
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        self.CW.Stages.populate(tabledata,curvedata,DIOstate=DIOstate,names=names)
        self.CW.RF_MG_load(RFdata,MGdata)
        for i,(name,note) in enumerate(zip(names,notes)):
          self.CW.stagelabels[i].name=name
          self.CW.stagelabels[i].notes=note
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        for i in range(24):
            self.CW.eagledac.Eagle_boxes[i].setValue(eagledata[i][0])
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        try:
            motloadsetting=headers['MOTLOAD']
            self.CW.cbMOTLoad.setChecked(motloadsetting)
            
            phototype=headers['SHOTTYPE']
            self.CW.cbPictype.setCurrentIndex(phototype)
            
            blackflysetting=headers['BLACKFLY']
            self.blackfly_action.setChecked(blackflysetting)
        except:
            pass
            
#==============================================================================================================
#==============================================================================================================

class FringeRemoveDialog(QDialog):
    def __init__(self, title='Improved Fringe Removal', default_atom_folder=None, default_BG_folder=None):
        super(QDialog, self).__init__()
        self.setWindowTitle(title)
        
        self.atomfolders=[]
        self.reffolders=[]
        
        if default_atom_folder:
          self.addfolds(default_atom_folder,self.atomfolders)
          
        if default_BG_folder:
          self.addfolds(default_BG_folder,self.reffolders)
          
        self.layout = QGridLayout()
        self.remake_dialog()
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def remake_dialog(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        
        def make_boxes(title,collection,rowpos):
            self.atom_label=QLabel(title)
            self.layout.addWidget(self.atom_label,rowpos,0)
        
            for i,folder in enumerate(collection):
                self.layout.addWidget(folder,rowpos+i+1,0)
            
                self.delParButton=QPushButton('-')
                self.delParButton.clicked.connect(partial(self.delfold, collection, pos=i))
                self.layout.addWidget(self.delParButton,rowpos+i+1,1)
            
            self.addFoldButton=QPushButton('+')
            self.addFoldButton.clicked.connect(partial(self.newread2,collection))
            self.layout.addWidget(self.addFoldButton,rowpos+len(collection),2)
        
        explainbox=QLabel('Heres how this works:\n\
    - Click \'+\' to add a folder containing .fits files, or containing other folders.\n\
    - This algorithm will search *every* child folder and return every .fits file it sees.\n\
    - Only files found via \'Atomic images\' will have fringes removed,\n\
          either using the background images stored with the atomic images,\n\
          or (optionally) using backgrounds from files found via \'Reference images\'.')
        buffertext=' - - - - - - - - - - - - - - - - - - -'
        self.layout.addWidget(explainbox,0,0)
        make_boxes(buffertext+'\'Atomic\' images - - - - - - - - -'+buffertext,self.atomfolders,1)
        make_boxes(buffertext+'\'Reference\' images (optional)' + buffertext, self.reffolders,len(self.atomfolders)+3)
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.naccept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox,len(self.atomfolders)+len(self.reffolders)+4,0)
        
        self.setLayout(self.layout)
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def addfold(self,foldname,collection):
        namebox=QLabel()
        namebox.setText(foldname)
        collection.append(namebox)
            
    def delfold(self,collection,pos=-1):
        collection[pos].deleteLater()
        del collection[pos]
        self.remake_dialog()
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    
    def newread2(self, collection):
        newfolder = QFileDialog.getExistingDirectory(self, 'Select Folder', './',\
                                                     QFileDialog.ShowDirsOnly)
        self.addfold(newfolder,collection)
        self.remake_dialog()
        
    def naccept(self):
        self.run_fringe_removal()
        self.close()
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        
    def run_fringe_removal(self):
        afiles,rfiles=self.get_FR_files()
        maxrefs=50
        pics,origpics,npics = klb.perform_FR(afiles,reffiles=rfiles,maxrefs=maxrefs,bunchsize=len(afiles))
        print('Completed fringe removal on '+str(len(afiles))+' files, using a set of '+str(min([len(rfiles),maxrefs]))+' reference images.')
    
    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        
    def get_FR_files(self):
        afiles=[]
        rfiles=[]
        # Note: we're using recursive glob.glob so it'll find *every single* fits file anywhere in a given folder. 
        #       I'll remove double-ups at the end using the ol' list(set(...)) trick, I think. 
        startdir=os.getcwd()
        for afold in self.atomfolders:
            os.chdir(afold.text())
            aflist=sorted(glob.glob("*.fits",recursive=True))
            afiles+=aflist
        for rfold in self.reffolders:
            os.chdir(rfold.text())
            rflist=sorted(glob.glob("*.fits",recursive=True))
            rfiles+=rflist
        os.chdir(startdir)
        
        return list(set(afiles)),list(set(rfiles))
      
#==============================================================================================================
#==============================================================================================================
class BlackflyOptionDialog(QDialog):
    def __init__(self, title='Blackfly Options', blackfly = None, CW = None):
        super(QDialog, self).__init__()
        self.setWindowTitle(title)
        
        self.bf=blackfly
        self.CW = CW
        
        self.maxes = [1200,1920]
          
        self.layout = QGridLayout()
        self.make_dialog()
        
    def make_dialog(self):
        explain_label=QLabel('Heres how this works')
        self.layout.addWidget(explain_label,0,0)
        
        row_labs = ['[R O I]','Y','X']
        col_labs = ['min', 'max']
        
        self.labels=[]
        self.roiboxes=[]
        for i, rlab in enumerate(row_labs):
            sidelab=QLabel(rlab)
            self.labels.append(sidelab)
            self.layout.addWidget(self.labels[-1],i+1,0)
            for j,clab in enumerate(col_labs):
                if not i:
                    lab = QLabel(clab)
                    self.labels.append(lab)
                    self.layout.addWidget(self.labels[-1],1,1+j)
                else:
                    self.roiboxes.append(QSpinBox())
                    self.roiboxes[-1].setRange(0,self.maxes[i-1]-1)
                    self.roiboxes[-1].setToolTip('Allowed range: '+str(0)+' -> '+str(self.maxes[i-1]-1))
                    self.roiboxes[-1].setValue(self.bf.roi[2*(i-1) + j])
                    self.layout.addWidget(self.roiboxes[-1],1+i,1+j)
                    
        self.filterflag=QCheckBox()
        self.filterflag.setTristate(False)
        self.filterflag.setChecked(self.bf.lowpassflag)
        self.layout.addWidget(QLabel('Low pass filter?:'),4,0)
        self.layout.addWidget(self.filterflag,4,1)

        self.changeValsButton=QPushButton('Change Values')
        self.changeValsButton.clicked.connect(self.changeBFValues)
        self.layout.addWidget(self.changeValsButton,5,0)
        
        self.setLayout(self.layout)
        
    def changeBFValues(self):
        self.bf.roi=[box.value() for box in self.roiboxes]
        print(f'self.filterflag.checkState()={self.filterflag.checkState()}')
        if self.filterflag.isChecked()>0:
            self.bf.lowpassflag=True
        else:
            self.bf.lowpassflag=False
        print(f'self.bf.lowpassflag={self.bf.lowpassflag}')
        for i in range(2):
            vals=[self.roiboxes[2*i].value(), self.roiboxes[2*i+1].value()]
            self.bf.center[i] = int(sum(vals)/2)
            self.bf.dims[i] = int(max(vals) - min(vals))
        print(f'self.bf.center={self.bf.center}')
        print(f'self.bf.dims={self.bf.dims}')
        self.bf.data=np.zeros((3,self.bf.dims[0],self.bf.dims[1]))
        print(f'self.bf.data.shape={self.bf.data.shape}')
        self.CW.BGimages=None # Resets background images; will be repaired next time 'Go' action occurs
        
def multigomenu(MGPanel,devnames,stagenames): # Open Multigo dialog. Something odd is that it takes two clicks to close.
    filename=MGPanel.cbExpKind.currentText()+".mgo"
    dlg=MultiGoDialog(filename,devnames,stagenames)
    if dlg.exec_():
      print('success')
      dlg.mysave()
      dlg.close()
    else:
      print("fail")
      dlg.close()






def main():
   app = QApplication(sys.argv)
   mw = MainWindow()
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   cProfile.run("main()",filename="/home/lab/mydata/Programming/newsetup/pyqtgui/profile.txt",sort="cumulative")
