# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 08:52:02 2013

@author: a8243587
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import ResilienceGUI_v2_4_1 as RG



class OptionsWindow(QWidget):
    def __init__(self, parent = None):  
        QWidget.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        fontbold = QFont("Calibri", 10, QFont.Bold)        
        
        self.colactive = None
        self.colinactive = None
        self.timedelay, self.col1, self.col2, self.destlocation,self.pertimestep,self.saveimage,self.analysistype,self.multiiterations, self.numofiterations = RG.Window.updateoptions(self) 
        self.timedelay = str(self.timedelay)
        
        lbltimetitle = QLabel('Pause between failure time steps',self)
        lbltimetitle.move(12,15)
        lbltimetitle.setFont(fontbold)
        lbltimetitle.adjustSize()
        lbltimedelay = QLabel('Time(secs) between iterations: ',self)
        lbltimedelay.move(12,35)
        lbltimedelay.adjustSize()
        self.txttimedelay = QLineEdit(self) 
        self.txttimedelay.move(170,32)
        self.txttimedelay.setFixedWidth(50)
        self.txttimedelay.setText(str(self.timedelay))
        self.txttimedelay.setToolTip('The minimum time(seconds) between iterations. Min = 0, Max = 300')        
        self.validator = QIntValidator(0,300,self.txttimedelay)       
        self.txttimedelay.setValidator(self.validator)
        
        lblnodesandedges = QLabel('Node and Edge colours',self)
        lblnodesandedges.move(12,60)
        lblnodesandedges.setFont(fontbold)
        lblnodesandedges.adjustSize()
        lblcolor1 = QLabel("Active features:", self)
        lblcolor1.adjustSize()        
        lblcolor1.move(12,84)
        lblcolor2 = QLabel("Inactive features:", self)
        lblcolor2.adjustSize()
        lblcolor2.move(12,109)
        self.colors= 'red','green','blue', 'black', 'cyan', 'magenta', 'yellow'
        self.cmbxcolor1 = QComboBox(self)
        self.cmbxcolor1.move(150,80)
        self.cmbxcolor1.addItems(self.colors)
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col1:
                self.cmbxcolor1.setCurrentIndex(int(index))        
                index = 999
            index += 1
        self.cmbxcolor2 = QComboBox(self)
        self.cmbxcolor2.move(150,105)
        self.cmbxcolor2.addItems(self.colors)
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col2:
                self.cmbxcolor2.setCurrentIndex(int(index))
                index = 999
            index += 1
        self.cmbxcolor1.activated[str].connect(self.getcoloractive)
        self.cmbxcolor2.activated[str].connect(self.getcolorinactive)

        lbltimedelay = QLabel('Save image of network during failure: ',self)
        lbltimedelay.move(12,145)
        lbltimedelay.setFont(fontbold)        
        lbltimedelay.adjustSize()
        
        lblsave = QLabel('Save images?',self)        
        lblsave.move(12,165)
        lblsave.adjustSize()
        self.ckbxsave = QCheckBox(self)
        self.ckbxsave.move(100,166)
        self.ckbxsave.setChecked(False)
        self.ckbxsave.stateChanged.connect(self.updatedependents)
                
        self.lblsavefreq = QLabel('Save every',self)
        self.lblsavefreq.move(12, 188)
        self.lblsavefreq.adjustSize()        
        self.txtsavefreq = QLineEdit(self)
        self.txtsavefreq.move(77,185)
        self.txtsavefreq.setFixedWidth(50)
        if self.pertimestep <> '':
            self.txtsavefreq.setText(str(self.pertimestep))
        self.lblsavefreq2 = QLabel('time step(s)',self)
        self.lblsavefreq2.move(135,188)
        self.lblsavefreq2.adjustSize()
        
        self.lblsavelocation = QLabel('Destination & name:', self)
        self.lblsavelocation.move(12,215)
        self.lblsavelocation.adjustSize()
        self.txtdestlocation = QLineEdit(self)
        self.txtdestlocation.move(12,235)
        self.txtdestlocation.setFixedWidth(200)
        self.txtdestlocation.setText(self.destlocation)
        self.btnbrowse = QPushButton("Browse",self)
        self.btnbrowse.move(130,210)
        self.btnbrowse.adjustSize()
        self.btnbrowse.clicked.connect(self.browsing)
        if self.saveimage == True:
            self.ckbxsave.setChecked(True)
        if self.txtdestlocation.text() <> '':
            self.ckbxsave.setChecked(True)
        else:
            self.lblsavefreq.setEnabled(False)
            self.txtsavefreq.setEnabled(False)     
            self.lblsavefreq2.setEnabled(False)
            self.lblsavelocation.setEnabled(False)
            self.txtdestlocation.setEnabled(False)
            self.btnbrowse.setEnabled(False)
        
        lblrunmultipletimes = QLabel('Run failure model multiple times:',self)
        lblrunmultipletimes.move(12,265)
        lblrunmultipletimes.setFont(fontbold)
        lblrunmultipletimes.adjustSize()
        self.ckbxmultipleruns = QCheckBox(self)
        self.ckbxmultipleruns.move(200,267)
        self.lblnumberofiterations = QLabel('Number of iterations:',self)
        self.lblnumberofiterations.move(12,287)
        self.lblnumberofiterations.adjustSize()
        self.txtnumofiterations = QLineEdit(self)
        self.txtnumofiterations.move(120,285)
        self.txtnumofiterations.setFixedWidth(30)
        self.ckbxmultipleruns.stateChanged.connect(self.multiplerunschanged)
        if self.multiiterations == True:
            self.ckbxmultipleruns.setChecked(True)
            self.txtnumofiterations.setText(str(self.numofiterations))
        else:
            self.ckbxmultipleruns.setChecked(False)
            self.lblnumberofiterations.setEnabled(False)
            self.txtnumofiterations.setEnabled(False)
        self.apply = QPushButton("Apply", self)
        self.apply.adjustSize()
        self.apply.move(145,310)
        self.apply.clicked.connect(self.applyandclose)
        self.apply.setToolTip("Apply any changes and close the window.")
        self.closebtn = QPushButton("Close", self)
        self.closebtn.adjustSize()
        self.closebtn.move(70,310)
        self.closebtn.clicked.connect(self.closeclick)
        self.closebtn.setToolTip("Close the window without saving any changes.")
                
        self.setGeometry(300,300,230,340) #vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Options Window') #title of window  
        self.show()
    def getcoloractive(self, text):
        self.colactive = text
    def getcolorinactive(self, text):
        self.colinactive = text
    def updatetimedelay(self, timedelay):
        self.timedelay = timedelay
        self.txttimedelay.setText(str(self.timedelay))
    def applyandclose(self):
        if self.colactive == None:
            self.colactive = self.col1
        if self.colinactive == None:
            self.colinactive = self.col2
        self.timedelay = int(self.txttimedelay.text())
        #window.updatetimedelay(self.timedelay)
        #window.updatecolors(self.colactive, self.colinactive)
        if self.ckbxmultipleruns.isChecked() == True:
            self.multiiterations = True
            if self.txtnumofiterations.text() == '':
                QMessageBox.question(self, 'Message',
                    "No value entered for the number of iterations.\nPlease enter a integer.", QMessageBox.Ok)
                return       
            try:            
                self.numofiterations = int(self.txtnumofiterations.text())
            except:
                QMessageBox.question(self, 'Message',
                    "The number if iterations must be an integer.\nPlease change the text entered.", QMessageBox.Ok)
                return  
        else:
            self.multiiterations = False
            #window.updatemultiiterations(self.multiiterations,self.numofiterations)
        if self.ckbxsave.isChecked() == True:
            if self.txtsavefreq.text() == '':
                QMessageBox.question(self, 'Message',
                    "No frequency value added.", QMessageBox.Ok)
                return
            else:
                try:
                    self.pertimesteps = int(self.txtsavefreq.text())
                except:
                    QMessageBox.question(self, 'Message',
                            "Value for per time step in an incorrect format. \nPlease enter a integer.", QMessageBox.Ok)
                    return
                if self.txtdestlocation.text() == '':
                    QMessageBox.question(self, 'Message',
                            "No file destination entered.", QMessageBox.Ok)
                    return
                try:
                    filedest = self.txtdestlocation.text()
                    f = open(filedest,'a')
                    f.close()
                except:
                    QMessageBox.question(self, 'Message',
                            "Could not find location. Please \ncheck the location or chose another.", QMessageBox.Ok)
                    return
            self.saveimage = True
            
        else:
            self.saveimage = False
            
        #window.updatesaveimage(self.destlocation,self.pertimesteps, self.saveimage)
        window.updateGUI_options(self.destlocation, self.pertimesteps, self.saveimage,self.multiiterations,self.numofiterations,self.colactive,self.colinactive,self.timedelay)
        self.close() 
    def closeclick(self):
        self.close()
    def updatedependents(self):
        if self.ckbxsave.isChecked() == True:
            self.lblsavefreq.setEnabled(True)
            self.txtsavefreq.setEnabled(True)     
            self.lblsavefreq2.setEnabled(True)
            self.lblsavelocation.setEnabled(True)
            self.txtdestlocation.setEnabled(True)
            self.btnbrowse.setEnabled(True)
        else:
            self.lblsavefreq.setEnabled(False)
            self.txtsavefreq.setEnabled(False)     
            self.lblsavefreq2.setEnabled(False)
            self.lblsavelocation.setEnabled(False)
            self.txtdestlocation.setEnabled(False)
            self.btnbrowse.setEnabled(False)
    def browsing(self):
        fileName = QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        self.txtdestlocation.setText(fileName)
        self.destlocation = fileName
    def multiplerunschanged(self):
        if self.ckbxmultipleruns.isChecked() == True:
            self.lblnumberofiterations.setEnabled(True)
            self.txtnumofiterations.setEnabled(True)
        elif self.ckbxmultipleruns.isChecked() == False:
            self.lblnumberofiterations.setEnabled(False)
            self.txtnumofiterations.setEnabled(False)
            
            