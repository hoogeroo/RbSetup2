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
            tables=self.initload(defaultfilename)
            self.CW = allboxes(tables)
            #self.myload(defaultfilename)
        else:
            self.CW = allboxes([[],[],[],[],[],[]])
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
        for i in range(len(self.CW.Stages.stages)):
            self.coldup_actions.append(QAction(self.CW.Stages.stages[i].name,self))
            self.column_dup.addAction(self.coldup_actions[-1])
            self.coldup_actions[-1].triggered.connect(partial(self.CW.DupCol,a=i))
        self.column_del = edit_menu.addMenu('Delete Column')
        self.coldel_actions=[]
        for i in range(self.CW.ntimes):
            self.coldel_actions.append(QAction(self.CW.Stages.stages[i].name,self))
            self.column_del.addAction(self.coldel_actions[-1])
            self.coldel_actions[-1].triggered.connect(partial(self.CW.DelCol,a=i))
        # adding actions to edit menu
        undo_action = QAction('Undo', self)
        redo_action = QAction('Redo', self)
        self.add_action = QAction('Add Column on Right',self)
        insert_action = QAction('Insert Column before Cursor',self)
        remove_action= QAction('Remove Column at Cursor',self)
        #edit_menu.addAction(undo_action)
        #edit_menu.addAction(redo_action)
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
            filename=fn1[0]+'_1'+fn1[1]
            print('New filename:',filename)
        
        if (self.blackfly_action.isChecked()):
          Imhdu=fits.PrimaryHDU(self.bfcam.data)
        else:
          Imhdu=fits.PrimaryHDU(np.arange(100.0))
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/          
        prihdr=Imhdu.header
        prihdr['NCOLS']=(self.CW.ntimes, 'Number of Columns')
        prihdr['NROWS']=(self.CW.nrows, 'Number of Rows')
        prihdr['NDACS']=(self.CW.nDACs, 'Number of DACs')
        prihdr['NAOMS']=(self.CW.nAOMs, 'Number of AOMs')
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        columns,curves,DIOstate = self.CW.Stages.store()
        RFstate,MGstate = self.CW.RF_MG_store()
        
        Tabhdu=fits.BinTableHDU.from_columns(columns)
        Tab2hdu=fits.BinTableHDU.from_columns(curves)
        Tab4hdu=fits.BinTableHDU.from_columns(DIOstate)
        
        tabhdr = Tabhdu.header
        tabhdr['RF'] = (RFstate,'FreqStop/FreqStart/Ampl/Stage/Style')
        tabhdr['MG'] = (MGstate,'From/To/Kind/Steps')

        edvals=[self.CW.eagledac.Eagle_boxes[i].value() for i in range(24)]
            
        Tab3hdu=fits.BinTableHDU.from_columns(\
          [fits.Column('Eagle DAC values',array=np.array(edvals),format='E')])
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
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
        try:
          DIOstate=fitsfile[4].data
          RFdata = fitsfile[1].header['RF']
          MGdata=fitsfile[1].header['MG']
        except:
          DIOstate = []
          RFdata = []
          MGdata = []

        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        fitsfile.close()
        return [tabledata,curvedata,eagledata,DIOstate,RFdata,MGdata]
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
        try:
          DIOstate=fitsfile[4].data
          RFdata = fitsfile[1].header['RF']
          MGdata=fitsfile[1].header['MG']
        except:
          DIOstate = []
          RFdata = []
          MGdata = []
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        self.CW.Stages.populate(tabledata,curvedata,DIOstate)
        self.CW.RF_MG_load(RFdata,MGdata)
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
