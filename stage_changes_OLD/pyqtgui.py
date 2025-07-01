#!/usr/local/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:00:25 2016

This file creates the main window of the control program.
It reads and writes the data as fits files.


@author: mhoo027
"""

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


defaultfilename="defaultb.fit"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Creating the main window
        # First we see if the default file exists, and if yes, we take the number of rows and columns from it.
        # If no, we make assumptions
        if os.path.exists(defaultfilename):
            fitsfile=fits.open(defaultfilename)
            headers=fitsfile[0].header
            ncols=headers['NCOLS']
            nrows=headers['NROWS']
            nDACs=headers['NDACS']
            nAOMs=headers['NAOMS']
            fitsfile.close()
            self.CW = allboxes(nDACs,nAOMs,ncols)
            self.myload(defaultfilename)
        else:
            nDACs=8
            nAOMs=6
            ncols=8
            nrows=nDACs+2*nAOMs
            self.CW = allboxes(nDACs,nAOMs,ncols)
        self.setCentralWidget(self.CW) # the central widget is everything in the main window
        self.setWindowTitle("Simple Experiment Controller")
        # filling up a menu bar
        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        # File menu
        file_menu = bar.addMenu(' File')
        # adding actions to file menu
        open_action = QAction('Open', self)
        save_action = QAction('Save as default', self)
        save_as_action= QAction('Save',self)
        close_action = QAction('Close', self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(close_action)
        # Edit menu
        edit_menu = bar.addMenu(' Edit')
        self.column_dup = edit_menu.addMenu('Duplicate Column')
        self.coldup_actions=[]
        for i in range(self.CW.ntimes):
            self.coldup_actions.append(QAction('Column '+str(i+1),self))
            self.column_dup.addAction(self.coldup_actions[-1])
            self.coldup_actions[-1].triggered.connect(partial(self.CW.DupCol,i))
        self.column_del = edit_menu.addMenu('Delete Column')
        self.coldel_actions=[]
        for i in range(self.CW.ntimes):
            self.coldel_actions.append(QAction('Column '+str(i+1),self))
            self.column_del.addAction(self.coldel_actions[-1])
            self.coldel_actions[-1].triggered.connect(partial(self.CW.DelCol,i+1))
        # adding actions to edit menu
        undo_action = QAction('Undo', self)
        redo_action = QAction('Redo', self)
        add_action = QAction('Add Column on Right',self)
        insert_action = QAction('Insert Column before Cursor',self)
        remove_action= QAction('Remove Column at Cursor',self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(add_action)
        go_menu=bar.addMenu('Go')
        go_action=QAction('Go',self)
        go_menu.addAction(go_action)
        multigo_action=QAction('Multigo',self)
        go_menu.addAction(multigo_action)
        multigo_options=QAction('MultiGo parameters',self)
        go_menu.addAction(multigo_options)
        multigo_options.triggered.connect(self.mgmenu)
        go_action.triggered.connect(self.CW.GoAction)
        self.filename=defaultfilename
        option_menu=bar.addMenu('Options')
        self.blackfly_action=QAction('Blackfly_Camera',checkable=True)
        option_menu.addAction(self.blackfly_action)
        self.princeton_action=QAction('Princeton Camera',checkable=True)
        option_menu.addAction(self.princeton_action)
        # use `connect` method to bind signals to desired behavior
        close_action.triggered.connect(self.close)
        save_action.triggered.connect(self.mysaveaction)
        open_action.triggered.connect(self.myopenaction)
        save_as_action.triggered.connect(self.saveasaction)
        add_action.triggered.connect(self.CW.AddCol)
        self.blackfly_action.triggered.connect(self.initblackfly)
        self.setMaximumHeight(800)
        self.CW.fill_MG_files() #Add multigo files
#==============================================================================================================
#==============================================================================================================
    def mgmenu(self):
        mg.multigomenu(self.CW.MGPanel)
#==============================================================================================================
#==============================================================================================================
    def initblackfly(self):  # Blackfly camera initialisation
        self.bfcam=blackfly.blackfly()
        self.blackfly_action.setChecked(True)
#==============================================================================================================
#==============================================================================================================
#    def multigomenu(self): # Open Multigo dialog. Something odd is that it takes two clicks to close.
#        filename=self.CW.MGPanel.cbExpKind.currentText()+".mgo"
#        dlg=mg.MultiGoDialog(filename)
#        if dlg.exec_():
#          print('success')
#          dlg.mysave()
#          #self.addMGFiles()
#          dlg.close()
#        else:
#          print("fail")
#          dlg.close()

#    def addMGFiles(self): # these are the custom multigo files. There are some issues with the multigo
#        flist=sorted(glob.glob("*.mgo"))
#        for item in flist:
#          sitem=item[:-4]
#          self.CW.MGPanel.cbExpKind.addItem(sitem)

#==============================================================================================================
#==============================================================================================================
    def myopenaction(self): # Action for file open
        fname,desc = QFileDialog.getOpenFileName(self, 'Open file', datapath,"FITS files (*.fit)")
        #print(fname)
        #fname='defaultb.fit'
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
        #name,path = QFileDialog.getSaveFileName(self, 'Save File', preferredname, myfilter)
        #print(name)
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
            fn1[0]=fn1[0]+'_1'
            filename=fn1[0]+fn1[1]
            print('New filename:',filename)
        from astropy.table import Table
        n=np.arange(100.0)
        if (self.blackfly_action.isChecked()):
          Imhdu=fits.PrimaryHDU(self.bfcam.data)
        else:
          Imhdu=fits.PrimaryHDU(n)
        prihdr=Imhdu.header
        ncols=self.CW.ntimes
        nrows=self.CW.nrows
        prihdr['NCOLS']=(ncols, 'Number of Columns')
        prihdr['NROWS']=(nrows, 'Number of Rows')
        prihdr['NDACS']=(self.CW.nDACs, 'Number of DACs')
        prihdr['NAOMS']=(self.CW.nAOMs, 'Number of AOMs')
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        columns=[]
        rows=[]
        rows.append(0.0)
        for row in range(nrows):
            rows.append(self.CW.DCSpinboxes[row].value())
        columns.append(fits.Column('DC'+str(row), array=np.array(rows), format='E'))
        for col in range(ncols):
            rows=[]
            rows.append(self.CW.Timeboxes[col].value())
            for row in range(nrows):
                rows.append(self.CW.Spinboxes[col][row].value())
            timeno='Time '+str(col)
            columns.append(fits.Column(timeno, array=np.array(rows), format='E'))
        Tabhdu=fits.BinTableHDU.from_columns(columns)
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        curves=[]
        for i in range(ncols):
            for j in range(nrows):
                if (self.CW.Spinboxes[i][j].value() < -15.0):
                    pars=[]
                    if (self.CW.Spinboxes[i][j].value() == -20.0): ##Lorentzian
                        pars.append(-20.0)
                        pars.append(self.CW.Spinboxes[i][j].LOffset)
                        pars.append(self.CW.Spinboxes[i][j].LAmp)
                        pars.append(self.CW.Spinboxes[i][j].LTc)
                        curves.append(fits.Column("Lorentz"+str(i)+str(j),array=np.array(pars), format='E'))
                    if (self.CW.Spinboxes[i][j].value() == -30.0): ##Linear ramp
                        pars.append(-30.0)
                        pars.append(self.CW.Spinboxes[i][j].RStart)
                        pars.append(self.CW.Spinboxes[i][j].REnd)
                        pars.append(0.0)
                        curves.append(fits.Column("Linear ramp"+str(i)+str(j),array=np.array(pars), format='E'))
        Tab2hdu=fits.BinTableHDU.from_columns(curves)
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        edvals=[]
        for i in range(24):
            edvals.append(self.CW.eagledac.Eagle_boxes[i].value())
        edcol=fits.Column('Eagle DAC values',array=np.array(edvals),format='E')
        Tab3hdu=fits.BinTableHDU.from_columns([edcol])
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        hdu1=fits.HDUList([Imhdu,Tabhdu,Tab2hdu,Tab3hdu])
        hdu1.writeto(filename)
#==============================================================================================================
#==============================================================================================================
    def myload(self,filename):
        from astropy.table import Table
        fitsfile=fits.open(filename)
        headers=fitsfile[0].header
        ncols=headers['NCOLS']
        nrows=headers['NROWS']
        tabledata=fitsfile[1].data
        curvedata=fitsfile[2].data
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        if self.CW.ntimes>ncols:
            for i in range(ncols,self.CW.ntimes):
                self.CW.DelCol(1)
        if self.CW.ntimes<ncols:
            for i in range(self.CW.ntimes,ncols):
                self.CW.AddCol()
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        myid=0
        for row in range(nrows):
            self.CW.DCSpinboxes[row].setValue(tabledata[row+1][0])
            #print("setting DCbox ", row, " to ",tabledata[row+1][0])
        for col in range(ncols):
            coln=col+1
            self.CW.Timeboxes[col].setValue(tabledata[0][coln])
            for row in range(nrows):
                tmp=tabledata[row+1][coln]
                if tmp<-10:
                    print('bpp')
                    self.CW.Spinboxes[col][row].setRange(tmp,10.0)
                    if ((tmp<-15) and (tmp>-25)):
                        self.CW.Spinboxes[col][row].LOffset=curvedata[1][myid]
                        self.CW.Spinboxes[col][row].LAmp=curvedata[2][myid]
                        self.CW.Spinboxes[col][row].LTc=curvedata[3][myid]
                        self.CW.Spinboxes[col][row].setSpecialValueText("Lrtz")
                        print('bxx')
                    if ((tmp<-25) and (tmp>-35)):
                        self.CW.Spinboxes[col][row].RStart=curvedata[1][myid]
                        self.CW.Spinboxes[col][row].REnd=curvedata[2][myid]
                        self.CW.Spinboxes[col][row].setSpecialValueText("Ramp")
                        print('byy')
                    myid=myid+1
                self.CW.Spinboxes[col][row].setValue(tmp)
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        eagledata=fitsfile[3].data
        for i in range(24):
            self.CW.eagledac.Eagle_boxes[i].setValue(eagledata[i][0])
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        fitsfile.close()
#==============================================================================================================
#==============================================================================================================


def main():
   app = QApplication(sys.argv)
   mw = MainWindow()
   #ex = spindemo()
   mw.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
