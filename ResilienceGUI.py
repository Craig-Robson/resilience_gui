# -*- coding: utf-8 -*-
"""
Version v2_5_0

Plans:
-how to visualise dependency and interdependency
   -to think about carefully

This code is for the visualising of static networks, as well as for the 
analysis and visualisation of networks which are under stress through component 
failure.
This currently only works for the visualisation and analysis of single 
networks, though may be extended to handle dependent networks and possibly 
interdependent networks.
The results from any analysis are saved to a .txt file at the users chosen 
detination and name. The data is in a .csv format, and this can be loaded into 
Excel for close examination of the results.
Networks can be generated using a number of avaialable algorithms, through a 
connection to our custom database schema for the handling of networks, or from 
.txt files in a suitable format.

@author: Craig
"""

import sys, time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import networkx as nx
import pylab as pl
import matplotlib.pyplot as plt
import random as r
sys.path.append("C:/Users/Craig/GitRepo/resilience")
sys.path.append("C:/a8243587_DATA/GitRepo/resilience")
import interdependency_analysis as res 
sys.path.append("C:/Users/Craig/GitRepo/resilience_gui/modules")
sys.path.append("C:/a8243587_DATA/GitRepo/resilience_gui/modules")
import inhouse_algorithms as customnets
import visalgorithms as vis
import metric_calcs as mc

class DbConnect(QDialog):  
#class DbConnect(QMainWindow):
    '''Class for the database parameters connection window.'''
    
    def __init__(self, parent=None):
        #super(dbconnect, self).__init__(parent)
        QDialog.__init__(self, parent)   
        
        #parametes for database connection               
        exitAction = QAction('&Exit',self)
        exitAction.triggered.connect(qApp.quit)

        lbl1 = QLabel('dbname: ', self)
        lbl1.move(25,30)
        lbl1.adjustSize()
        self.txtinput1 = QLineEdit(self)        
        self.txtinput1.move(75, 25)
        self.txtinput1.setToolTip('name of database')
        lbl2 = QLabel('host: ', self)
        lbl2.move(25,55)
        lbl2.adjustSize()
        self.txtinput2 = QLineEdit(self)        
        self.txtinput2.move(75, 50)
        self.txtinput2.setToolTip('host of database')
        lbl3 = QLabel('port: ', self)
        lbl3.move(25,80)
        lbl3.adjustSize()        
        self.txtinput3 = QLineEdit(self)        
        self.txtinput3.move(75, 75)
        self.txtinput3.setToolTip('port')
        lbl4 = QLabel('user: ', self)
        lbl4.move(25,105)
        lbl4.adjustSize()
        self.txtinput4 = QLineEdit(self)        
        self.txtinput4.move(75, 100)
        self.txtinput4.setToolTip('user')
        lbl5 = QLabel('password: ', self)
        lbl5.move(25,130)
        lbl5.adjustSize()
        self.txtinput5 = QLineEdit(self)        
        self.txtinput5.move(75, 125)
        self.txtinput5.setToolTip('password')
        lbl6 = QLabel('net name: ', self)
        lbl6.move(25,160)
        lbl6.adjustSize()
        self.txtinput6 = QLineEdit(self)        
        self.txtinput6.move(75, 155)
        self.txtinput6.setToolTip('network name in database')

        self.clearbtn = QPushButton('Clear', self)
        self.clearbtn.setToolTip('Clear all input boxes')
        self.clearbtn.move(10, 185)
        self.clearbtn.adjustSize()
        self.clearbtn.clicked.connect(self.clear)
        
        self.openbtn = QPushButton('Open', self)
        self.openbtn.setToolTip('Open a text file storing connection parameters')
        self.openbtn.move(90, 185)
        self.openbtn.adjustSize()
        self.openbtn.clicked.connect(self.openfile)
        
        self.savebtn = QPushButton('Save', self)
        self.savebtn.setToolTip('Save the connection parameters to a text file')
        self.savebtn.move(170, 185)
        self.savebtn.adjustSize()
        self.savebtn.clicked.connect(self.savefile)

        self.applybtn = QPushButton('Apply', self)
        self.applybtn.setToolTip('Connect to the database and run the analysis')
        self.applybtn.move(170, 215)
        self.applybtn.adjustSize()
        self.applybtn.clicked.connect(self.applyclick)
        
        self.cancelbtn = QPushButton('Cancel', self)
        self.cancelbtn.setToolTip('Cancel the analysis and close the window')
        self.cancelbtn.move(10, 215)
        self.cancelbtn.adjustSize()
        self.cancelbtn.clicked.connect(self.cancel)
             
        self.restore = QPushButton('Restore', self)
        self.restore.setToolTip('Restore the settings from the previous successful analyiss this session')
        self.restore.move(90, 215)
        self.restore.adjustSize()
        self.restore.clicked.connect(self.restoreinputs)
        #get the last set of connection parameters if they exist is not all will be None
        self.dbconnect = self.pullindbconnect()
        DBNAME,HOST,PORT,USER,PASSWORD,NETNAME=self.dbconnect
        if HOST == None and DBNAME == None and USER == None and NETNAME == None and PORT == None and PASSWORD == None:
            self.restore.setEnabled(False)

        self.setGeometry(300,500,250,250)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('db Connection Parameters')  #title of windpw
        self.setWindowIcon(QIcon('logo.png'))
        self.show()#show window   
        
    def openfile(self):
        '''Opens a text file for the user to load in a set of connection 
        parameters. Needs some error checking to make stable though.'''
        fname = QFileDialog.getOpenFileName(self, 'Open file')
        if fname == '': #if the user closes the window or in case the file is read only
            return
        text=open(fname).read()
        text = text.split('\n')
        self.dbconnect = []
        for line in text:
            parameter, txtinput = line.split(';')
            self.dbconnect.append(txtinput)
        self.txtinput1.setText(self.dbconnect[0])
        self.txtinput2.setText(self.dbconnect[1])
        self.txtinput3.setText(self.dbconnect[2])
        self.txtinput4.setText(self.dbconnect[3])
        self.txtinput5.setText(self.dbconnect[4])   
        self.txtinput6.setText(self.dbconnect[5])
            
    def savefile(self):
        '''Function for saving the parameters in a text file for future use. 
        Called by the 'Save' button only.'''
        DBNAME,HOST,PORT,USER,PASSWORD,NETNAME=self.dbconnect
        fname = QFileDialog.getSaveFileName(self, 'Save File', '.txt')
        if fname == '': #if the user closes the window or in case the file is read only
            return
        f = open(fname,'a')
        f.write('DBNAME;%s\nHOST;%s\nPORT;%s\nUSER;%s\nPASSWORD;%s\nNETNAME;%s' %(DBNAME, HOST, PORT,USER, PASSWORD, NETNAME))
        f.close()

    def clear(self):
        '''Clears all six input boxes. Called by the 'Clear' button.'''
        self.txtinput1.setText('')
        self.txtinput2.setText('')
        self.txtinput3.setText('')
        self.txtinput4.setText('')
        self.txtinput5.setText('')        
        self.txtinput6.setText('')
        
    def pullindbconnect(self):
        '''This pulls in the database connection properties from the main 
        window.'''
        dbconnect = window.updatedb_db()
        return dbconnect
   
    def applyclick(self):
        '''Save the text from that was in the text boxes when function called.'''
        #need to import ogr and nx_pgnet here
        try:
            import osgeo.ogr as ogr
        except:
            print 'could not import ogr'
        try: 
            sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
            sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet')
            import nx_pgnet, nx_pg
        except:
            print 'could not import nx_pgnet'

        self.DBNAME = self.txtinput1.text()
        self.HOST = self.txtinput2.text()
        self.PORT = self.txtinput3.text()
        self.USER = self.txtinput4.text()
        self.PASSWORD = self.txtinput5.text()        
        self.NETNAME = self.txtinput6.text()

        try:
            #needed to convert the items to strings for the connection
            self.DBNAME = str(self.DBNAME)
            self.HOST = str(self.HOST)
            self.PORT = str(self.PORT)
            self.USER = str(self.USER)
            self.PASSWORD = str(self.PASSWORD)
            self.NETNAME = str(self.NETNAME)              
            '''
            # paramers for a safe conenction that should always work
            self.DBNAME = 'roads_national'
            self.HOST = 'localhost'
            self.PORT = '5433'
            self.USER = 'postgres'
            self.PASSWORD = 'aaSD2011'
            '''
            conn = None
            conn = ogr.Open("PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (self.HOST, self.DBNAME, self.USER, self.PASSWORD, self.PORT))
            conn_worked = True
        except:
            QMessageBox.warning(self, 'Error!', "Could not connect to the database. Please check your inputs and try again.",'&OK')
            self.G = None
            conn_worked = False
            return
            
        if conn_worked == True:
            try:
                self.NETNAME = str(self.NETNAME)
                '''                
                #this is part of the known set for testing
                self.NETNAME = 'ire_m_t_roads' 
                '''
                self.G = nx_pgnet.read(conn).pgnet(self.NETNAME)
                #package the successfult connection parameters
                self.dbconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME
            except:
                QMessageBox.warning(self, 'Error!', "Could not find network in database. Please check the network name.",'&OK')             
                return
        
        #return the good set of connection parameters and the graph
        window.updateGUI_db(self.dbconnect, self.G)
        self.close()
    
    def cancel(self):
        '''Clear the text boxes and close the window when the cancel button is 
        clicked.'''
        self.close()
        
    def getval(self):
        '''Used to pass the database connection data back to the window class.'''
        return self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME
    
    def restoreinputs(self, dbconnect):
        '''Restore the previusoly saved vlaues from the last successful 
        execution of the database connection. Data is retireved from a global 
        variable.'''
        DBNAME,HOST,PORT,USER,PASSWORD,NETNAME=self.dbconnect
        if HOST == None and DBNAME == None and USER == None and NETNAME == None and PORT == None and PASSWORD == None:
            #when no inputs have been used suceesfully yet
            QMessageBox.warning(self, 'Warning', "No inputs to restore. Inputs must have been used already before they can be restored." , '&OK')
        else:
            self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = self.dbconnect
            self.txtinput1.setText(self.DBNAME)
            self.txtinput2.setText(self.HOST)
            self.txtinput3.setText(self.PORT)
            self.txtinput4.setText(self.USER)
            self.txtinput5.setText(self.PASSWORD)         
            self.txtinput6.setText(self.NETNAME)

class FailureOptionWindow(QWidget): # not sure if I will need this after all
    def __init__(self, parent = None):  
        QWidget.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        fontbold = QFont("Calibri", 10, QFont.Bold)
        
        lbltitle = QLabel("Options when loading networks\nfrom Database", self)
        lbltitle.setFont(fontbold)
        lbltitle.adjustSize()
        lbltitle.move(12,10)
        
        lblnet = QLabel("Save copies of networks\nto database at each time step:", self)        
        lblnet.adjustSize()
        lblnet.move(12,55)
        
        self.ckbwritestep = QCheckBox(self)
        self.ckbwritestep.move(180,60)
        
        lblnet = QLabel("Write results to table in database:", self)
        lblnet.adjustSize()
        lblnet.move(12,95)
        
        self.ckbwritetable = QCheckBox(self)
        self.ckbwritetable.move(180,96)
        
        lblnet = QLabel("Store metrics as node and edge\nattributes:", self)
        lblnet.adjustSize()
        lblnet.move(12,125)
        
        self.ckbstoreasatts = QCheckBox(self)
        self.ckbstoreasatts.move(180,131)   
        
        self.apply = QPushButton("Apply", self)
        self.apply.adjustSize()
        self.apply.move(145,165)
        self.apply.clicked.connect(self.applyandclose)
        self.apply.setToolTip("Apply any changes and close the window.")
        self.closebtn = QPushButton("Close", self)
        self.closebtn.adjustSize()
        self.closebtn.move(70,165)
        self.closebtn.clicked.connect(self.closeclick)
        self.closebtn.setToolTip("Close the window without saving any changes.")        
        
        self.setGeometry(300,180,230,195) #vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Failure Options') #title of window
        self.setWindowIcon(QIcon('logo.png'))        
        
        self.write_step_to_db,self.write_results_table,self.store_n_e_atts = window.updatefoptions()        
        self.updateoptions()
        self.show()        
        
    def applyandclose(self):
        if self.ckbwritestep.isChecked() == True:
            self.write_step_to_db = True
        else: self.write_step_to_db = False
        if self.ckbwritetable.isChecked() == True:
            self.write_results_table = True
        else: self.write_results_table = False
        if self.ckbstoreasatts.isChecked() == True:
            self.store_n_e_atts = True
        else: self.store_n_e_atts = False
        window.updateGUI_foptions(self.write_step_to_db,self.write_results_table,self.store_n_e_atts)
        self.close()
        
    def closeclick(self):
        self.close()
        
    def updateoptions(self):
        if self.write_step_to_db == True:
            self.ckbwritestep.setChecked(True)
        if self.write_results_table == True:
            self.ckbwritetable.setChecked(True)
        if self.store_n_e_atts == True:
            self.ckbstoreasatts.setChecked(True)
        
class MetricsWindow(QWidget): # not sure if I will need this after all
    def __init__(self, parent = None):  
        QWidget.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        fontbold = QFont("Calibri", 10, QFont.Bold)      
        
        lblnet = QLabel("Network", self)                
        lblnet.setFont(fontbold)            
        lblnet.adjustSize()
        lblnet.move(12,10)
        
        lblnetA = QLabel("A", self)        
        lblnetA.setFont(fontbold)        
        lblnetA.adjustSize()
        lblnetA.move(181,10)
        
        lblnetB = QLabel("B", self)   
        lblnetB.setFont(fontbold)
        lblnetB.adjustSize()
        lblnetB.move(201,10)
        
        lblbasic = QLabel("Basic Metrics", self)
        lblbasic.setFont(fontbold)        
        lblbasic.adjustSize()
        lblbasic.move(12,35)
        
        self.height = 35
        networkAbasicgroup = QButtonGroup(self)
        networkAbasicgroup.setExclusive(False)
        networkBbasicgroup = QButtonGroup(self)
        networkBbasicgroup.setExclusive(False)
        networkAoptionalgroup = QButtonGroup(self)
        networkAoptionalgroup.setExclusive(False)
        networkBoptionalgroup = QButtonGroup(self)  
        networkBoptionalgroup.setExclusive(False)
        
        #----------------------basic metrics----------------------------------
        self.height += 20        
        lblnodesremoved_A = QLabel("nodes removed", self)
        lblnodesremoved_A.adjustSize()
        lblnodesremoved_A.move(12,self.height)       
        self.ckbnodesremoved_A = QCheckBox(self)
        self.ckbnodesremoved_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbnodesremoved_A) 
        self.ckbnodesremoved_B = QCheckBox(self)
        self.ckbnodesremoved_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbnodesremoved_B)
        self.ckbnodesremoved_A.setChecked(True)                
        self.ckbnodesremoved_A.setEnabled(False)
        self.ckbnodesremoved_B.setChecked(True)
        self.ckbnodesremoved_B.setEnabled(False)
        
        self.height += 20
        lblnodecountremoved_A = QLabel("number of nodes removed", self)
        lblnodecountremoved_A.adjustSize()
        lblnodecountremoved_A.move(12,self.height)       
        self.ckbnodecountremoved_A = QCheckBox(self)
        self.ckbnodecountremoved_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbnodecountremoved_A)
        self.ckbnodecountremoved_B = QCheckBox(self)
        self.ckbnodecountremoved_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbnodecountremoved_B)
        self.ckbnodecountremoved_A.setChecked(True)                
        self.ckbnodecountremoved_A.setEnabled(False)
        self.ckbnodecountremoved_B.setChecked(True)
        self.ckbnodecountremoved_B.setEnabled(False)
                
        self.height += 20       
        lblcountnodesleft_A = QLabel("number of nodes", self)
        lblcountnodesleft_A.adjustSize()
        lblcountnodesleft_A.move(12,self.height)       
        self.ckbcountnodesleft_A = QCheckBox(self)
        self.ckbcountnodesleft_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbcountnodesleft_A)
        self.ckbcountnodesleft_B = QCheckBox(self)
        self.ckbcountnodesleft_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbcountnodesleft_B)
        self.ckbcountnodesleft_A.setChecked(True)  
        self.ckbcountnodesleft_A.setEnabled(False)              
        self.ckbcountnodesleft_B.setChecked(True)
        self.ckbcountnodesleft_B.setEnabled(False)
        
        self.height += 20
        lblnumberofedges_A = QLabel("number of edges", self)
        lblnumberofedges_A.adjustSize()
        lblnumberofedges_A.move(12,self.height)       
        self.ckbnumberofedges_A = QCheckBox(self)
        self.ckbnumberofedges_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbnumberofedges_A)
        self.ckbnumberofedges_B = QCheckBox(self)
        self.ckbnumberofedges_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbnumberofedges_B)
        self.ckbnumberofedges_A.setChecked(True) 
        self.ckbnumberofedges_A.setEnabled(False)               
        self.ckbnumberofedges_B.setChecked(True)
        self.ckbnumberofedges_B.setEnabled(False)
        
        self.height += 20
        lblnumberofcomponents_A = QLabel("number of components", self)
        lblnumberofcomponents_A.adjustSize()
        lblnumberofcomponents_A.move(12,self.height)       
        self.ckbnumberofcomponents_A = QCheckBox(self)
        self.ckbnumberofcomponents_A.move(180,self.height)    
        networkAbasicgroup.addButton(self.ckbnumberofedges_A)
        self.ckbnumberofcomponents_B = QCheckBox(self)
        self.ckbnumberofcomponents_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbnumberofedges_B)
        self.ckbnumberofcomponents_A.setChecked(True)
        self.ckbnumberofcomponents_A.setEnabled(False)
        self.ckbnumberofcomponents_B.setChecked(True)
        self.ckbnumberofcomponents_B.setEnabled(False)
        
        self.height += 20
        lblisolatedncount_A = QLabel("number of isolated nodes", self)
        lblisolatedncount_A.adjustSize()
        lblisolatedncount_A.move(12,self.height)
        self.ckbisolatedncount_A = QCheckBox(self)
        self.ckbisolatedncount_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbisolatedncount_A)
        self.ckbisolatedncount_B = QCheckBox(self)
        self.ckbisolatedncount_B.move(200,self.height) 
        networkBbasicgroup.addButton(self.ckbisolatedncount_B)
        self.ckbisolatedncount_A.setChecked(True)
        self.ckbisolatedncount_A.setEnabled(False)
        self.ckbisolatedncount_B.setChecked(True)
        self.ckbisolatedncount_B.setEnabled(False)
        
        self.height += 20
        lblisolatednodesremoved_A = QLabel("isolated nodes removed", self)
        lblisolatednodesremoved_A.adjustSize()
        lblisolatednodesremoved_A.move(12,self.height)
        self.ckbisolatednodesremoved_A = QCheckBox(self)
        self.ckbisolatednodesremoved_A.move(180,self.height)
        networkAbasicgroup.addButton(self.ckbisolatednodesremoved_A)
        self.ckbisolatednodesremoved_B = QCheckBox(self)
        self.ckbisolatednodesremoved_B.move(200,self.height)
        networkBbasicgroup.addButton(self.ckbisolatednodesremoved_B)
        self.ckbisolatednodesremoved_A.setChecked(True)
        self.ckbisolatednodesremoved_A.setEnabled(False)
        self.ckbisolatednodesremoved_B.setChecked(True)
        self.ckbisolatednodesremoved_B.setEnabled(False)
        
        self.height += 20
        lblnodesselectedtofail_A = QLabel("nodes selected to fail", self)
        lblnodesselectedtofail_A.adjustSize()
        lblnodesselectedtofail_A.move(12,self.height)
        ckbnodesselectedtofail_A = QCheckBox(self)
        ckbnodesselectedtofail_A.move(180,self.height)
        networkAoptionalgroup.addButton(ckbnodesselectedtofail_A)        
        ckbnodesselectedtofail_A.setChecked(True)
        ckbnodesselectedtofail_A.setEnabled(False)
        
        #-----------------------basic above, optional below--------------------
        self.height += 20
        lblmetrics = QLabel("Optional Metrics", self)
        lblmetrics.setFont(fontbold)
        lblmetrics.adjustSize()
        lblmetrics.move(12,self.height) 
  
        self.height += 20
        lblsizeofcomponents_A = QLabel("size of components*", self)
        lblsizeofcomponents_A.adjustSize()
        lblsizeofcomponents_A.move(12,self.height)
        self.ckbsizeofcomponents_A = QCheckBox(self)
        self.ckbsizeofcomponents_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbsizeofcomponents_A)                
        self.ckbsizeofcomponents_B = QCheckBox(self)
        self.ckbsizeofcomponents_B.move(200,self.height)        
        networkBoptionalgroup.addButton(self.ckbsizeofcomponents_B)
        
        self.height += 20
        lblgiantcomponentsize_A = QLabel("giant component size", self)
        lblgiantcomponentsize_A.adjustSize()
        lblgiantcomponentsize_A.move(12,self.height)
        self.ckbgiantcomponentsize_A = QCheckBox(self)
        self.ckbgiantcomponentsize_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbgiantcomponentsize_A)
        self.ckbgiantcomponentsize_B = QCheckBox(self)
        self.ckbgiantcomponentsize_B.move(200,self.height)        
        networkBoptionalgroup.addButton(self.ckbgiantcomponentsize_B)
  
        self.height += 20
        lblavnodesincomponents_A = QLabel("average size of components", self)
        lblavnodesincomponents_A.adjustSize()
        lblavnodesincomponents_A.move(12,self.height)
        self.ckbavnodesincomponents_A = QCheckBox(self)
        self.ckbavnodesincomponents_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavnodesincomponents_A)
        self.ckbavnodesincomponents_B = QCheckBox(self)
        self.ckbavnodesincomponents_B.move(200,self.height)  
        networkBoptionalgroup.addButton(self.ckbavnodesincomponents_B)
  
        self.height += 20
        lblisolatednodes_A = QLabel("isolated nodes*", self)
        lblisolatednodes_A.adjustSize()
        lblisolatednodes_A.move(12,self.height)
        self.ckbisolatednodes_A = QCheckBox(self)
        self.ckbisolatednodes_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbisolatednodes_A)
        self.ckbisolatednodes_B = QCheckBox(self)
        self.ckbisolatednodes_B.move(200,self.height)  
        networkBoptionalgroup.addButton(self.ckbisolatednodes_B)
  
        self.height += 20
        lblisolatedncountremoved_A = QLabel("number if isolated nodes removed", self)
        lblisolatedncountremoved_A.adjustSize()
        lblisolatedncountremoved_A.move(12,self.height)
        self.ckbisolatedncountremoved_A = QCheckBox(self)
        self.ckbisolatedncountremoved_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbisolatedncountremoved_A)
        self.ckbisolatedncountremoved_B = QCheckBox(self)
        self.ckbisolatedncountremoved_B.move(200,self.height) 
        networkBoptionalgroup.addButton(self.ckbisolatedncountremoved_B)
  
        self.height += 20
        lblsubnodes_A = QLabel("subnodes*", self)
        lblsubnodes_A.adjustSize()
        lblsubnodes_A.move(12,self.height)
        self.ckbsubnodes_A = QCheckBox(self)
        self.ckbsubnodes_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbsubnodes_A)
        self.ckbsubnodes_B = QCheckBox(self)
        self.ckbsubnodes_B.move(200,self.height) 
        networkBoptionalgroup.addButton(self.ckbsubnodes_B)
  
        self.height += 20        
        lblsubnodescount_A = QLabel("number of subnodes", self)
        lblsubnodescount_A.adjustSize()
        lblsubnodescount_A.move(12,self.height)
        self.ckbsubnodescount_A = QCheckBox(self)
        self.ckbsubnodescount_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbsubnodescount_A)
        self.ckbsubnodescount_B = QCheckBox(self)
        self.ckbsubnodescount_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbsubnodescount_B)
  
        self.height += 20
        lblavpathlength_A = QLabel("average path length", self)
        lblavpathlength_A.adjustSize()
        lblavpathlength_A.move(12,self.height)
        self.ckbavpathlength_A = QCheckBox(self)
        self.ckbavpathlength_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavpathlength_A)
        self.ckbavpathlength_B = QCheckBox(self)
        self.ckbavpathlength_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavpathlength_B)  
                               
        self.height += 20
        lblavpathlengthcomp_A = QLabel("avg path length components", self)
        lblavpathlengthcomp_A.adjustSize()
        lblavpathlengthcomp_A.move(12,self.height)
        self.ckbavpathlengthcomp_A = QCheckBox(self)
        self.ckbavpathlengthcomp_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavpathlengthcomp_A)
        self.ckbavpathlengthcomp_B = QCheckBox(self)
        self.ckbavpathlengthcomp_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavpathlengthcomp_B)

        self.height += 20        
        lblgiantcompavpathlength_A = QLabel("ag path length of giant component", self)
        lblgiantcompavpathlength_A.adjustSize()
        lblgiantcompavpathlength_A.move(12,self.height)
        self.ckbgiantcompavpathlength_A = QCheckBox(self)
        self.ckbgiantcompavpathlength_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbgiantcompavpathlength_A)
        self.ckbgiantcompavpathlength_B = QCheckBox(self)
        self.ckbgiantcompavpathlength_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbgiantcompavpathlength_B)

        self.height += 20
        lblavpathlengthgeo_A = QLabel("avg geographic path length", self)
        lblavpathlengthgeo_A.adjustSize()
        lblavpathlengthgeo_A.move(12,self.height)
        self.ckbavpathlengthgeo_A = QCheckBox(self)
        self.ckbavpathlengthgeo_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavpathlengthgeo_A)
        self.ckbavpathlengthgeo_B = QCheckBox(self)
        self.ckbavpathlengthgeo_B.move(200,self.height) 
        networkBoptionalgroup.addButton(self.ckbavpathlengthgeo_B)

        self.height += 20
        lblavggeocomponentspathlength_A = QLabel("avg geo path of length of components", self)
        lblavggeocomponentspathlength_A.adjustSize()
        lblavggeocomponentspathlength_A.move(12,self.height)
        self.ckbavggeopathlengthcomponents_A = QCheckBox(self)
        self.ckbavggeopathlengthcomponents_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavggeopathlengthcomponents_A)
        self.ckbavggeopathlengthcomponents_B = QCheckBox(self)
        self.ckbavggeopathlengthcomponents_B.move(200,self.height) 
        networkBoptionalgroup.addButton(self.ckbavggeopathlengthcomponents_B)

        self.height += 20
        lblavggeopathlengthgiantcomponent_A = QLabel("avg geo path length of giant component", self)
        lblavggeopathlengthgiantcomponent_A.adjustSize()
        lblavggeopathlengthgiantcomponent_A.move(12,self.height)
        self.ckbavggeopathlengthgiantcomponent_A = QCheckBox(self)
        self.ckbavggeopathlengthgiantcomponent_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavggeopathlengthgiantcomponent_A)
        self.ckbavggeopathlengthgiantcomponent_B = QCheckBox(self)
        self.ckbavggeopathlengthgiantcomponent_B.move(200,self.height) 
        networkBoptionalgroup.addButton(self.ckbavggeopathlengthgiantcomponent_B)

        self.height += 20
        lblavdegree_A = QLabel("average degree", self)
        lblavdegree_A.adjustSize()
        lblavdegree_A.move(12,self.height)
        self.ckbavdegree_A = QCheckBox(self)
        self.ckbavdegree_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavdegree_A)
        self.ckbavdegree_B = QCheckBox(self)
        self.ckbavdegree_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavdegree_B) 

        self.height += 20
        lbldensity_A = QLabel("density", self)
        lbldensity_A.adjustSize()
        lbldensity_A.move(12,self.height)
        self.ckbdensity_A = QCheckBox(self)
        self.ckbdensity_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbdensity_A)  
        self.ckbdensity_B = QCheckBox(self)
        self.ckbdensity_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbdensity_B)
        
        self.height += 20
        lblmaxbetweennesscentrality_A = QLabel("maximum betweenness centrality", self)
        lblmaxbetweennesscentrality_A.adjustSize()
        lblmaxbetweennesscentrality_A.move(12,self.height)
        self.ckbmaxbetweennesscentrality_A = QCheckBox(self)
        self.ckbmaxbetweennesscentrality_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbmaxbetweennesscentrality_A)  
        self.ckbmaxbetweennesscentrality_B = QCheckBox(self)
        self.ckbmaxbetweennesscentrality_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbmaxbetweennesscentrality_B)
        
        self.height += 20
        lblavgbetweennesscentrality_A = QLabel("avg betweenness centrality", self)
        lblavgbetweennesscentrality_A.adjustSize()
        lblavgbetweennesscentrality_A.move(12,self.height)
        self.ckbavgbetweennesscentrality_A = QCheckBox(self)
        self.ckbavgbetweennesscentrality_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavgbetweennesscentrality_A)
        self.ckbavgbetweennesscentrality_B = QCheckBox(self)
        self.ckbavgbetweennesscentrality_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavgbetweennesscentrality_B)

        self.height += 20
        lblassortativitycoefficient_A = QLabel("assortativity coefficient", self)
        lblassortativitycoefficient_A.adjustSize()
        lblassortativitycoefficient_A.move(12,self.height)
        self.ckbassortativitycoefficient_A = QCheckBox(self)
        self.ckbassortativitycoefficient_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbassortativitycoefficient_A)
        self.ckbassortativitycoefficient_B = QCheckBox(self)
        self.ckbassortativitycoefficient_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbassortativitycoefficient_B)

        self.height += 20
        lblclusteringcoefficient_A = QLabel("clustering coefficient", self)
        lblclusteringcoefficient_A.adjustSize()
        lblclusteringcoefficient_A.move(12,self.height)
        self.ckbclusteringcoefficient_A = QCheckBox(self)
        self.ckbclusteringcoefficient_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbclusteringcoefficient_A)
        self.ckbclusteringcoefficient_B = QCheckBox(self)
        self.ckbclusteringcoefficient_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbclusteringcoefficient_B)
 
        self.height += 20
        lbltransitivity_A = QLabel("transitivity", self)
        lbltransitivity_A.adjustSize()
        lbltransitivity_A.move(12,self.height)
        self.ckbtransitivity_A = QCheckBox(self)
        self.ckbtransitivity_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbtransitivity_A)
        self.ckbtransitivity_B = QCheckBox(self)
        self.ckbtransitivity_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbtransitivity_B)
 
        self.height += 20
        lblsquareclustering_A = QLabel("square clustering", self)
        lblsquareclustering_A.adjustSize()
        lblsquareclustering_A.move(12,self.height)
        self.ckbsquareclustering_A = QCheckBox(self)
        self.ckbsquareclustering_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbsquareclustering_A)
        self.ckbsquareclustering_B = QCheckBox(self)
        self.ckbsquareclustering_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbsquareclustering_B)
 
        self.height += 20
        lblavgneighbordegree_A = QLabel("avg neighbor degree", self)
        lblavgneighbordegree_A.adjustSize()
        lblavgneighbordegree_A.move(12,self.height)
        self.ckbavgneighbordegree_A = QCheckBox(self)
        self.ckbavgneighbordegree_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavgneighbordegree_A)
        self.ckbavgneighbordegree_B = QCheckBox(self)
        self.ckbavgneighbordegree_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavgneighbordegree_B)
 
        self.height += 20
        lblavgdegreeconnectivity_A = QLabel("avg degree connectivity", self)
        lblavgdegreeconnectivity_A.adjustSize()
        lblavgdegreeconnectivity_A.move(12,self.height)
        self.ckbavgdegreeconnectivity_A = QCheckBox(self)
        self.ckbavgdegreeconnectivity_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavgdegreeconnectivity_A)
        self.ckbavgdegreeconnectivity_B = QCheckBox(self)
        self.ckbavgdegreeconnectivity_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavgdegreeconnectivity_B)

        self.height += 20
        lblavgdegreecentrality_A = QLabel("avg degree centrality", self)
        lblavgdegreecentrality_A.adjustSize()
        lblavgdegreecentrality_A.move(12,self.height)
        self.ckbavgdegreecentrality_A = QCheckBox(self)
        self.ckbavgdegreecentrality_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavgdegreecentrality_A)
        self.ckbavgdegreecentrality_B = QCheckBox(self)
        self.ckbavgdegreecentrality_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavgdegreecentrality_B)

        self.height += 20
        lblavgclosenesscentrality_A = QLabel("avg closeness centrality", self)
        lblavgclosenesscentrality_A.adjustSize()
        lblavgclosenesscentrality_A.move(12,self.height)
        self.ckbavgclosenesscentrality_A = QCheckBox(self)
        self.ckbavgclosenesscentrality_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbavgclosenesscentrality_A)
        self.ckbavgclosenesscentrality_B = QCheckBox(self)
        self.ckbavgclosenesscentrality_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbavgclosenesscentrality_B)

        self.height += 20
        lbldiameter_A = QLabel("diameter", self)
        lbldiameter_A.adjustSize()
        lbldiameter_A.move(12,self.height)
        self.ckbdiameter_A = QCheckBox(self)
        self.ckbdiameter_A.move(180,self.height)
        networkAoptionalgroup.addButton(self.ckbdiameter_A)
        self.ckbdiameter_B = QCheckBox(self)
        self.ckbdiameter_B.move(200,self.height)
        networkBoptionalgroup.addButton(self.ckbdiameter_B)
        
        self.metrics = window.updatewindow_metrics()
        self.update_ckbs(self.metrics) #updates check boxes
        
        self.height += 20
        self.lblastrix = QLabel("*Will not show in metric plots at end of analysis.", self)
        self.lblastrix.adjustSize()
        self.lblastrix.move(12,self.height)
                
        self.height += 20
        closebtn = QPushButton("Close", self)
        closebtn.adjustSize()
        closebtn.move(170,self.height)
        closebtn.clicked.connect(self.closeclick)
        closebtn.setToolTip("Close the window without saving any changes.")
        selectallAbtn = QPushButton('Select all A', self)
        selectallAbtn.setToolTip('Select all check boxes for network A')
        selectallAbtn.move(10, self.height)
        selectallAbtn.clicked.connect(self.selectallA)
        selectallBbtn = QPushButton('Select all B', self)
        selectallBbtn.setToolTip('Select all check boxes for network B')
        selectallBbtn.move(90, self.height)
        selectallBbtn.clicked.connect(self.selectallB)        
        
        self.height += 30
        applybtn = QPushButton("Apply", self)
        applybtn.adjustSize()
        applybtn.move(170,self.height)
        applybtn.clicked.connect(self.applyandclose)
        applybtn.setToolTip("Apply any changes and close the window.")     
        unselectallAbtn = QPushButton('Unselect all A', self)
        unselectallAbtn.setToolTip('Unselect all check boxes for network A')
        unselectallAbtn.move(10, self.height)
        unselectallAbtn.clicked.connect(self.unselectallA)
        unselectallBbtn = QPushButton('Unselect all B', self)
        unselectallBbtn.setToolTip('Unselect all check boxes for network B')
        unselectallBbtn.move(90, self.height)
        unselectallBbtn.clicked.connect(self.unselectallB)
        
        #if self.basic_metrics_B == None:
        #    selectallBbtn.setEnabled(False)            
        #    unselectallBbtn.setEnabled(False)

        self.setGeometry(300,100,250,self.height+30) #vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Metrics Window') #title of window
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def update_ckbs(self, metrics):
        '''Updates check boxs on startup based on previuos selections. The 
        previous selections are stored in memory in the window function are 
        retrieved upon launch of the window.'''

        basicA, basicB, optionA, optionB = metrics
               
        if optionA['size_of_components'] == False:
            self.ckbsizeofcomponents_A.setChecked(False)
        else: self.ckbsizeofcomponents_A.setChecked(True)
        
        if optionA['giant_component_size'] == False:
            self.ckbgiantcomponentsize_A.setChecked(False)
        else: self.ckbgiantcomponentsize_A.setChecked(True)
        
        if optionA['avg_size_of_components'] == False:
            self.ckbavnodesincomponents_A.setChecked(False)
        else: self.ckbavnodesincomponents_A.setChecked(True)
        
        if optionA['isolated_nodes'] == False:
            self.ckbisolatednodes_A.setChecked(False)
        else: self.ckbisolatednodes_A.setChecked(True)
        
        if optionA['no_of_isolated_nodes_removed'] == False:
            self.ckbisolatedncountremoved_A.setChecked(False)
        else: self.ckbisolatedncountremoved_A.setChecked(True)
        
        if optionA['subnodes'] == False:
            self.ckbsubnodes_A.setChecked(False)
        else: self.ckbsubnodes_A.setChecked(True)
        
        if optionA['no_of_subnodes'] == False:
            self.ckbsubnodescount_A.setChecked(False)
        else: self.ckbsubnodescount_A.setChecked(True)
        
        if optionA['avg_path_length'] == False:
            self.ckbavpathlength_A.setChecked(False)
        else: self.ckbavpathlength_A.setChecked(True)
        
        if optionA['avg_path_length_of_components'] == False:
            self.ckbavpathlengthcomp_A.setChecked(False)
        else: self.ckbavpathlengthcomp_A.setChecked(True)
        
        if optionA['avg_path_length_of_giant_component'] == False:
            self.ckbgiantcompavpathlength_A.setChecked(False)
        else: self.ckbgiantcompavpathlength_A.setChecked(True)
        
        if optionA['avg_geo_path_length'] == False:
            self.ckbavpathlengthgeo_A.setChecked(False)
        else: self.ckbavpathlengthgeo_A.setChecked(True)
        
        if optionA['avg_geo_path_length_of_components'] == False:
            self.ckbavggeopathlengthcomponents_A.setChecked(False)
        else: self.ckbavggeopathlengthcomponents_A.setChecked(True)
        
        if optionA['avg_geo_path_length_of_giant_component'] == False:
            self.ckbavggeopathlengthgiantcomponent_A.setChecked(False)
        else: self.ckbavggeopathlengthgiantcomponent_A.setChecked(True)
        
        if optionA['avg_degree'] == False:
            self.ckbavdegree_A.setChecked(False)
        else: self.ckbavdegree_A.setChecked(True)
        
        if optionA['density'] == False:
            self.ckbdensity_A.setChecked(False)
        else: self.ckbdensity_A.setChecked(True)
        
        if optionA['maximum_betweenness_centrality'] == False:
            self.ckbmaxbetweennesscentrality_A.setChecked(False)
        else: self.ckbmaxbetweennesscentrality_A.setChecked(True)
        
        if optionA['avg_betweenness_centrality'] == False:
            self.ckbavgbetweennesscentrality_A.setChecked(False)
        else: self.ckbavgbetweennesscentrality_A.setChecked(True)
        
        if optionA['assortativity_coefficient'] == False:
            self.ckbassortativitycoefficient_A.setChecked(False)
        else: self.ckbassortativitycoefficient_A.setChecked(True)
        
        if optionA['clustering_coefficient'] == False:
            self.ckbclusteringcoefficient_A.setChecked(False)
        else: self.ckbclusteringcoefficient_A.setChecked(True)
        
        if optionA['transitivity'] == False:
            self.ckbtransitivity_A.setChecked(False)
        else: self.ckbtransitivity_A.setChecked(True)
        
        if optionA['square_clustering'] == False:
            self.ckbsquareclustering_A.setChecked(False)
        else: self.ckbsquareclustering_A.setChecked(True)
        
        if optionA['avg_neighbor_degree'] == False:
            self.ckbavgneighbordegree_A.setChecked(False)
        else: self.ckbavgneighbordegree_A.setChecked(True)
        
        if optionA['avg_degree_connectivity'] == False:
            self.ckbavgdegreeconnectivity_A.setChecked(False)
        else: self.ckbavgdegreeconnectivity_A.setChecked(True)
        
        if optionA['avg_degree_centrality'] == False:
            self.ckbavgdegreecentrality_A.setChecked(False)
        else: self.ckbavgdegreecentrality_A.setChecked(True)
        
        if optionA['avg_closeness_centrality'] == False:
            self.ckbavgclosenesscentrality_A.setChecked(False)
        else: self.ckbavgclosenesscentrality_A.setChecked(True)
        
        if optionA['diameter'] == False:
            self.ckbdiameter_A.setChecked(False)
        else: self.ckbdiameter_A.setChecked(True)
        
        #-------------------for network B------------------------------------
        if optionB['size_of_components'] == False:
            self.ckbsizeofcomponents_B.setChecked(False)
        else: self.ckbsizeofcomponents_B.setChecked(True)
        
        if optionB['giant_component_size'] == False:
            self.ckbgiantcomponentsize_B.setChecked(False)
        else: self.ckbgiantcomponentsize_B.setChecked(True)
        
        if optionB['avg_size_of_components'] == False:
            self.ckbavnodesincomponents_B.setChecked(False)
        else: self.ckbavnodesincomponents_B.setChecked(True)
        
        if optionB['isolated_nodes'] == False:
            self.ckbisolatednodes_B.setChecked(False)
        else: self.ckbisolatednodes_B.setChecked(True)
        
        if optionB['no_of_isolated_nodes_removed'] == False:
            self.ckbisolatedncountremoved_B.setChecked(False)
        else: self.ckbisolatedncountremoved_B.setChecked(True)
        
        if optionB['subnodes'] == False:
            self.ckbsubnodes_B.setChecked(False)
        else: self.ckbsubnodes_B.setChecked(True)
        
        if optionB['no_of_subnodes'] == False:
            self.ckbsubnodescount_B.setChecked(False)
        else: self.ckbsubnodescount_B.setChecked(True)
        
        if optionB['avg_path_length'] == False:
            self.ckbavpathlength_B.setChecked(False)
        else: self.ckbavpathlength_B.setChecked(True)
        
        if optionB['avg_path_length_of_components'] == False:
            self.ckbavpathlengthcomp_B.setChecked(False)
        else: self.ckbavpathlengthcomp_B.setChecked(True)
        
        if optionB['avg_path_length_of_giant_component'] == False:
            self.ckbgiantcompavpathlength_B.setChecked(False)
        else: self.ckbgiantcompavpathlength_B.setChecked(True)
        
        if optionB['avg_geo_path_length'] == False:
            self.ckbavpathlengthgeo_B.setChecked(False)
        else: self.ckbavpathlengthgeo_B.setChecked(True)
        
        if optionB['avg_geo_path_length_of_components'] == False:
            self.ckbavggeopathlengthcomponents_B.setChecked(False)
        else: self.ckbavggeopathlengthcomponents_B.setChecked(True)
        
        if optionB['avg_geo_path_length_of_giant_component'] == False:
            self.ckbavggeopathlengthgiantcomponent_B.setChecked(False)
        else: self.ckbavggeopathlengthgiantcomponent_B.setChecked(True)
        
        if optionB['avg_degree'] == False:
            self.ckbavdegree_B.setChecked(False)
        else: self.ckbavdegree_B.setChecked(True)
        
        if optionB['density'] == False:
            self.ckbdensity_B.setChecked(False)
        else: self.ckbdensity_B.setChecked(True)
        
        if optionB['maximum_betweenness_centrality'] == False:
            self.ckbmaxbetweennesscentrality_B.setChecked(False)
        else: self.ckbmaxbetweennesscentrality_B.setChecked(True)
        
        if optionB['avg_betweenness_centrality'] == False:
            self.ckbavgbetweennesscentrality_B.setChecked(False)
        else: self.ckbavgbetweennesscentrality_B.setChecked(True)
        
        if optionB['assortativity_coefficient'] == False:
            self.ckbassortativitycoefficient_B.setChecked(False)
        else: self.ckbassortativitycoefficient_B.setChecked(True)
        
        if optionB['clustering_coefficient'] == False:
            self.ckbclusteringcoefficient_B.setChecked(False)
        else: self.ckbclusteringcoefficient_B.setChecked(True)
        
        if optionB['transitivity'] == False:
            self.ckbtransitivity_B.setChecked(False)
        else: self.ckbtransitivity_B.setChecked(True)
        
        if optionB['square_clustering'] == False:
            self.ckbsquareclustering_B.setChecked(False)
        else: self.ckbsquareclustering_B.setChecked(True)
        
        if optionB['avg_neighbor_degree'] == False:
            self.ckbavgneighbordegree_B.setChecked(False)
        else: self.ckbavgneighbordegree_B.setChecked(True)
        
        if optionB['avg_degree_connectivity'] == False:
            self.ckbavgdegreeconnectivity_B.setChecked(False)
        else: self.ckbavgdegreeconnectivity_B.setChecked(True)
        
        if optionB['avg_degree_centrality'] == False:
            self.ckbavgdegreecentrality_B.setChecked(False)
        else: self.ckbavgdegreecentrality_B.setChecked(True)
        
        if optionB['avg_closeness_centrality'] == False:
            self.ckbavgclosenesscentrality_B.setChecked(False)
        else: self.ckbavgclosenesscentrality_B.setChecked(True)
        
        if optionB['diameter'] == False:
            self.ckbdiameter_B.setChecked(False)
        else: self.ckbdiameter_B.setChecked(True)
        
       
    def selectallA(self):
        '''Selects all text box's for network A.'''
        self.ckbsizeofcomponents_A.setChecked(True)
        self.ckbgiantcomponentsize_A.setChecked(True)
        self.ckbavnodesincomponents_A.setChecked(True)
        self.ckbisolatednodes_A.setChecked(True)
        self.ckbisolatedncountremoved_A.setChecked(True)
        self.ckbsubnodes_A.setChecked(True)
        self.ckbsubnodescount_A.setChecked(True)
        self.ckbavpathlength_A.setChecked(True)
        self.ckbavpathlengthcomp_A.setChecked(True)
        self.ckbgiantcompavpathlength_A.setChecked(True)
        self.ckbavpathlengthgeo_A.setChecked(True)
        self.ckbavggeopathlengthcomponents_A.setChecked(True)
        self.ckbavggeopathlengthgiantcomponent_A.setChecked(True)
        self.ckbavdegree_A.setChecked(True)
        self.ckbdensity_A.setChecked(True)
        self.ckbmaxbetweennesscentrality_A.setChecked(True)
        self.ckbavgbetweennesscentrality_A.setChecked(True)
        self.ckbassortativitycoefficient_A.setChecked(True)
        self.ckbclusteringcoefficient_A.setChecked(True)
        self.ckbtransitivity_A.setChecked(True)
        self.ckbsquareclustering_A.setChecked(True)
        self.ckbavgneighbordegree_A.setChecked(True)
        self.ckbavgdegreeconnectivity_A.setChecked(True)
        self.ckbavgdegreecentrality_A.setChecked(True)
        self.ckbavgclosenesscentrality_A.setChecked(True)
        self.ckbdiameter_A.setChecked(True)
        
    def selectallB(self):
        '''Selects all text box's for network B.'''
        self.ckbsizeofcomponents_B.setChecked(True)
        self.ckbgiantcomponentsize_B.setChecked(True)
        self.ckbavnodesincomponents_B.setChecked(True)
        self.ckbisolatednodes_B.setChecked(True)
        self.ckbisolatedncountremoved_B.setChecked(True)
        self.ckbsubnodes_B.setChecked(True)
        self.ckbsubnodescount_B.setChecked(True)
        self.ckbavpathlength_B.setChecked(True)
        self.ckbavpathlengthcomp_B.setChecked(True)
        self.ckbgiantcompavpathlength_B.setChecked(True)
        self.ckbavpathlengthgeo_B.setChecked(True)
        self.ckbavggeopathlengthcomponents_B.setChecked(True)
        self.ckbavggeopathlengthgiantcomponent_B.setChecked(True)
        self.ckbavdegree_B.setChecked(True)
        self.ckbdensity_B.setChecked(True)
        self.ckbmaxbetweennesscentrality_B.setChecked(True)
        self.ckbavgbetweennesscentrality_B.setChecked(True)
        self.ckbassortativitycoefficient_B.setChecked(True)
        self.ckbclusteringcoefficient_B.setChecked(True)
        self.ckbtransitivity_B.setChecked(True)
        self.ckbsquareclustering_B.setChecked(True)
        self.ckbavgneighbordegree_B.setChecked(True)
        self.ckbavgdegreeconnectivity_B.setChecked(True)
        self.ckbavgdegreecentrality_B.setChecked(True)
        self.ckbavgclosenesscentrality_B.setChecked(True)
        self.ckbdiameter_B.setChecked(True)

    def unselectallA(self):
        '''Selects all text box's for network A.'''
        self.ckbsizeofcomponents_A.setChecked(False)
        self.ckbgiantcomponentsize_A.setChecked(False)
        self.ckbavnodesincomponents_A.setChecked(False)
        self.ckbisolatednodes_A.setChecked(False)
        self.ckbisolatedncountremoved_A.setChecked(False)
        self.ckbsubnodes_A.setChecked(False)
        self.ckbsubnodescount_A.setChecked(False)
        self.ckbavpathlength_A.setChecked(False)
        self.ckbavpathlengthcomp_A.setChecked(False)
        self.ckbgiantcompavpathlength_A.setChecked(False)
        self.ckbavpathlengthgeo_A.setChecked(False)
        self.ckbavggeopathlengthcomponents_A.setChecked(False)
        self.ckbavggeopathlengthgiantcomponent_A.setChecked(False)
        self.ckbavdegree_A.setChecked(False)
        self.ckbdensity_A.setChecked(False)
        self.ckbmaxbetweennesscentrality_A.setChecked(False)
        self.ckbavgbetweennesscentrality_A.setChecked(False)
        self.ckbassortativitycoefficient_A.setChecked(False)
        self.ckbclusteringcoefficient_A.setChecked(False)
        self.ckbtransitivity_A.setChecked(False)
        self.ckbsquareclustering_A.setChecked(False)
        self.ckbavgneighbordegree_A.setChecked(False)
        self.ckbavgdegreeconnectivity_A.setChecked(False)
        self.ckbavgdegreecentrality_A.setChecked(False)
        self.ckbavgclosenesscentrality_A.setChecked(False)
        self.ckbdiameter_A.setChecked(False)
        
    def unselectallB(self):
        '''Selects all text box's for network B.'''
        self.ckbsizeofcomponents_B.setChecked(False)
        self.ckbgiantcomponentsize_B.setChecked(False)
        self.ckbavnodesincomponents_B.setChecked(False)
        self.ckbisolatednodes_B.setChecked(False)
        self.ckbisolatedncountremoved_B.setChecked(False)
        self.ckbsubnodes_B.setChecked(False)
        self.ckbsubnodescount_B.setChecked(False)
        self.ckbavpathlength_B.setChecked(False)
        self.ckbavpathlengthcomp_B.setChecked(False)
        self.ckbgiantcompavpathlength_B.setChecked(False)
        self.ckbavpathlengthgeo_B.setChecked(False)
        self.ckbavggeopathlengthcomponents_B.setChecked(False)
        self.ckbavggeopathlengthgiantcomponent_B.setChecked(False)
        self.ckbavdegree_B.setChecked(False)
        self.ckbdensity_B.setChecked(False)
        self.ckbmaxbetweennesscentrality_B.setChecked(False)
        self.ckbavgbetweennesscentrality_B.setChecked(False)
        self.ckbassortativitycoefficient_B.setChecked(False)
        self.ckbclusteringcoefficient_B.setChecked(False)
        self.ckbtransitivity_B.setChecked(False)
        self.ckbsquareclustering_B.setChecked(False)
        self.ckbavgneighbordegree_B.setChecked(False)
        self.ckbavgdegreeconnectivity_B.setChecked(False)
        self.ckbavgdegreecentrality_B.setChecked(False)
        self.ckbavgclosenesscentrality_B.setChecked(False)
        self.ckbdiameter_B.setChecked(False)
        
    def check_checkbxs(self, metrics):
        '''Checks the check boxes to identify those which have been checked or 
        are not checked.'''
        basicA, basicB, optionA, optionB = metrics
        
        if self.ckbsizeofcomponents_A.isChecked():
            optionA['size_of_components']=True
        else: optionA['size_of_componets']=False
        
        if self.ckbgiantcomponentsize_A.isChecked():
            optionA['giant_component_size']=True
        else: optionA['giant_component_size']=False            
                  
        if self.ckbavnodesincomponents_A.isChecked():
            optionA['avg_size_of_components']=True
        else: optionA['avg_size_of_components']=False
        
        if self.ckbisolatednodes_A.isChecked():
            optionA['isolated_nodes']=True
        else: optionA['isoalted_nodes']=False

        if self.ckbisolatedncountremoved_A.isChecked():
            optionA['no_of_isoalted_nodes_removed']=True
        else: optionA['no+of_isolated_nodes_removed']=False
        
        if self.ckbsubnodes_A.isChecked():
            optionA['subnodes']=True
        else: optionA['subnodes']=False
        
        if self.ckbsubnodescount_A.isChecked():
            optionA['no_of_subnodes']=True
        else: optionA['no_of_subnodes']=False
        
        if self.ckbavpathlength_A.isChecked():
            optionA['avg_path_length']=True
        else: optionA['avg_path_length']=False
        
        if self.ckbavpathlengthcomp_A.isChecked():
            optionA['avg_path_length_of_components']=True
        else: optionA['avg_path_length_of_components']=False
        
        if self.ckbgiantcompavpathlength_A.isChecked():
            optionA['avg_path_length_of_giant_component']=True
        else: optionA['avg_path_length_of_giant_component']=False
        
        if self.ckbavpathlengthgeo_A.isChecked():
            optionA['avg_geo_path_length']=True
        else: optionA['avg_geo_path_length']=False
        
        if self.ckbavggeopathlengthcomponents_A.isChecked():
            optionA['avg_geo_path_length_of_components']=True
        else: optionA['avg_geo_path_length_of_components']=False
        
        if self.ckbavggeopathlengthgiantcomponent_A.isChecked():
            optionA['avg_geo_path_length_of_giant_component']=True
        else: optionA['avg_geo_path_length_of_giant_component']=False
        
        if self.ckbavdegree_A.isChecked():
            optionA['avg_degree']=True
        else: optionA['avg_degree']=False
        
        if self.ckbdensity_A.isChecked():
            optionA['density']=True
        else: optionA['density']=False
        
        if self.ckbmaxbetweennesscentrality_A.isChecked():
            optionA['maximum_betweenness_centrality']=True
        else: optionA['maximum_betweenness_centrality']=False
        
        if self.ckbavgbetweennesscentrality_A.isChecked():
            optionA['avg_betweenness_centrality']=True
        else: optionA['avg_betweenness_centrality']=False
        
        if self.ckbassortativitycoefficient_A.isChecked():
            optionA['assortativity_coefficient']=True
        else: optionA['assortativity_coefficient']=False
        
        if self.ckbclusteringcoefficient_A.isChecked():
            optionA['clustering_coefficient']=True
        else: optionA['clustering_coefficient']=False
        
        if self.ckbtransitivity_A.isChecked():
            optionA['transitivity']=True
        else: optionA['transitivity']=False
        
        if self.ckbsquareclustering_A.isChecked():
            optionA['square_clustering']=True
        else: optionA['square_clustering']=False
        
        if self.ckbavgneighbordegree_A.isChecked():
            optionA['avg_neighbor_degree']=True
        else: optionA['avg_neighbor_degree']=False
        
        if self.ckbavgdegreeconnectivity_A.isChecked():
            optionA['avg_degree_connectivity']=True
        else: optionA['avg_degree_connectivity']=False
        
        if self.ckbavgdegreecentrality_A.isChecked():
            optionA['avg_degree_centrality']=True
        else: optionA['avg_degree_centrality']=False
        
        if self.ckbavgclosenesscentrality_A.isChecked():
            optionA['avg_closenes_centrality']=True
        else: optionA['avg_closeness_centrality']=False
        
        if self.ckbdiameter_A.isChecked():
            optionA['diameter']=True
        else: optionA['diameter']=False
  
        #-----------for network B--------------------------------------------
        if self.ckbsizeofcomponents_B.isChecked():
            optionB['size_of_components']=True
        else: optionB['size_of_componets']=False
        
        if self.ckbgiantcomponentsize_A.isChecked():
            optionB['giant_component_size']=True
        else: optionB['giant_component_size']=False            
                  
        if self.ckbavnodesincomponents_B.isChecked():
            optionB['avg_size_of_components']=True
        else: optionB['avg_size_of_components']=False
        
        if self.ckbisolatednodes_B.isChecked():
            optionB['isolated_nodes']=True
        else: optionB['isoalted_nodes']=False

        if self.ckbisolatedncountremoved_B.isChecked():
            optionB['no_of_isoalted_nodes_removed']=True
        else: optionB['no+of_isolated_nodes_removed']=False
        
        if self.ckbsubnodes_B.isChecked():
            optionB['subnodes']=True
        else: optionB['subnodes']=False
        
        if self.ckbsubnodescount_B.isChecked():
            optionB['no_of_subnodes']=True
        else: optionB['no_of_subnodes']=False
        
        if self.ckbavpathlength_B.isChecked():
            optionB['avg_path_length']=True
        else: optionB['avg_path_length']=False
        
        if self.ckbavpathlengthcomp_B.isChecked():
            optionB['avg_path_length_of_components']=True
        else: optionB['avg_path_length_of_components']=False
        
        if self.ckbgiantcompavpathlength_B.isChecked():
            optionB['avg_path_length_of_giant_component']=True
        else: optionB['avg_path_length_of_giant_component']=False
        
        if self.ckbavpathlengthgeo_B.isChecked():
            optionB['avg_geo_path_length']=True
        else: optionB['avg_geo_path_length']=False
        
        if self.ckbavggeopathlengthcomponents_B.isChecked():
            optionB['avg_geo_path_length_of_components']=True
        else: optionB['avg_geo_path_length_of_components']=False
        
        if self.ckbavggeopathlengthgiantcomponent_B.isChecked():
            optionB['avg_geo_path_length_of_giant_component']=True
        else: optionB['avg_geo_path_length_of_giant_component']=False
        
        if self.ckbavdegree_B.isChecked():
            optionB['avg_degree']=True
        else: optionB['avg_degree']=False
        
        if self.ckbdensity_B.isChecked():
            optionB['density']=True
        else: optionB['density']=False
        
        if self.ckbmaxbetweennesscentrality_B.isChecked():
            optionB['maximum_betweenness_centrality']=True
        else: optionB['maximum_betweenness_centrality']=False
        
        if self.ckbavgbetweennesscentrality_B.isChecked():
            optionB['avg_betweenness_centrality']=True
        else: optionB['avg_betweenness_centrality']=False
        
        if self.ckbassortativitycoefficient_B.isChecked():
            optionB['assortativity_coefficient']=True
        else: optionB['assortativity_coefficient']=False
        
        if self.ckbclusteringcoefficient_B.isChecked():
            optionB['clustering_coefficient']=True
        else: optionB['clustering_coefficient']=False
        
        if self.ckbtransitivity_B.isChecked():
            optionB['transitivity']=True
        else: optionB['transitivity']=False
        
        if self.ckbsquareclustering_B.isChecked():
            optionB['square_clustering']=True
        else: optionB['square_clustering']=False
        
        if self.ckbavgneighbordegree_B.isChecked():
            optionB['avg_neighbor_degree']=True
        else: optionB['avg_neighbor_degree']=False
        
        if self.ckbavgdegreeconnectivity_B.isChecked():
            optionB['avg_degree_connectivity']=True
        else: optionB['avg_degree_connectivity']=False
        
        if self.ckbavgdegreecentrality_B.isChecked():
            optionB['avg_degree_centrality']=True
        else: optionB['avg_degree_centrality']=False
        
        if self.ckbavgclosenesscentrality_B.isChecked():
            optionB['avg_closenes_centrality']=True
        else: optionB['avg_closeness_centrality']=False
        
        if self.ckbdiameter_B.isChecked():
            optionB['diameter']=True
        else: optionB['diameter']=False
        
        
        self.metrics = basicA, basicB, optionA, optionB
        return self.metrics

    def applyandclose(self):
        '''Calls for the check boxes to be checked for their state and then 
        packages up the containers into a single container. The single container 
        then replaces the latest version in the window class.'''
        self.metrics = self.check_checkbxs(self.metrics)
        self.basic_metrics_A, self.basic_metrics_B, self.option_metrics_A, self.option_metrics_B = self.metrics
        window.updateGUI_metrics(self.metrics)
        self.close() 

    def closeclick(self):
        '''Closes the window when initiated via the close button.'''
        self.close()
    def get_metrics(self, metrics):
        '''Does not do anything.'''    
        self.metrics = metrics
        basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B
                 
class OptionsWindow(QWidget):
    def __init__(self, parent = None):  
        QWidget.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        fontbold = QFont("Calibri", 10, QFont.Bold)        
        
        self.colactive = None
        self.colinactive = None
        self.timedelay, self.col1, self.col2, self.destlocation,self.pertimestep,self.saveimage,self.analysistype,self.multiiterations, self.numofiterations,self.saveoutputfile, self.imagedpi,self.nxpglocation,self.runallseqmodels,self.nodesizemeth,self.edgesizemeth=window.updatewindow_options() 
        self.timedelay = str(self.timedelay)
        
        vpos = 15
        lblsaveoutputfile = QLabel('Save output text file:',self)
        lblsaveoutputfile.move(12, vpos)
        lblsaveoutputfile.adjustSize()
        self.ckbxsaveoutputfile = QCheckBox(self)
        self.ckbxsaveoutputfile.move(120,vpos)
        if self.saveoutputfile == True:        
            self.ckbxsaveoutputfile.setChecked(True)
        else: self.ckbxsaveoutputfile.setChecked(False)
        
        vpos += 20
        lbltimetitle = QLabel('Pause between failure time steps',self)
        lbltimetitle.move(12,vpos)
        lbltimetitle.setFont(fontbold)
        lbltimetitle.adjustSize()
        vpos += 20
        lbltimedelay = QLabel('Time(secs) between iterations: ',self)
        lbltimedelay.move(12,vpos)
        lbltimedelay.adjustSize()
        self.txttimedelay = QLineEdit(self) 
        self.txttimedelay.move(170,vpos-3)
        self.txttimedelay.setFixedWidth(50)
        self.txttimedelay.setText(str(self.timedelay))
        self.txttimedelay.setToolTip('The minimum time(seconds) between iterations. Min = 0, Max = 300')        
        self.validator = QIntValidator(0,300,self.txttimedelay)       
        self.txttimedelay.setValidator(self.validator)
        vpos += 20
        lblnodesandedges = QLabel('Node and Edge colours',self)
        lblnodesandedges.move(12,vpos)
        lblnodesandedges.setFont(fontbold)
        lblnodesandedges.adjustSize()
        vpos+=20
        lblcolor1 = QLabel("Active features:", self)
        lblcolor1.adjustSize()        
        lblcolor1.move(12,vpos-1)
        self.colors= 'red','green','blue', 'black', 'cyan', 'magenta', 'yellow'
        self.cmbxcolor1 = QComboBox(self)
        self.cmbxcolor1.move(150,vpos-3)
        self.cmbxcolor1.addItems(self.colors)
        vpos+=25
        lblcolor2 = QLabel("Inactive features:", self)
        lblcolor2.adjustSize()
        lblcolor2.move(12,vpos-1)
        self.cmbxcolor2 = QComboBox(self)
        self.cmbxcolor2.move(150,vpos-3)
        self.cmbxcolor2.addItems(self.colors)
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col1:
                self.cmbxcolor1.setCurrentIndex(int(index))        
                index = 999
            index += 1
       
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col2:
                self.cmbxcolor2.setCurrentIndex(int(index))
                index = 999
            index += 1
        self.cmbxcolor1.activated[str].connect(self.getcoloractive)
        self.cmbxcolor2.activated[str].connect(self.getcolorinactive)
        vpos+=20
        lbltimedelay = QLabel('Save image of network during failure: ',self)
        lbltimedelay.move(12,vpos)
        lbltimedelay.setFont(fontbold)        
        lbltimedelay.adjustSize()
        vpos+=20
        lblsave = QLabel('Save images?',self)        
        lblsave.move(12,vpos)
        lblsave.adjustSize()
        self.ckbxsave = QCheckBox(self)
        self.ckbxsave.move(100,vpos+1)
        self.ckbxsave.setChecked(False)
        self.ckbxsave.stateChanged.connect(self.updatedependents)
        vpos+=20
        self.lblsavefreq = QLabel('Save every',self)
        self.lblsavefreq.move(12, vpos+3)
        self.lblsavefreq.adjustSize()        
        self.txtsavefreq = QLineEdit(self)
        self.txtsavefreq.move(77,vpos)
        self.txtsavefreq.setFixedWidth(50)
        if self.pertimestep <> '':
            self.txtsavefreq.setText(str(self.pertimestep))
        self.lblsavefreq2 = QLabel('time step(s)',self)
        self.lblsavefreq2.move(135,vpos+3)
        self.lblsavefreq2.adjustSize()
        vpos+=25
        self.lblsavelocation = QLabel('Destination & name:', self)
        self.lblsavelocation.move(12,vpos)
        self.lblsavelocation.adjustSize()
        self.btnbrowse = QPushButton("Browse",self)
        self.btnbrowse.move(130,vpos-5)
        self.btnbrowse.adjustSize()
        self.btnbrowse.clicked.connect(self.browsing)
        vpos+=20
        self.txtdestlocation = QLineEdit(self)
        self.txtdestlocation.move(12,vpos)
        self.txtdestlocation.setFixedWidth(200)
        self.txtdestlocation.setText(self.destlocation)
        vpos+=24
        self.lbldpiofimages = QLabel('Image dpi:', self)
        self.lbldpiofimages.move(12,vpos+2)
        self.lbldpiofimages.adjustSize()
        self.txtimagedpi = QLineEdit(self)
        self.txtimagedpi.move(80,vpos)
        self.txtimagedpi.setFixedWidth(50)
        self.txtimagedpi.setText(str(self.imagedpi))
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
            self.lbldpiofimages.setEnabled(False)
            self.txtimagedpi.setEnabled(False)
        vpos+=25
        lblrunmultipletimes = QLabel('Run failure model multiple times:',self)
        lblrunmultipletimes.move(12,vpos)
        lblrunmultipletimes.setFont(fontbold)
        lblrunmultipletimes.adjustSize()
        self.ckbxmultipleruns = QCheckBox(self)
        self.ckbxmultipleruns.move(200,vpos+2)
        vpos+=20
        self.lblnumberofiterations = QLabel('Number of iterations:',self)
        self.lblnumberofiterations.move(12,vpos+2)
        self.lblnumberofiterations.adjustSize()
        self.txtnumofiterations = QLineEdit(self)
        self.txtnumofiterations.move(120,vpos)
        self.txtnumofiterations.setFixedWidth(30)
        self.ckbxmultipleruns.stateChanged.connect(self.multiplerunschanged)
        vpos+=30
        self.lblrunthreeseqtypes = QLabel('Run the three seq failure models:', self)
        self.lblrunthreeseqtypes.move(12,vpos)
        self.lblrunthreeseqtypes.adjustSize()
        self.ckbxrunthreeseqtypes = QCheckBox(self)
        self.ckbxrunthreeseqtypes.move(190,vpos)
                
        if self.multiiterations == True:
            self.ckbxmultipleruns.setChecked(True)
            self.txtnumofiterations.setText(str(self.numofiterations))
            if self.runallseqmodels == True:
                self.ckbxrunthreeseqtypes.setChecked(True)
        else:
            self.ckbxmultipleruns.setChecked(False)
            self.lblnumberofiterations.setEnabled(False)
            self.txtnumofiterations.setEnabled(False)
            self.ckbxrunthreeseqtypes.setEnabled(False)
        vpos+=30
        self.lblnodesizeonmetric = QLabel('Base node size on a metric',self)
        self.lblnodesizeonmetric.move(12,vpos)
        self.lblnodesizeonmetric.adjustSize()
        vpos+=20
        self.dpdwnmetricfornodesize = QComboBox(self)
        self.dpdwnmetricfornodesize.move(12,vpos)
        self.dpdwnmetricfornodesize.addItems(['None','Degree','Betweenness Centrality','Clustering Coefficent'])
        self.dpdwnmetricfornodesize.setCurrentIndex(self.nodesizemeth)
        vpos+=30
        self.lbledgesizeonmetric = QLabel('Base edge size on a metric',self)
        self.lbledgesizeonmetric.move(12,vpos)
        self.lbledgesizeonmetric.adjustSize()
        vpos+=20
        self.dpdwnmetricforedgesize = QComboBox(self)
        self.dpdwnmetricforedgesize.move(12,vpos)
        self.dpdwnmetricforedgesize.addItems(['None','Betweenness Centrality'])
        self.dpdwnmetricforedgesize.setCurrentIndex(self.edgesizemeth)
        vpos+=30
        self.lblnxpglocation = QLabel('nxpg module location:',self)
        self.lblnxpglocation.move(12,vpos)
        self.lblnxpglocation.adjustSize()
        self.btnnxpgbrowse = QPushButton("Browse",self)
        self.btnnxpgbrowse.move(130,vpos-5)
        self.btnnxpgbrowse.adjustSize()
        self.btnnxpgbrowse.clicked.connect(self.browsing_nxpg)
        vpos+=20
        self.txtnxpglocation = QLineEdit(self)
        self.txtnxpglocation.move(12,vpos)
        self.txtnxpglocation.setFixedWidth(200)
        self.txtnxpglocation.setText(self.nxpglocation)
        vpos+=40       
        
        self.apply = QPushButton("Apply", self)
        self.apply.adjustSize()
        self.apply.move(145,vpos)
        self.apply.clicked.connect(self.applyandclose)
        self.apply.setToolTip("Apply any changes and close the window.")
        self.closebtn = QPushButton("Close", self)
        self.closebtn.adjustSize()
        self.closebtn.move(70,vpos)
        self.closebtn.clicked.connect(self.closeclick)
        self.closebtn.setToolTip("Close the window without saving any changes.")
        vpos+=30
        self.setGeometry(300,200,230,vpos) #vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Options Window') #title of window
        self.setWindowIcon(QIcon('logo.png'))
        self.updatedependents()
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
            if self.ckbxrunthreeseqtypes.isChecked() == True:
                    self.runallseqmodels = True
        else:
            self.multiiterations = False
            self.runallseqmodels = False
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
                try:
                    self.imagedpi = int(self.txtimagedpi.text())
                except:
                    QMessageBox.question(self, 'Message',
                            "Value for dpi in an incorrect format. \nPlease enter an integer.", QMessageBox.Ok)
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
        if self.ckbxsaveoutputfile.isChecked() == True:
            self.saveoutputfile = True
        else: self.saveoutputfile = False
        #if self.dpdwnmetricfornodesize.currentIndex() == 0:
        window.updateGUI_options(self.destlocation, self.pertimestep, self.saveimage,self.multiiterations,self.numofiterations,self.colactive,self.colinactive,self.timedelay,self.saveoutputfile,self.imagedpi,self.nxpglocation,self.runallseqmodels,self.dpdwnmetricfornodesize.currentIndex(),self.dpdwnmetricforedgesize.currentIndex())
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
            self.lbldpiofimages.setEnabled(True)
            self.txtimagedpi.setEnabled(True)
        else:
            self.lblsavefreq.setEnabled(False)
            self.txtsavefreq.setEnabled(False)     
            self.lblsavefreq2.setEnabled(False)
            self.lblsavelocation.setEnabled(False)
            self.txtdestlocation.setEnabled(False)
            self.btnbrowse.setEnabled(False)
            self.lbldpiofimages.setEnabled(False)
            self.txtimagedpi.setEnabled(False)
    def browsing(self):
        fileName = QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        self.txtdestlocation.setText(fileName)
        self.destlocation = fileName
    def browsing_nxpg(self):
        fileName = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.txtnxpglocation.setText(fileName)
        self.nxpglocation = fileName
    def multiplerunschanged(self):
        if self.ckbxmultipleruns.isChecked() == True:
            self.lblnumberofiterations.setEnabled(True)
            self.txtnumofiterations.setEnabled(True)
            self.ckbxrunthreeseqtypes.setEnabled(True)
        elif self.ckbxmultipleruns.isChecked() == False:
            self.lblnumberofiterations.setEnabled(False)
            self.txtnumofiterations.setEnabled(False)
            self.ckbxrunthreeseqtypes.setEnabled(False)
            
class ViewGraphs(QDialog):   
    "Class for the window which allows the viewing of the results in terms of the graph metrics."
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        
        self.metrics, self.failure = window.updatewindow_viewgraphs() #gets the metrics value
        basicA, basicB, optionA, optionB = self.metrics
        self.valuesA = basicA,optionA
        #self.valuesetA = node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A,size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,av_path_length_geo_A,giant_component_av_path_length_A,average_degree_A,inter_removed_count_A
        self.valuesB = basicB,optionB
        #self.valuesetB = node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B,size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,av_path_length_geo_B,giant_component_av_path_length_B,average_degree_B,inter_removed_count_B
            
        #self.metriclist = ['Number of nodes removed', 'Number of nodes left', 'Number of edges left', 'Number of components', 'None']
        self.metriclist = self.makemetriclist(basicA, optionA)
        print 'self.metriclist is:', self.metriclist
        exit()
        if self.failure['stand_alone'] == False:
            net_list = ['A','B']
        else:
            net_list = ['A']

        self.figureGraph = None        
        self.net1cbx = QComboBox(self)
        self.net1cbx.addItems(net_list)
        self.net1cbx.move(45, 25)    
        self.net2cbx = QComboBox(self)
        self.net2cbx.addItems(net_list)
        self.net2cbx.move(45, 55)
        
        lblop1 = QLabel('Plot 1:', self)
        lblop1.adjustSize()
        lblop1.move(5, 28)
        self.option1cbx = QComboBox(self)
        self.option1cbx.addItems(self.metriclist)
        self.option1cbx.move(85, 25)
        lblop2 = QLabel('Plot 2:', self)
        lblop2.adjustSize()
        lblop2.move(5, 58)
        self.option2cbx = QComboBox(self)
        self.option2cbx.addItems(self.metriclist)      
        self.option2cbx.move(85, 55)
        cancelbtn = QPushButton('Close', self)
        cancelbtn.setToolTip('Close the window')        
        cancelbtn.move(124, 80)
        cancelbtn.clicked.connect(self.cancelclick)
        
        self.net1cbx.activated[str].connect(self.networkchanged)        
        self.net2cbx.activated[str].connect(self.networkchanged)
        
        self.option1cbx.activated.connect(self.option1changed)             
        self.option2cbx.activated.connect(self.option2changed)

        self.setGeometry(900,500,300,110)#vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Graph parameters')  #title of windpw          
        self.setWindowIcon(QIcon('logo.png'))
        self.show()#show GUI window  
        self.option1value = 0
        self.option2value = 1
        
        self.figureGraph = pl.figure() #create the figure
        self.figureGraph = pl.gcf() #allow the title to be changed
        self.figureGraph.canvas.set_window_title('Results plot') #assign a title
        pl.ion() #make the plot interactive so the update process is easier
        pl.show() #this displays a blank plot which I then want the graph to be displayed in
        self.option2cbx.removeItem(self.option1value) #from list2, remove the item selected in list1
        self.option1cbx.removeItem(self.option2value) #from list1 remove the item selected in list2
        self.applyclick()
        
    def option1changed(self):
        '''Update the option in combo box 2 and draw the graph.'''
        if self.net1cbx.currentText() == self.net2cbx.currentText():
            index = self.index(self.option2cbx.currentText())
            #clear the list in box 2
            self.option2cbx.clear()
            #add all option back to the list2
            self.option2cbx.addItems(self.metriclist)
            #set option 2 to what it was on before 
            self.option2cbx.setCurrentIndex(index)
            #get the position for the data 
            index = self.index(self.option1cbx.currentText()) #get metric index for data list
            #remove the item from box2 selected in box1
            self.option2cbx.removeItem(index)  
            #run the function to refresh the plots
            self.applyclick()
        else:
            #print 'different networks selected'
            self.applyclick()
        
    def option2changed(self):
        '''Update the option in combo box 2 and draw the graph.''' 
        if self.net1cbx.currentText() == self.net2cbx.currentText():
            index = self.index(self.option1cbx.currentText())
            #clear the list in box 2
            self.option1cbx.clear()
            #add all option back to the list2
            self.option1cbx.addItems(self.metriclist)
            #set option 2 to what it was on before 
            self.option1cbx.setCurrentIndex(index)
            #get the text in option 2
            index = self.index(self.option2cbx.currentText())
            #remove item selected in box 2 from box1
            self.option1cbx.removeItem(index)     
            #run the function to refresh the plots
            self.applyclick()
        else:
            #print 'different networks selected'
            self.applyclick()
            
    def index(self,text):
        '''Find the index given the text. Dynamic method.'''
        #print self.metriclist
        index = 0
        for item in self.metriclist:
            if text == item:
                #print 'found a match'
                return index
            index += 1
                        
    def applyclick(self):
        '''Runs the code to identify the metrics requested for the visualisation.'''   
        self.valuenames = 'Node count removed', 'Count nodes left', 'Number of edges left', 'Number of components', 'None','','','','','','','','','','','','','','','','','','','',''
        
        if self.figureGraph == None or self.figureGraph.canvas.manager.window == None: #if figure model window has not been opened yet
            self.figureGraph = pl.figure()
            pl.ion()
            pl.show()  
        #need the following in case the user closes the window 
        try:
            self.figureGraph.canvas.set_window_title('Results plot') 
        except:
            self.figureGraph = None
            self.figureGraph = pl.figure()
            self.figureGraph.canvas.set_window_title('Results plot') 
        #top plot
        pl.subplot(211)
        pl.cla() #clear the plot   
        if self.net1cbx.currentText() == 'A':
            #if network A selected
            values = self.identifymetric(self.option1cbx.currentText(),self.valuesA)
            pl.plot(values, 'b', linewidth=2, label=self.option1cbx.currentText())
        else:
            #if network B selected
            values = self.identifymetric(self.option1cbx.currentText(),self.valuesB)
            pl.plot(values, 'b', linewidth=2, label=self.option1cbx.currentText())
        pl.xlabel('Number of nodes removed')
        pl.ylim(ymin=0)
        if self.net1cbx.currentText() == 'A':
            ymax =max(values)
        else:
            ymax =max(values)
        pl.ylim(ymax=ymax+0.5);pl.xlim(xmin=0)
        
        #secnd plot
        pl.subplot(212);pl.cla()
        if  self.net2cbx.currentText() == 'A':
            values = self.identifymetric(self.option2cbx.currentText(),self.valuesA)
            pl.plot(values, 'b', linewidth=2, label=self.option2cbx.currentText())
        else:
            values = self.identifymetric(self.option2cbx.currentText(),self.valuesB)
            pl.plot(values, 'b', linewidth=2, label=self.option2cbx.currentText())
                
        pl.xlabel('Number of nodes removed')
        pl.ylim(ymin=0)
        if self.net2cbx.currentText() == 'A':
            ymax =max(values)
        else:
            ymax =max(values)
        pl.ylim(ymax=ymax+0.5);pl.xlim(xmin=0)
        pl.show() #show the window 

    def cancelclick(self):
        '''Close the selection box and graph window when the cancel button is 
        clicked.'''
        self.close()            
        pl.close()
        
    def getval(self):
        '''Used to pass varaibles between classes.'''
        return self.metric1, self.metric2

    def closeEvent(self, event):
        '''Closes the windows.'''
        pl.close()

    def identifymetric(self, metric,values):
        '''Method to idenitfy the metric requested, and assign the correct 
        value for the position of its data in the lists of lists.'''
        #print 'IN Identify metric'
        print 'METRIC IS:', metric
        basic, option = values
        if metric == 'Number of nodes removed':
            metric = basic['no_of_nodes_removed']
        elif metric == 'Number of nodes':
            metric = basic['no_of_nodes']
        elif metric == 'Number of edges':
            metric = basic['no_of_edges']
        elif metric == 'Number of components':
            metric = basic['no_of_components']
        elif metric == 'Number of isolated nodes':
            metric = basic['no_of_isolated_nodes']
        #------option metrics-------------------------------
        elif metric == 'Giant component size':
            metric = option['giant_component_size']
        elif metric == 'Average number of nodes in components':
            metric = option['avg_size_of_components']
        elif metric == 'Number of isolates removed':
            metric = option['no_of_isolated_nodes_removed']
        elif metric == 'Number of subgraph nodes':
            metric = option['no_of_subnodes']
        elif metric == 'Average path length':
            metric = option['avg_path_length']
        elif metric == 'Average path length of giant component':
            metric = option['avg_path_length_of_giant_component']
        elif metric == 'Average geo path length':
            metric = option['avg_geo_path_length']
        elif metric == 'Average geo path length of giant component':
            metric = option['avg_geo_path_length_of_giant_component']     
        elif metric == 'Average node degree':
            metric = option['avg_degree']
        elif metric == 'Density':
            metric = option['density']
        elif metric == 'Maximum betweenness centrality':
            metric = option['maximum_betweenness_centrality']
        elif metric == 'Avgerage betweenness centrality':
            metric = option['avg_betweenness_centrality']
        elif metric == 'Assortativity coefficient':
            metric = option['assortativity coefficient']
        elif metric == 'Clustering coefficient':
            metric = option['clustering_coefficient']
        elif metric == 'Transitivity':
            metric = option['transitivity']
        elif metric == 'Square clustering':
            metric = option['square_clustering']
        elif metric == 'Average neighbor degree':
            metric = option['avg_neighbor_degree']
        elif metric == 'Average degree connectivity':
            metric = option['avg_degree_connectivity']
        elif metric == 'Average degree centrality':
            metric = option['avg_degree_centrality']
        elif metric == 'Average closeness centrality':
            metric = option['avg_closeness_centrality']
        elif metric == 'Diameter':
            metric = option['diameter']
        elif metric == 'None': 
            metric = 99
        else:
            QMessageBox.warning(self, 'Error!', "Internal error. Metric value error in identification porcess.")
            print 'Uncategorised'
        return metric

    def makemetriclist(self,basic,option):
        '''This checks which metrics are true and false and creates a list from 
        them for the metric list in the dialog window.'''
        
        metric_list = []
        metric_list.append('Number of nodes removed')
        metric_list.append('Number of nodes')
        metric_list.append('Number of edges')
        metric_list.append('Number of components')
        metric_list.append('Number of isolated nodes')
        
        if option['giant_component_size'] <> False:
            metric_list.append('Giant component size')
        if option['avg_size_of_components'] <> False:
            metric_list.append('Average number of nodes in components')
        if option['no_of_isolated_nodes_removed'] <> False:
            metric_list.append('Number of isolates removed')
        if option['no_of_subnodes'] <> False:
            metric_list.append('Number of subgraph nodes')
        if option['avg_path_length'] <> False:
            metric_list.append('Average path length')
        if option['avg_path_length_of_giant_component'] <> False:
            metric_list.append('Average path length of giant component')
        if option['avg_geo_path_length'] <> False:            
            metric_list.append('Average geo path length')
        if option['avg_geo_path_length_of_giant_component'] <> False:
            metric_list.append('Average geo path length of giant component')
        if option['avg_degree'] <> False:
            metric_list.append('Average node degree')
        if option['density'] <> False:
            metric_list.append('Density')
        if option['maximum_betweenness_centrality'] <> False:
            metric_list.append('Maximum betweenness centrality')
        if option['avg_betweenness_centrality'] <> False:
            metric_list.append('Avgerage betweenness centrality')
        if option['assortativity coefficient'] <> False:
            metric_list.append('Assortativity coefficient')
        if option['clustering_coefficient'] <> False:
            metric_list.append('Clustering coefficient')
        if option['transitivity'] <> False:
            metric_list.append('Transitivity')
        if option['square_clustering'] <> False:
            metric_list.append('Square clustering')
        if option['avg_neighbor_degree'] <> False:
            metric_list.append('Average neighbor degree')
        if option['avg_degree_connectivity'] <> False:
            metric_list.append('Average degree connectivity')
        if option['avg_degree_centrality'] <> False:
            metric_list.append('Average degree centrality')
        if option['avg_closeness_centrality'] <> False:
            metric_list.append('Average closeness centrality')
        if option['diameter'] <> False:
            metric_list.append('Diameter')
        
        return metric_list
       
class Window(QMainWindow):
    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        #Check  networkx files can be loaded
        try:
            import networkx as nx
        except:
            QMessageBox.warning(self, 'Import Error', 'Could not import networkx. The application will now close.')
            qApp.quit
        #Check the files for the database connection can be loaded.
        try:
            import osgeo.ogr as ogr
        except:
            QMessageBox.warning(self,'Import Error!', "Could not import the osgeo.ogr library. There will be no database connectivity as a result.")

        try:
            try: 
                sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
                import nx_pgnet #,nx_pg
            except:
                pass
                #sys.path.append('C:/Users/Craig/Documents/GitRepo/nx_pgnet')
        except:
            QMessageBox.warning(self, 'Import Error!', 'Could not import the nx_pgnet or nx_pg modules. This will not allow the database conection to work.')
        
        #set initial location and call the function to import the module        
        self.nxpglocation = 'C:/a8243587_DATA/GitRepo/nx_pgnet'
        #self.try_nxpg_import()
        can_use_db = True
        #initiate thread
        self.thread = Worker()
        '''
        #db parameters here to save having to type them in every time at the moment
        self.DBNAME = 'inter_london'
        self.HOST = 'localhost'
        self.PORT = '5433'
        self.USER = 'postgres'
        self.PASSWORD = 'aaSD2011'        
        self.NETNAME = 'power_lines'
        '''
        self.DBNAME = None
        self.HOST = None
        self.PORT = None
        self.USER = None
        self.PASSWORD = None        
        self.NETNAME = None
        self.dbconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        self.write_step_to_db=False;self.write_results_table=False;self.store_n_e_atts=False
        self.parameters = None
        self.running = False
        self.pause = False
        changedA = True
        changedB = True
        self.lastparam1A = None;self.lastparam2A = None;self.lastparam3A = None
        self.lastparam1B = None;self.lastparam2B = None;self.lastparam3B = None
        self.first = True
        self.figureModel = None
        self.iterate = True
        self.timestep = -1
        self.cancel = False
        self.positions = None
        self.G = None; self.GnetB = None
        self.masterAnet = None; self.masterBnet = None
        self.graphvis = None
        self.analysistype = 'Single'
        self.fullanalysis = False
        self.active = 1
        self.inactive = 0
        self.timedelay = 2
        self.coloractive = 'green'
        self.colorinactive = 'red'
        self.imagedestlocation = ''
        self.pertimestep = 1
        self.whenToSave = []
        self.saveimage = False
        self.multiiterations = False
        self.numofiterations = 1 
        self.iterationsdone = 0
        self.saveoutputfile = True
        self.imagedpi = 100
        self.runallseqmodels = False
        self.nodesizingmeth = 0
        self.edgesizingmeth = 0
        self.metrics = self.sort_metrics()
        self.geo_vis = None
        
        #create actions for menues
        RunAction = QAction('&Run',self)
        RunAction.setShortcut('Ctrl+R')
        RunAction.setStatusTip('Run the selected analysis')
        RunAction.triggered.connect(self.full_analysis)       
        
        exitAction = QAction('&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        exitAction.triggered.connect(self.closeall)

        optionsAction = QAction('&View Options', self)
        optionsAction.setShortcut('Ctrl+P')
        optionsAction.setStatusTip('Open network view options window')
        optionsAction.triggered.connect(self.showwindow_options)

        metricsAction = QAction('&Metrics', self)
        metricsAction.setShortcut('Ctrl+M')
        metricsAction.setStatusTip('Open metrics window')
        metricsAction.triggered.connect(self.showwindow_metrics)
    
        failoptionAction = QAction('&Options',self)
        failoptionAction.setStatusTip('Option failure options window')
        failoptionAction.triggered.connect(self.show_fail_option_window)
    
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load node and edge lists from .txt file')
        openAction.triggered.connect(self.openfileA)
        
        resetAction = QAction('&Cancel/Reset', self)
        resetAction.setStatusTip('Cancel the analysis')
        resetAction.triggered.connect(self.reset)
        
        ClearAllAction = QAction('&Clear all', self)
        ClearAllAction.setShortcut('Ctrl+E')
        ClearAllAction.setStatusTip('Clear the input text boxes')
        ClearAllAction.triggered.connect(self.clearAll)
        
        ClearAAction = QAction('&Inputs for A', self)
        ClearAAction.setStatusTip('Clear the input text boxes for network A')
        ClearAAction.triggered.connect(self.clearA)

        ClearBAction = QAction('&Inputs for B', self)
        ClearBAction.setStatusTip('Clear the input text boxes for network B')
        ClearBAction.triggered.connect(self.clearB)        
        
        ClearDepeEdgesAction = QAction('&Dependency Edges', self)
        ClearDepeEdgesAction.setStatusTip('Clear the input text for the dependency edges')        
        ClearDepeEdgesAction.triggered.connect(self.clearDependencyEdges)
        
        viewnetAction = QAction('&View Network', self)
        viewnetAction.setShortcut('Ctrl+D')
        viewnetAction.setStatusTip('View the network')
        viewnetAction.triggered.connect(self.drawview)

        saveConfigAction = QAction('Save a Config file', self)
        saveConfigAction.triggered.connect(self.saveConfig)
        
        openConfigAction = QAction('Open a Config file',self)
        openConfigAction.triggered.connect(self.openConfig)

        getDegreeDistAction = QAction('&Degree Distribution',self)
        getDegreeDistAction.setStatusTip('Return the degree distribution of the network') 
        changedA = getDegreeDistAction.triggered.connect(self.calcDegreeDist, changedA)
        
        massCalcAction = QAction('&Many Metrics',self)
        massCalcAction.setStatusTip('Calcualte a range of metrics in one process')
        massCalcAction.triggered.connect(self.massCalc)        
        
        metricsExportAction = QAction('&Export Metrics',self)
        metricsExportAction.setStatusTip('Export a suite of metrics to a text file')
        metricsExportAction.triggered.connect(self.export)

        metricsGraphAction = QAction('&Plot Graph',self)
        metricsGraphAction.setStatusTip('Not in use')
        metricsGraphAction.triggered.connect(self.plotGraph)
        
        calcClusteringAction = QAction('&Clustering(Tri)',self)
        calcClusteringAction.setStatusTip('Calcualte the clustering coefficient')
        calcClusteringAction.triggered.connect(self.calcClustering)

        calcClusteringSqAction = QAction('&Clustering(Sq)',self)
        calcClusteringSqAction.setStatusTip('Calculate the square clustering coefficent')  
        calcClusteringSqAction.triggered.connect(self.calcClusteringSq)
        
        calcAverageDegreeAction = QAction('&Average Node Degree', self)
        calcAverageDegreeAction.setStatusTip('Return the average node degree')
        calcAverageDegreeAction.triggered.connect(self.calcAvDegree)
        
        calcAssortativityAction = QAction('&Assortativity',self)
        calcAssortativityAction.setStatusTip('Calculanetworks =  GA, GB, GtempA, GtempBte the assortativity coefficent (node degree)')
        calcAssortativityAction.triggered.connect(self.calcAssortativity)
        
        calcBetweennessAction = QAction('&Betweenness Centrality',self)
        calcBetweennessAction.setStatusTip('Calculate the betweenness centrality')
        calcBetweennessAction.triggered.connect(self.calcBetweenness)
        
        calcCycleBasisAction = QAction('&Cycle Basis',self)        
        calcCycleBasisAction.setStatusTip('Count the number of cycle basis')
        calcCycleBasisAction.triggered.connect(self.calcCycleBasis)
        
        calcAvPathLengthAction = QAction('&Average Path Length',self)
        calcAvPathLengthAction.setStatusTip('Calculate the topological average path length')
        calcAvPathLengthAction.triggered.connect(self.calcAvPathLength)
        
        AtoBEdgesAction = QAction('&A to B Edges',self)
        AtoBEdgesAction.setStatusTip('Randomly create a set of dependency edges (A to B)')
        AtoBEdgesAction.triggered.connect(self.AtoBEdges)
        
        BtoAEdgesAction = QAction('&B to A Edges',self)
        BtoAEdgesAction.setStatusTip('Randomly create a set of dependency edges (B to A)') 
        BtoAEdgesAction.triggered.connect(self.BtoAEdges)
               
        self.statusBar() #create status bar 
        menubar=self.menuBar() #create menu bar
        fileMenu = menubar.addMenu('&File') #add file menu
        editMenu = menubar.addMenu('&Edit')
        foMenu = menubar.addMenu('&Failure Options') #add edit menu
        calcMenu = menubar.addMenu('&Metrics') #add mnetworks =  GA, GB, GtempA, GtempBetric calculation menu
        
        #add actions to file and edit menu's        
        editMenu.addAction(viewnetAction)
        editMenu.addAction(resetAction)
        editMenu.addAction(optionsAction)
        editMenu.addAction(saveConfigAction)
        editMenu.addAction(openConfigAction)
        foMenu.addAction(RunAction)
        foMenu.addAction(failoptionAction) 
        foMenu.addAction(metricsAction)
        subEdges_menu = foMenu.addMenu('Random Dependency Edges')
        subEdges_menu.addAction(AtoBEdgesAction)
        subEdges_menu.addAction(BtoAEdgesAction)
        subClear_menu = editMenu.addMenu('Clear')
        subClear_menu.addAction(ClearAllAction)        
        subClear_menu.addAction(ClearAAction)
        subClear_menu.addAction(ClearBAction)
        subClear_menu.addAction(ClearDepeEdgesAction)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        calcMenu.addAction(getDegreeDistAction) 
        subCalc_menu = calcMenu.addMenu('Calculate')
        calcMenu.addAction(massCalcAction)
        calcMenu.addAction(metricsGraphAction)
        calcMenu.addAction(metricsExportAction)
        subCalc_menu.addAction(calcClusteringAction)
        subCalc_menu.addAction(calcClusteringSqAction)
        subCalc_menu.addAction(calcAverageDegreeAction)
        subCalc_menu.addAction(calcAssortativityAction)
        subCalc_menu.addAction(calcBetweennessAction)
        subCalc_menu.addAction(calcCycleBasisAction)
        subCalc_menu.addAction(calcAvPathLengthAction)

        #create and set some lables
        self.lbl4 = QLabel("Ready", self)
        self.lbl4.move(50,201)
        self.lbl4.adjustSize() 
        fontbold = QFont("Calibri", 10, QFont.Bold)      

        lblState = QLabel("STATE: ", self)
        lblState.move(6,200)
        lblState.setFont(fontbold)
        lblState.adjustSize() 
        #set and create GUI features for the analysis type
        lblAType = QLabel("Analysis types",self)
        lblAType.setFont(fontbold)
        lblAType.adjustSize()        
        lblAType.move(25,25)
        self.ckbxSingle = QCheckBox("Single",self)
        self.ckbxSingle.adjustSize()
        self.ckbxSingle.move(25,45)
        self.ckbxSingle.setToolTip("Remove one node and relpace before the next node is removed")
        self.ckbxSingle.toggle()
        self.ckbxSingle.stateChanged.connect(self.ckbxoptionlimited)
        self.ckbxSequential = QCheckBox("Sequential",self)
        self.ckbxSequential.adjustSize()
        self.ckbxSequential.move(25,65) 
        self.ckbxSequential.setToolTip("Remove nodes one after each other until none are left")
        self.ckbxSequential.stateChanged.connect(self.ckbxoptionall)
        self.ckbxCascading = QCheckBox("Cascading",self)
        self.ckbxCascading.adjustSize()
        self.ckbxCascading.move(25,85)
        self.ckbxCascading.setToolTip("Remove a node, them all it's neighbours, then all of their neighbours etc,")
        self.ckbxCascading.stateChanged.connect(self.ckbxoptionall)
        GroupAtype = QButtonGroup(self)
        GroupAtype.addButton(self.ckbxSingle)
        GroupAtype.addButton(self.ckbxSequential)
        GroupAtype.addButton(self.ckbxCascading)
        GroupAtype.exclusive()
        
        #set and create GUI features for the node selection method
        lblNSMethod = QLabel("Node selection method",self)
        lblNSMethod.setFont(fontbold)
        lblNSMethod.adjustSize()        
        lblNSMethod.move(130,25)
        self.ckbxRandom = QCheckBox("Random", self)
        self.ckbxRandom.adjustSize()
        self.ckbxRandom.move(130,45)
        self.ckbxRandom.setToolTip("Select the node to remove at random")
        self.ckbxRandom.toggle()
        self.ckbxDegree = QCheckBox("Degree", self)
        self.ckbxDegree.adjustSize()        
        self.ckbxDegree.move(130,65)
        self.ckbxDegree.setToolTip("Select the node with the highest degree")
        self.ckbxBetweenness = QCheckBox("Betweenness", self)
        self.ckbxBetweenness.adjustSize()
        self.ckbxBetweenness.move(130,85) 
        self.ckbxBetweenness.setToolTip(
        "Select the node with the highest betweenness value")
        GroupNSMethod = QButtonGroup(self)     
        GroupNSMethod.addButton(self.ckbxRandom)
        GroupNSMethod.addButton(self.ckbxDegree)
        GroupNSMethod.addButton(self.ckbxBetweenness)
        GroupNSMethod.exclusive()
        #set when initated as not chackable as single is the defualt option
        self.ckbxDegree.setEnabled(False)
        self.ckbxBetweenness.setEnabled(False)
        #set and create GUI features for the network selection type
        self.lblNetType = QLabel("Network Type", self)
        self.lblNetType.setFont(fontbold)
        self.lblNetType.adjustSize()
        self.lblNetType.move(275, 25)
        
        #for network A
        self.graph = 'GNM' #means this is the default, so if menu option not changed/used, will persume GNM graph
        if can_use_db == True:
            inputs = ('Random - GNM', 'Random - Erdos Renyi',
                      'Small-World', 'Scale-free',
                      'Hierarchical Random','Hierarchical Random +',
                      'Hierarchical Communities','Tree','Database',
                      'From CSV','Lists')
        else:
            inputs = ('Random - GNM', 'Random - Erdos Renyi',
                      'Small-World', 'Scale-free',
                      'Hierarchical Random','Hierarchical Random +',
                      'Hierarchical Communities','Tree','From CSV','Lists')
        self.cmboxA = QComboBox(self)
        self.cmboxA.move(275,44)
        self.cmboxA.addItems(inputs)
        self.cmboxA.setToolTip("Select the graph type or graph input method")
        self.cmboxA.activated[str].connect(self.networkselectionA)           
        #set and create GUI features for the input text boxes
        lblGphInputs = QLabel("Graph Inputs", self)
        lblGphInputs.setFont(fontbold)
        lblGphInputs.adjustSize()
        lblGphInputs.move(400, 25)
        self.txtparamA1 = QLineEdit(self)        
        self.txtparamA1.move(400, 45)
        self.txtparamA1.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM        
        self.txtparamA2 = QLineEdit(self)
        self.txtparamA2.move(500, 45)
        self.txtparamA2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtparamA3 = QLineEdit(self)
        self.txtparamA3.move(600, 45)
        self.txtparamA3.setEnabled(False)  
              
        #for network B
        self.graphB = 'None' #means this is the default, so if menu option not changed/used, will persume GNM graph
        if can_use_db == True:        
            inputs = ('None','Random - GNM', 'Random - Erdos Renyi',
                      'Small-World', 'Scale-free',
                      'Hierarchical Random','Hierarchical Random +',
                      'Hierarchical Communities','Tree','Database',
                      'From CSV','Lists')
        else:
            inputs = ('None','Random - GNM', 'Random - Erdos Renyi',
                      'Small-World', 'Scale-free',
                      'Hierarchical Random','Hierarchical Random +',
                      'Hierarchical Communities','Tree',
                      'From CSV','Lists')
            
        self.cmboxB = QComboBox(self)
        self.cmboxB.move(275,90)
        self.cmboxB.addItems(inputs)
        self.cmboxB.setToolTip("Select the graph type or graph input method")
        self.cmboxB.activated[str].connect(self.networkselectionB)
        self.cmboxB.setEnabled(False)
        #set and create GUI features for the input text boxes
        self.txtparamB1 = QLineEdit(self)
        self.txtparamB1.move(400, 90)
        self.txtparamB1.setEnabled(False)
        self.txtparamB1.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM        
        self.txtparamB2 = QLineEdit(self)
        self.txtparamB2.move(500, 90)
        self.txtparamB2.setEnabled(False)
        self.txtparamB2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtparamB3 = QLineEdit(self)
        self.txtparamB3.move(600, 90)
        self.txtparamB3.setEnabled(False)     
        
        #analysis options
        lbltype = QLabel("Analysis Type", self)
        lbltype.setFont(fontbold)
        lbltype.adjustSize()
        lbltype.move(275, 135)
        #self.graph_analysis = 'Single' #means this is the default, so if menu option not changed/used, will persume GNM graph
        inputs = ('Single','Dependency','Interdependency')
        self.cmboxtype = QComboBox(self)
        self.cmboxtype.move(275,155)
        self.cmboxtype.addItems(inputs)
        self.cmboxtype.setToolTip("Select the graph analysis type")
        self.cmboxtype.activated[str].connect(self.selectAnalysisType)
        
        #set and create GUI features for the input text boxes
        lblfromA = QLabel("From A to B", self)
        lblfromA.adjustSize()
        lblfromA.move(400, 135)
        self.txtparamt1 = QLineEdit(self)        
        self.txtparamt1.move(400, 155)
        self.txtparamt1.setEnabled(False)
        self.txtparamt1.setToolTip('List of dependency edges from network A to B') #set the start up states for that top of the list, GNM        
        lblfromB = QLabel("From B to A", self)
        lblfromB.adjustSize()
        lblfromB.move(500, 135)
        self.txtparamt2 = QLineEdit(self)
        self.txtparamt2.move(500, 155)
        self.txtparamt2.setEnabled(False)
        self.txtparamt2.setToolTip('List if dependency edges from network B to A')        
        
        #set and create the extra options features on GUI    
        lblRemoveOptions = QLabel("Remove subgraphs/isolated nodes", self)
        lblRemoveOptions.setFont(fontbold)
        lblRemoveOptions.adjustSize()
        lblRemoveOptions.move(25,105)
        self.ckbxsubgraphs = QCheckBox("Subgraphs", self)  
        self.ckbxsubgraphs.adjustSize()
        self.ckbxsubgraphs.move(25, 120)
        self.ckbxsubgraphs.setToolTip(
        "Select if subgraphs are to be removed when they appear in the network")
        self.ckbxisolates = QCheckBox("Isolates", self)
        self.ckbxisolates.adjustSize()
        self.ckbxisolates.move(130, 120)
        self.ckbxisolates.setToolTip(
        "Select if nodes are to be removed when they become isolated")
        self.ckbxnoisolates = QCheckBox("Exclude isolates", self)
        self.ckbxnoisolates.adjustSize()
        self.ckbxnoisolates.move(130, 140)
        self.ckbxnoisolates.setToolTip("Tick if nodes, one isolated, should not be selected for removal when running resilience analysis")
        self.ckbxisolates.stateChanged.connect(self.limitoptions)
        
        self.ckbxviewnet = QCheckBox("View net failure", self)
        self.ckbxviewnet.adjustSize()
        self.ckbxviewnet.move(130, 175)
        self.ckbxviewnet.setToolTip("View the network failure as nodes are removed")
        
        #set and create button for the GUI
        self.btndraw = QPushButton('Draw', self)
        self.btndraw.move(470, 200)
        self.btndraw.setToolTip('Draw the network')
        self.btndraw.adjustSize()
        self.built = self.btndraw.clicked.connect(self.drawview) #view the network and set built as true 
        self.btnstart = QPushButton('Start', self)
        self.btnstart.setToolTip('Run the analysis')
        self.btnstart.move(630, 200)
        self.btnstart.adjustSize()
        self.btnstart.clicked.connect(self.startorpause)        
        self.btnstep = QPushButton('Step', self)
        self.btnstep.setToolTip('Run the first step of the analysis')
        self.btnstep.move(550, 200)
        self.btnstep.adjustSize()
        self.btnstep.clicked.connect(self.step_analysis)
        self.btnreset = QPushButton('Reset/Cancel', self)
        self.btnreset.setToolTip('Cancel and/or reset the analysis')
        self.btnreset.move(390, 200)
        self.btnreset.adjustSize()
        self.btnreset.clicked.connect(self.reset)        
        btnclear = QPushButton('Clear', self)        
        btnclear.setToolTip('Clear all inputs for networks')
        btnclear.move(310, 200)        
        btnclear.adjustSize()
        btnclear.clicked.connect(self.clearAll)        
        
        self.setGeometry(300,300,720,235)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Network Tool v2.5') #title of window 
        self.setWindowIcon(QIcon('logo.png'))
        self.show() #show window
        #finished signal to follow on from the work thread
        self.connect(self.thread, SIGNAL("finished()"), self.updateUi)
    
    def try_nxpg_import(self):
        try: 
            sys.path.append(self.nxpglocation)
            import nx_pgnet, nx_pg
            self.can_use_db = True
        except:
            self.can_use_db = False    
        
    def calcClustering(self, changedA):
        '''Calculates clustering related values for a network. If no network 
        exists, or the inputs for network A have changed it will build the 
        network itself. Returns the maximum, minimum, avergae and per node 
        values in a message box.'''
        #calc the normal clustering coefficient
        #will return the average value
        #will also return the value per node
        #return other stats
        #send calc to code in another script

        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3, 'A') #builds network
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            maxVal, minVal, averageVal, nodeVal = mc.Clustering_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Clustering Coefficient", 'maximum: \t%s \nminimum: \t%s \naverage: \t%s \nper node: \n%s' %(maxVal, minVal, averageVal, nodeVal), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Clustering Coefficient", 'The graph created had no nodes. No calculations could be performed.')
        return changedA

    def calcAvDegree(self, changedA):
        '''Calcualtes the average degree of a node. If no 
        network exists, or the inputs for network A have changed it will build
        the network itself.'''
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3, 'A') #builds network
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            maxVal, minVal, averageVal, nodeVal = mc.Degree(self.G)
            QMessageBox.information(self, "Computation Results: Average Degree", 'maximum: \t%s \nminimum: \t%s \naverage: \t%s \nper node: \n%s' %(maxVal, minVal, averageVal, nodeVal), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Average Degree", 'The graph created had no nodes. No calculations could be performed.')
        return changedA

    def calcClusteringSq(self, changedA):
        '''Calculates clustering (square) related values for a network. If no 
        network exists, or the inputs for network A have changed it will build
        the network itself. Returns the maximum, minimum, avergae and per node 
        values in a message box.'''
        #calc the square clustering coefficient
        #will return the average value
        #will also return the value per node   
        #return other stats
        #send calc to code in another script
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            maxVal, minVal, averageVal, nodeVal = mc.ClusteringSQ_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Clustering Coefficient (Square)", 'maximum: \t%s \nminimum: \t%s \naverage: \t%s \nper node: \n%s' %(maxVal, minVal, averageVal, nodeVal), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Clustering Coefficient (Square)", 'The graph created had no nodes. No calculations could be performed.')
        return changedA

    def calcAssortativity(self, changedA):
        '''Calculates the assortativity coefficient for a network. If no network 
        exists, or the inputs for network A have changed it will build the 
        network itself. Returns the coefficent value in a message box.'''
        #calc the assortativty coefficient
        #will return the average value
        #will also return the value per node   
        #return other stats
        #send calc to code in another script
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            val  = mc.Assortativity_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Assortativity Coefficient", 'assortativity coefficient: \t%s' %(val), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Assortativity Coefficient", 'The graph created had no nodes. No calculations could be performed.')        
        return changedA
        
    def calcBetweenness(self, changedA):
        '''Calculates betweenness related values for a network. If no network 
        exists, or the inputs for network A have changed it will build the 
        network itself. Returns the maximum, minimum, avergae and per node 
        values in a message box.'''
        #calc the betweenness centrality
        #send calc to code in another script
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return            
        if self.G.number_of_nodes() > 0 and self.G.number_of_nodes() < 100:
            maxVal, minVal, averageVal, nodeVal = mc.Betweenness_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Betweenness Centrality", 'maximum: \t%s \nminimum: \t%s \naverage: \t%s \nper node: \n%s' %(maxVal, minVal, averageVal, nodeVal), QMessageBox.Ok)
        elif self.G.number_of_nodes() >= 100:
            maxVal, minVal, averageVal, nodeVal = mc.Betweenness_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Betweenness Centrality", 'maximum: \t%s \nminimum: \t%s \naverage: \t%s \nper node: \nTo many to show' %(maxVal, minVal, averageVal), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Betweenness Centrality", 'The graph created had no nodes. No calculations could be performed.')        
        return changedA
    
    def calcAvPathLength(self, changedA):
        '''Calculates the average shortest path length and as well as per 
        subgraph for a nework. If no network exists or the input values for 
        network A have changed, the network will be built. The results are 
        presented in a message box.'''
        #calc the average path length
        #send calc to code in another script
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        #here node a way of asking of want to use geo
        if self.G.number_of_nodes > 0:
            if self.graph == 'Database':
                #allows length attribute to be specified
                text, ok = QInputDialog.getText(self, 'Path length option', 
                'If you want to calculate the geographic average \npath length enter the attribute below. \nOtherwise leave blank.')
                if ok:
                    whole_graph, subgraphs = mc.GeoAveragePathLength_Calc(self.G, str(text))
                    QMessageBox.information(self, "Computation Results: Average Georaphic path length", 'Whole graph: \t%s \nPer subgraph: \n%s' %(whole_graph,subgraphs), QMessageBox.Ok)
            else:
                #calc path topological path length
                whole_graph, subgraphs = mc.AveragePathLength_Calc(self.G)
                QMessageBox.information(self, "Computation Results: Average path length", 'Whole graph: \t%s \nPer subgraph: \n%s' %(whole_graph,subgraphs), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Average path length", 'The graph created had no nodes. No calculations could be performed.')
        return changedA
        
    def calcCycleBasis(self, changedA):
        '''Find all the cycle basis in a network. Returns number of cycle basis
        and a list of them in a message box.'''
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return            
        if self.G.number_of_nodes() > 0 and self.G.number_of_nodes() < 100:
            count, basis = mc.CycleBasis_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Cycle Basis", 'Count: \t%s \n%s' %(count, basis), QMessageBox.Ok)
        elif self.G.number_of_nodes() >= 100:
            count, basis = mc.CycleBasis_Calc(self.G)
            QMessageBox.information(self, "Computation Results: Cycle Basis", 'Count: \t%s ' %(count), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Cycle Basis", 'The graph created had no nodes. The count could be performed.')        
        return changedA
        
    def calcDegreeDist(self, changedA):
        '''Generates a degree distribution plot for a network. If no network 
        exisits, or the contents of the input boxes for network A have changed,
        it will try and build the network.'''
        #calc the degree distribution
        #send calc to code in another script
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            degreedist = mc.DegreeDistribution(self.G)
            QMessageBox.information(self, "Computation Results: Degree Distribution", 'Degree distribution: \n%s' %(degreedist), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Degree Distribution", 'The graph created had no nodes. No calculations could be performed.')        
        degs = {}
        for n in self.G.nodes () :
            deg = self.G.degree(n)
            if deg not in degs :
                degs[deg] = 0
            degs[deg] += 1
        
        items = sorted(degs.items())
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.loglog([ k for (k,v) in items] , [v for (k,v) in items])
        plt.xlabel("degree")
        plt.ylabel("frequency")
        plt.show()
        return changedA
        
    def massCalc(self, changedA):
        '''Used to calculate the full range of metrics. Returns the average 
        where multiple values possible via a message window. Results will also
        be written to a text file but this has not been added yet.'''
        #will open a new window where user can select the metrics they want to calculate
        #then calc the metrics
        #create a text file output
        #make a summary window appear
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        if self.G.number_of_nodes > 0:
            maxValCC, minValCC, averageValCC, nodeValCC = mc.Clustering_Calc(self.G)
            maxValCS, minValCS, averageValCS, nodeValCS = mc.ClusteringSQ_Calc(self.G)
            maxValBC, minValBC, averageValBC, nodeValBC = mc.Betweenness_Calc(self.G)
            whole_graph, subgraphs = mc.AveragePathLength_Calc(self.G, changedA)
            val  = mc.Assortativity_Calc(self.G)
            #need code here which writes the full set of results to a textfile
            #will have to open the file dialog 
            QMessageBox.information(self, "Computation Results: Selected metrics", 'Mean clustering coefficient: \t\t%s \nMean clustering coefficient(Sq): \t%s \nMean betweenness coefficient: \t%s \nAssotativity coefficient: \t\t%s \nAverage path length: \t\t%s' %(averageValCC, averageValCS, averageValBC, val, whole_graph), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Computation Results: Selected metrics", 'The graph created had no nodes. No calculations could be performed.')        
        return changedA
        
    def plotGraph(self):
        '''This will allow the user to plot a graph comapring the metrics per 
        node for a network. The details of te functionality and use of this 
        need considering further.'''
        #will allow the user to plot a graph with any of the metrics
        #send calc to code in another script
        QMessageBox.information(self, "Information", 'This has no functionality as yet.')
        return
        
    def export(self, changedA):
        '''This will export some detailed metric results. Export the nodes and 
        edges of the network along with the chosen metrics in one text file.'''
        #QMessageBox.information(self, "Information", 'This has no functionality as yet.')

        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or self.changedA == True:
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G == None: return
        if self.G.number_of_nodes == 0:
            return
            
        fileName = self.setfilelocation_save()
        if fileName == '':
            return

        #if a file name as been provided
        f = open(fileName, 'a')
        f.write('Network overview \n')
        f.write('Network nodes: ' + str(self.G.nodes()) + '\n')
        f.write('Network edges: ' + str(self.G.edges()) + '\n')
        f.write('Number of nodes: ' + str(self.G.number_of_nodes()) + '\n')
        f.write('Number of edges: ' + str(self.G.number_of_edges()) + '\n')
        maxVal, minVal, averageVal, nodeVal = mc.Degree(self.G)
        f.write('Node degree:' + '\n')
        f.write('Maximum: %s, Minimum: %s, Average: %s\n' %(maxVal,minVal,averageVal))
        f.write('Per node: %s\n' %(nodeVal))
        maxVal, minVal, averageVal, nodeVal = mc.Clustering_Calc(self.G)
        f.write('Clustering coefficent:\n')
        f.write('Maximum: %s, Minimum: %s, Average: %s\n' %(maxVal,minVal,averageVal))
        f.write('Per node: %s\n' %(nodeVal))
        maxVal, minVal, averageVal, nodeVal = mc.ClusteringSQ_Calc(self.G)
        f.write('Square clustering coefficent:\n')
        f.write('Maximum: %s, Minimum: %s, Average: %s\n' %(maxVal,minVal,averageVal))
        f.write('Per node: %s\n' %(nodeVal))
        val  = mc.Assortativity_Calc(self.G)
        f.write('Assortativty:\n')
        f.write('Value: %s\n' %(val))
        count, basis = mc.CycleBasis_Calc(self.G)
        f.write('Cycle basis:\n')
        f.write('Count: %s\n' %(count))
        f.write('Listed: %s\n' %(basis))
        text = ''
        whole_graph, subgraphs = mc.AveragePathLength_Calc(self.G, str(text))
        f.write('Average path length:\n')
        f.write('Whole graph: %s\n' %(whole_graph))
        f.write('Per subgraph: %s\n' %(subgraphs))
        f.close()
        QMessageBox.information(self, "Information", 'Successfully saved metric results to text file.')

        return changedA
        
    def saveConfig(self):
        '''Saves a text file which contains the settings used in GUI.'''
        
        import datetime
        #ask the user for a file name and locaiton
        fileName = self.setfilelocation_save()
        #if the given file name is not blank
        if fileName <> '':
            #open the text file a write out some metadata
            f = open(fileName, 'a')
            f.write('Date: ' + str(datetime.datetime.now().date()) + '\n')
            f.write('Time: ' + str(datetime.datetime.now().time()) + '\n')
            #write some of the parameters out            
            f.write('Analysis method: ')
            if self.ckbxSingle.isChecked() == True: f.write('Single == True\n')
            elif self.ckbxSequential.isChecked() == True: f.write('Sequential == True\n')
            elif self.ckbxCascading.isChecked() == True: f.write('Cascading == True\n')
            f.write('Node selection method: ')
            if self.ckbxRandom.isChecked() == True: f.write('Random == True\n')
            elif self.ckbxDegree.isChecked() == True: f.write('Degree == True\n')
            elif self.ckbxBetweenness.isChecked() == True: f.write('Betweenness == True\n')
            f.write('Analysis type:')
            if self.cmboxtype.currentText() == 'Single': f.write('Single == True\n')
            elif self.cmboxtype.currentText() == 'Dependency': f.write('Dependency == True\n')
            elif self.cmboxtype.currentText() == 'Interdependency': f.write('Interdependency == True\n')
            f.write('Optional parameters:\n')
            if self.ckbxsubgraphs.isChecked() == True: f.write('Subgraphs == True\n')
            else: f.write('Subgraphs == False\n')
            if self.ckbxisolates.isChecked() == True: f.write('Isolates == True\n')
            else: f.write('Isolates == False\n')
            if self.ckbxnoisolates.isChecked() == True: f.write('No Isolates == True\n')
            else: f.write('No Isolates == False\n')
            #if the analysis had many iterations
            if self.multiiterations == True:
                f.write('Multiple iterations == True\n')
                f.write('Number of iterations == %s\n' %(self.numofiterations))
            else: f.write('Multiple iterations == False')
            #if images were saved during the failure at set intervals
            if self.saveimage == True:
                f.write('Save Image == True\n')
                f.write('Per time step == %s\n' %(self.pertimestep))
                f.write('Save location == %s\n'%(self.imagedestlocation))
            elif self.saveimage == False:
                f.write('Save Image == False\n')               
            #write the boolean state for all the metrics
            f.write('Metrics:\n')
            a,b,c,d = self.metrics
            f.write('Metrics A1: ' + str(a) + '\n')
            f.write('Metrics B1: ' + str(b) + '\n')
            f.write('Metrics A2: ' + str(c) + '\n')
            f.write('Metrics B2: ' + str(d) + '\n')
            #ask the user if they want to save the networks
            if self.G <> None:
                reply = QMessageBox.question(self, 'Message',
                    "Do you want to save the networks?", QMessageBox.Yes,QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if str(self.G.nodes()) <> '':
                        f.write('Network A is: \n')
                        f.write('Nodes A: ' + str(self.G.nodes())+'\n')
                        f.write('Edges A: ' + str(self.G.edges())+'\n')
                    if str(self.GnetB.nodes()) <> '':
                        f.write('Network B is: \n')
                        f.write('Nodes B: ' + str(self.GnetB.nodes())+'\n')
                        f.write('Edges B: ' + str(self.GnetB.edges())+'\n')
                    if str(self.txtparamt1.text()) <> '':
                        f.write('Dependency Edges are:\n')
                        f.write('A to B edges are: ' + str(self.txtparamt1.text())+'\n')
                    if str(self.txtparamt2.text())<>'':
                        f.write('B to A edges are: ' + str(self.txtparamt2.text())+'\n')
                else:
                    pass
            #inform the user that the save process has been successful
            QMessageBox.question(self, 'Message',
                "Successfully saved file.", QMessageBox.Ok)

            f.close()
        else:
            pass
        return
    
    def openConfig(self):
        '''Function to open a config file and set the specified settings for 
        analysis. Changes all settings it can find which are error free. If 
        there is an error in the config file, it notifies the user at the end 
        once changes are made which can be made. This is still vulnerable to a 
        user modifying the text file in a text editor.'''
        #get the user to select the file to open
        fileName = self.setfilelocation_open()
        #if the file name is not blank
        if fileName <> '':
            #open the file so it can be read
            f = open(fileName, 'r')
           
            self.tempmetrics=[]
            #variables to insure the load is successfull
            done1 = False #failure type - single, sequential, cascading
            done2 = False #node selection - random, degree, betweenness
            done3 = False #analysis type - single, dependency, interdependency
            error1 = True #how to handle subgraphs
            error2 = True #how to handle isolates
            error3 = True #how to handle no isolates
            #loop through all the lines in the text file
            line = f.readlines()
            for item in line:
                #if the line starts wit the text, process as appropriate
                if item.startswith('Analysis method'):
                    a,b = item.split(':')
                    b = b.strip()
                    if b.startswith('Single'): 
                        #set the checkboxes on the interface accordingly
                        self.ckbxSequential.setChecked(False)
                        self.ckbxCascading.setChecked(False)
                        self.ckbxSingle.setChecked(True)
                        self.ckbxoptionlimited()
                        #change this to true to clarify this has been completed
                        done1 = True
                    elif b.startswith('Sequential'):
                        self.ckbxSingle.setChecked(False)
                        self.ckbxCascading.setChecked(False)
                        self.ckbxSequential.setChecked(True)
                        self.ckbxoptionall()
                        done1 = True
                    elif b.startswith('Cascading'):
                        self.ckbxSingle.setChecked(False)
                        self.ckbxSequential.setChecked(False)
                        self.ckbxCascading.setChecked(True)
                        self.ckbxoptionall()
                        done1 = True
                elif item.startswith('Node selection'):
                    a,b = item.split(':')
                    b = b.strip()
                    if b.startswith('Random'):
                        self.ckbxRandom.setChecked(True)
                        done2 = True
                    elif b.startswith('Degree'):
                        self.ckbxDegree.setChecked(True)
                        done2 = True
                    elif b.startswith('Betweenness'):
                        self.ckbxBetweenness.setChecked(True)
                        done2 = True
                elif item.startswith('Analysis type'):
                    a,b = item.split(':')
                    b = b.strip()
                    if b.startswith('Single'):
                        self.cmboxtype.setCurrentIndex(0)
                        self.cmboxB.setCurrentIndex(0)                    
                        self.cmboxB.setEnabled(False)
                        self.ckbxviewnet.setEnabled(True )
                        done3 = True
                    elif b.startswith('Dependency'):
                        self.cmboxtype.setCurrentIndex(1)
                        self.cmboxB.setCurrentIndex(1)
                        self.cmboxB.setEnabled(True)
                        self.networkselectionB(self.cmboxB.currentText())
                        self.ckbxviewnet.setEnabled(False)
                        done3 = True
                    elif b.startswith('Interdependency'):
                        self.cmboxtype.setCurrentIndex(2)
                        self.cmboxB.setCurrentIndex(1)
                        self.cmboxB.setEnabled(True)
                        self.networkselectionB(self.cmboxB.currentText())
                        self.ckbxviewnet.setEnabled(False)
                        done3 = True
                        
                if item.startswith('Subgraphs == T'):
                    self.ckbxsubgraphs.setChecked(True)
                    error1 = False
                elif item.startswith('Subgraphs == F'):
                    self.ckbxsubgraphs.setChecked(False)
                    error1 = False
                if item.startswith('Isolates == T'):
                    self.ckbxisolates.setChecked(True)
                    error2 = False
                elif item.startswith('Isolates == F'):
                    self.ckbxisolates.setChecked(False)
                    error2 = False
                if item.startswith('No Isolates == T'):
                    self.ckbxnoisolates.setChecked(True)
                    error3 = False
                elif item.startswith('No Isolates == F'):
                    self.ckbxnoisolates.setChecked(False)
                    error3 = False
                    
                if item.startswith('Multiple iterations == True'):
                    self.multiiterations = True
                elif item.startswith('Multiple iterations == False'):
                    self.multiiterations = False
                if item.startswith('Number of iterations'):
                    a,b = item.split('==')
                    self.numofiterations = int(b.strip())
                    
                if item.startswith('Save Image == True'):
                    self.saveimage = True
                elif item.startswith('Save Image == False'):
                    self.saveimage = False
                if item.startswith('Per time step'):
                    a,b = item.split('==')
                    self.pertimestep = int(b.strip())
                    
                if item.startswith('Save location'):
                    a,b = item.split('==')
                    self.imagedestlocation=b.strip()
                                                            
                #if the line is to do with the metrics
                if item.startswith('Metrics A1:'):
                    #edit the list so it is only comma separated
                    a,b = item.split(':')
                    b = b.strip()
                    b = b.replace('(','')
                    b = b.replace(')','')
                    b = b.split(',')
                    temp = []
                    #loop through the list
                    for items in b:
                        items = items.strip()
                        if items == 'True': temp.append(True)
                        elif items == 'False': temp.append(False)
                    #add to the global list
                    self.tempmetrics.append(temp)
                if item.startswith('Metrics B1:'):
                    a,b = item.split(':')
                    b = b.strip()
                    b = b.replace('(','')
                    b = b.replace(')','')
                    b = b.split(',')
                    temp = []
                    if str(b) == "['None']": self.tempmetrics.append(None)
                    else:
                        for items in b:
                            items = items.strip()
                            if items == 'True': temp.append(True)
                            elif items == 'False': temp.append(False)
                        self.tempmetrics.append(temp)    
                if item.startswith('Metrics A2:'):
                    a,b = item.split(':')
                    b = b.strip()
                    b = b.replace('(','')
                    b = b.replace(')','')
                    b = b.split(',')
                    if b == 'None': self.metrics.append('None')
                    else:
                        temp = []
                        for items in b:
                            items = items.strip()
                            if items == 'True': temp.append(True)
                            elif items == 'False': temp.append(False)
                        self.tempmetrics.append(temp)
                if item.startswith('Metrics B2:'):
                    a,b = item.split(':'); b = b.strip()
                    b = b.replace('(',''); b = b.replace(')','')
                    b = b.split(',')
                    if str(b) == "['None']": self.tempmetrics.append(None)
                    else:
                        temp = []
                        for items in b:
                            items = items.strip()
                            if items == 'True': temp.append(True)
                            elif items == 'False': temp.append(False)
                        self.tempmetrics.append(temp)
                    
                if item.startswith('Nodes A: '):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamA1.setText(b)
                    self.cmboxA.setCurrentIndex(10)
                    self.graph=('Lists')
                if item.startswith('Edges A: '):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamA2.setText(b)
                if item.startswith('Nodes B: '):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamB1.setText(b)
                    self.cmboxB.setCurrentIndex(11)
                if item.startswith('Edges B: '):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamB2.setText(b)
                if item.startswith('A to B edges are:'):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamt1.setText(b)
                if item.startswith('B to A edges are:'):
                    a,b = item.split(':')
                    b = b.strip()
                    self.txtparamt2.setText(b)
                    
            #error checking for those which have been loaded
            # will not check the network nodes and edges, leave that to 
            #    the code in the gui to build the networks
            FAIL = 0
            #if this has not changed sine being created
            if done1 == False:
                FAIL += 1
                #show a error message to the user
                QMessageBox.question(self, 'Message',
                    "Error when loading 'Analysis Method' parameter.", QMessageBox.Ok)
            if done2 == False:
                FAIL += 1
                QMessageBox.question(self, 'Message',
                    "Error when loading 'Node Selection' parameter.", QMessageBox.Ok)
            if done3 == False:
                FAIL += 1
                QMessageBox.question(self, 'Message',
                    "Error when loading 'Analysis type' parameter.", QMessageBox.Ok)
            
            #error checking for the parameters
            if error1 == True or error2 == True or error3 == True:
                FAIL += 1
                QMessageBox.question(self, 'Message',
                    "Error when loading parameters. There were %s error(s)." %(FAIL), QMessageBox.Ok)
            
            #error checking for the loading of the metrics - the length for 
            #each of them is known thus if different, must be an error
            OK = True
            if len(self.tempmetrics[0]) <> 5: OK = False; FAIL += 1
            if self.tempmetrics[1] == None: pass
            elif len(self.tempmetrics[1]) == 5: pass
            else: OK = False; FAIL += 1
            if len(self.tempmetrics[2]) <> 14: OK = False; FAIL += 1
            if self.tempmetrics[3] == None: pass
            elif len(self.tempmetrics[3])<> 14: pass
            else: OK = False; FAIL += 1
            #give user a error message if metrics have not loaded correctly
            if OK == False:                
                 QMessageBox.question(self, 'Message',
                    "Error loading in metrics." , QMessageBox.Ok)
            #if there have been no issues, informt the user
            if FAIL == 0:
                self.metrics = self.tempmetrics
                QMessageBox.question(self, 'Message',
                    "Successfully loaded file.", QMessageBox.Ok)
            #if there have been issues, inform the user
            elif FAIL > 0:
                QMessageBox.question(self, 'Message',
                    "Error when loading file. Error in loading the status of \nthe metrics. There was %s error(s)." %(FAIL), QMessageBox.Ok)
            #clsoe the reader
            f.close()
        else:
            pass
        return
        
    def AtoBEdges(self, changedA=False, changedB=False):
        '''Function to check the contents of the input dependency edges box, 
        and randomly create a set of edges which conenct network B 
        to A if there are none entered. Otherwise will read these in. 
        Parameters for networks must be entered already and user is 
        required to set how many edges they want. Can be called from the 
        Failure options menu or will run if no edges have been entered when 
        they are needed to.'''
        #need to build the networks
        #ask user how mant edges they want to add
        #need to check that the analysis is not stand alone - safety check        
        #build network A if required
        if self.analysistype == 'Single':
            QMessageBox.warning(self, 'Error!', "This function is not required for analysing a single network.",'&OK')            
            return
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == False:
            self.G = self.buildnetwork(param1,param2,param3, 'A') #builds network
            if self.G == None: return
            
        #build network B if required
        param1 = self.txtparamB1.text()
        param2 = self.txtparamB2.text()
        param3 = self.txtparamB3.text()  
        changedB = self.check_for_changes(param1,param2,param3,'B')
        if self.GnetB == None or changedB == False:
            self.GnetB = self.buildnetwork(param1,param2,param3, 'B') #builds network
            if self.GnetB == None: return 
        
        dependencyEdges = []
        if str(self.txtparamt1.text()) <> '': #reads text in text box
            #may also one some code to overwrite these with random one if chosen  
            line = self.txtparamt1.text()                     
            line = replace_all(line, {')':'' , ']':'' , '[':'' , ' ':''}) #clean the list
            line = line.split(',')
            i = 0            
            while i <len(line):
                temp=[]
                temp.append(int(line[i]))
                temp.append(int(line[i+1]))
                dependencyEdges.append(temp)
                i += 2
                      
        else: #randomly creates dependency edges
            #get the number of edges wanted from the input dialog
            numberOfEdgesToCreate = self.EdgesDialog(self.G.number_of_nodes(),self.GnetB.number_of_nodes())   
            if numberOfEdgesToCreate == 0 or numberOfEdgesToCreate == False:
                return
                
            #generate node pairs
            ANodes = self.G.nodes()
            BNodes = self.GnetB.nodes()
             
            edges = 0                
            while edges < numberOfEdgesToCreate:
                edges += 1
                temp = []
                temp.append(r.choice(ANodes))
                temp.append(r.choice(BNodes))
                dependencyEdges.append(temp)
            #QMessageBox.information(self, 'Information', "The dependency edges have been created.\n %s"%(str(dependencyEdges))+self.NETNAME,'&OK')            
            self.txtparamt1.setText(str(dependencyEdges))
        return  dependencyEdges, changedA,changedB

    def BtoAEdges(self, changedA, changedB):
        '''Function to randomly create a set of edges which conenct network A 
        to B. Parameters for networks muf.write('Dependency Edges are:\n')st be entered already and user is 
        required to set how many edges they want. Can be called from the 
        Failure options menu or will run if no edges have been entered when 
        they are needed to.'''
        #need to build the networks
        #ask user how mant edges they want to add
        if self.analysistype == 'Single' or self.analysistype == 'Dependency':
            QMessageBox.warning(self, 'Error!', "This function is only required when analysing an inerdependent system, not for the analysis of a single network or a system with dependency."+self.NETNAME,'&OK')      
            return
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()        
        changedA = self.check_for_changes(param1,param2,param3,'A')
        if self.G == None or changedA == False:
            self.G = self.buildnetwork(param1,param2,param3, 'A') #builds network
            if self.G == None: return
            
        #build network B if required
        param1 = self.txtparamB1.text()
        param2 = self.txtparamB2.text()
        param3 = self.txtparamB3.text()  
        changedB = self.check_for_changes(param1,param2,param3,'B')
        if self.GnetB == None or changedB == False:
            self.GnetB = self.buildnetwork(param1,param2,param3, 'B') #builds network
            if self.GnetB == None: return 
        
        #this needs change to an input message for the window
        numberOfEdgesToCreate = self.EdgesDialog(self.G.number_of_nodes(),self.GnetB.number_of_nodes())   
        if numberOfEdgesToCreate == 0:
            return        
        numberOfEdgesToCreate = 5

        #generate node pairs
        ANodes = self.G.nodes()
        BNodes = self.GnetB.nodes()
        dependencyEdges = [] 
        edges = 0                
        while edges < numberOfEdgesToCreate:
            edges += 1
            temp = []
            temp.append(r.choice(ANodes))
            temp.append(r.choice(BNodes))
            dependencyEdges.append(temp)
        QMessageBox.information(self, 'Information', "The dependency edges have been created.\n %s"%(dependencyEdges)+self.NETNAME,'&OK')            
        self.txtparamt2.setText(str(dependencyEdges))
        return dependencyEdges, changedA, changedB
        
    def EdgesDialog(self,sizeA,sizeB):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 
            'Enter the number of dependency edges wanted.\nNetwork A has %s nodes.\nNetwork B has %s nodes.'%(sizeA,sizeB))
                    
        if ok:
            #need some more error checking in here so only integers can be added
            try:            
                text = int(text)
                return text
            except:
                print  'Error! Incorrect value entered. It must be an integer.'
        else:
            return False     

    def startorpause(self):
        ''''''
        if self.running == True:
            self.pause = True
        elif self.running == False:
            self.running = True
            self.pause= False            
            self.full_analysis()

    def selectAnalysisType(self, text):
        '''Change which input text boxes are activiated based on the selection 
        of the anlysis type.'''
        self.analysistype = text
        if self.analysistype == 'Single':
            self.txtparamt1.setEnabled(False)
            self.txtparamt2.setEnabled(False)
            self.txtparamB1.setEnabled(False)
            self.txtparamB2.setEnabled(False)
            self.txtparamB3.setEnabled(False)
            self.ckbxviewnet.setEnabled(True)
            self.cmboxB.setCurrentIndex(0)
            self.cmboxB.setEnabled(False)
        elif self.analysistype == 'Dependency':
            self.txtparamt1.setEnabled(True)
            self.txtparamt2.setEnabled(False)
            self.cmboxB.setCurrentIndex(1)
            self.cmboxB.setEnabled(True)
            self.networkselectionB('GNM')
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.ckbxviewnet.setEnabled(False)
        elif self.analysistype == 'Interdependency':
            self.txtparamt1.setEnabled(True)
            self.txtparamt2.setEnabled(True)
            self.cmboxB.setCurrentIndex(2)
            self.cmboxB.setEnabled(True)
            self.networkselectionB('GNM')
            self.ckbxviewnet.setEnabled(False)
            
    def limitoptions(self):
        '''Change the state of the option checkboxes when the isolates check 
        box is selected.'''
        if self.ckbxisolates.isChecked():
            self.ckbxnoisolates.setEnabled(False)
            self.ckbxnoisolates.setChecked(True)
        else:
            self.ckbxnoisolates.setEnabled(True)
            self.ckbxnoisolates.setChecked(False)
            
    def ckbxoptionlimited(self):
        '''Change the enabled checkboxes for node slection when single analysis
        is selected and check the only valid option.'''
        self.ckbxDegree.setEnabled(False)
        self.ckbxBetweenness.setEnabled(False)
        self.ckbxDegree.setChecked(False)
        self.ckbxBetweenness.setChecked(False)
        self.ckbxRandom.setChecked(True)
        QApplication.processEvents() #refresh gui

    def ckbxoptionall(self):
        '''Set all the node selection check boxes as checkable again.'''
        self.ckbxDegree.setEnabled(True)
        self.ckbxBetweenness.setEnabled(True)

    def disableallckbx(self):
        '''Used to disable all the checkboxes when resileince analysis is being 
        run. Called by the full_analysis function.'''
        self.ckbxSingle.setEnabled(False)
        self.ckbxSequential.setEnabled(False)
        self.ckbxCascading.setEnabled(False)
        self.ckbxRandom.setEnabled(False)
        self.ckbxDegree.setEnabled(False)
        self.ckbxBetweenness.setEnabled(False)
        self.ckbxisolates.setEnabled(False)
        self.ckbxnoisolates.setEnabled(False)
        self.ckbxsubgraphs.setEnabled(False)

    def enableallckbx(self):
        '''Used by the reset function to enable all the checkboxes which need 
        are required in the default setup.'''
        self.ckbxSingle.setEnabled(True)
        self.ckbxSequential.setEnabled(True)
        self.ckbxCascading.setEnabled(True)
        self.ckbxRandom.setEnabled(True)
        if self.ckbxSingle.isChecked():
            pass
        else:
            self.ckbxDegree.setEnabled(True)
            self.ckbxBetweenness.setEnabled(True)
        self.ckbxisolates.setEnabled(True)
        if self.ckbxisolates.isChecked():
            pass
        else:
            self.ckbxnoisolates.setEnabled(True)
        self.ckbxsubgraphs.setEnabled(True)

    def openfileA(self):
         '''Function for opening a text file and adding the node and edge lists 
         to the input boxes for network A.'''
         #load in a csv, add lists to text boxes, then select lists for the input 
         fname = QFileDialog.getOpenFileName(self, 'Open file')
         if fname == '':
             return
         text = 'Lists'
         self.networkselectionA(text)
         text=open(fname).read()
         text1, text2 = text.split('\n')
         self.txtparamA1.setText(text1)
         self.txtparamA2.setText(text2)
         self.cmboxA.setCurrentIndex(9)
    
    def openfileB(self):
         '''Function for opening a text file and adding the node and edge lists
         to the input boxes for network B.'''
         #load in a csv, add lists to text boxes, then select lists for the input 
         fname = QFileDialog.getOpenFileName(self, 'Open file')
         if fname == '':
             return
         text = 'Lists'
         self.networkselectionB(text)
         text=open(fname).read()
         text1, text2 = text.split('\n')
         self.txtparamB1.setText(text1)
         self.txtparamB2.setText(text2)
         self.cmboxB.setCurrentIndex(9)
    def reset_analysiscompleted(self):
        ''''''
        self.cancel = False
        self.timestep = -1
        self.figureModel = None
        self.fullanalysis = False
        self.lbl4.setText('Ready')
        self.lbl4.adjustSize()
        self.btnstart.setText("Start")       
        self.running = False
        self.pause = False
        self.parameters = None
        self.graphparameters = None
        self.enableallckbx()
        self.btndraw.setEnabled(True) #draw button
        self.btnstep.setEnabled(True) #allow the button to be pressed again
        self.btnstart.setEnabled(True)
        self.ckbxviewnet.setEnabled(True) #view graph checkbox  
        
        '''
        self.parameters = None
        self.running = False
        self.pause = False
        self.changedA = True
        self.changedB = True
        self.lastparam1A = None;self.lastparam2A = None;self.lastparam3A = None
        self.lastparam1B = None;self.lastparam2B = None;self.lastparam3B = None
        self.first = True
        self.figureModel = None
        self.iterate = True
        self.timestep = -1
        self.cancel = False
        self.positions = None
        self.G = None; self.GnetB = None
        self.masterAnet = None; self.masterBnet = None
        self.graphvis = None
        self.analysistype = 'Single'
        self.fullanalysis = False
        self.active = 1
        self.inactive = 0
        self.timedelay = 2
        self.coloractive = 'green'
        self.colorinactive = 'red'
        self.imagedestlocation = ''
        self.pertimestep = 1
        self.whenToSave = []
        self.saveimage = False
        self.multiiterations = False
        self.numofiterations = 1 
        self.iterationsdone = 0
        self.saveoutputfile = True
        '''
    def reset(self):
        '''Reset all the appropriate variables, enable/disable the appropriate 
        buttons and check boxes and reset any text.'''
        
        #self.G = None
        #self.GnetB = None
        #self.cmboxA.setCurrentIndex(0)
        #self.networkselectionA('GNM') #this clears the text boxes - dont really want it too though
        #self.cmboxB.setCurrentIndex(0)
        #self.networkselectionB('None') #this clears the text boxes - dont really want it too though
        #self.cmboxtype.setCurrentIndex(0)        
        #self.txtparamt1.setEnabled(False)
        #self.txtparamt2.setEnabled(False)
        #self.positions = None
        self.cancel = False
        self.timestep = -1
        self.graphvis = None
        #self.figureModel = None
        self.iterate = True
        self.fullanalysis = False
        self.lbl4.setText('Ready')
        self.lbl4.adjustSize()
        self.btnstart.setText("Start")       
        self.running = False
        self.pause = False
        self.parameters = None
        self.graphparameters = None
        self.enableallckbx()
        self.btndraw.setEnabled(True) #draw button
        self.btnstep.setEnabled(True) #allow the button to be pressed again
        self.btnstart.setEnabled(True)
        self.ckbxviewnet.setEnabled(True) #view graph checkbox  
        self.clearDependencyEdges()
        self.whenToSave = []
        self.write_step_to_db = False
        self.write_results_table = False
        self.store_n_e_atts = False
        #self.clearAll()
        self.graph = 'GNM'
        #pl.close()
        
        self.changedA = True
        self.changedB = True
        #self.lastparam1A = None;self.lastparam2A = None;self.lastparam3A = None
        #self.lastparam1B = None;self.lastparam2B = None;self.lastparam3B = None
        #self.first = True

        #self.active = 1
        #self.inactive = 0
        #self.timedelay = 2
        #self.coloractive = 'green'
        #self.colorinactive = 'red'
        #self.imagedestlocation = ''
        #self.pertimestep = 1
        self.metrics = self.sort_metrics()           
        
        print 'GUI reset'
        
        
    def clearAll(self):
        '''Clear all the QLinEdit/input text boxes for both networks A and B. 
        Uses the individual functions for A and B.'''
        self.clearA()
        self.clearB()
        self.clearDependencyEdges()

    def clearA(self):
        '''Clear the three QLinEdit/input text boxes for the first network(A).'''
        self.txtparamA1.setText('')
        self.txtparamA2.setText('')
        self.txtparamA3.setText('')

    def clearB(self):
        '''Clear the three QLinEdit/input text boxes for the second network(B).'''
        self.txtparamB1.setText('')
        self.txtparamB2.setText('')
        self.txtparamB3.setText('')
  
    def clearDependencyEdges(self):
        '''Clear the dependency edges boxes.'''
        self.txtparamt1.setText('')
        self.txtparamt2.setText('')
    
    def closeall(self):
        '''Closes the other windows if they are open when Exit chosen from 
        File menu.'''
        pl.close('all') #closes the network visualisation window

    def check_for_changes(self,param1,param2,param3,text):
        '''Checks to see if any of the inputs for a graph have changed. 
        Does not check the network type or the analysis type.'''
          
        #checks for changes in the three inputs
        if text == 'A':
            self.changedA = False
            if param1 <> self.lastparam1A:
                self.changedA = True
            if param2 <> self.lastparam2A: 
                self.changedA = True
            if param3 <> self.lastparam3A:
                self.changedA = True
            return self.changedA
        elif text == 'B':
            self.changedB = False
            if param1 <> self.lastparam1B:
                self.changedB = True
            if param2 <> self.lastparam2B: 
                self.changedB = True
            if param3 <> self.lastparam3B:
                self.changedB = True
            return self.changedB
        else:
            print 'ERROR, text given did not match as required'
            exit()
        return      
    
    #functions for failure options window
    def show_fail_option_window(self):
        '''Opens the failure options window.'''
        self.w = FailureOptionWindow()
    def updatefoptions(self):
        '''Called by the fail options window to get the state of teh variables.'''
        return self.write_step_to_db,self.write_results_table,self.store_n_e_atts
    def updateGUI_foptions(self,write_step_to_db,write_results_table,store_n_e_atts):
        '''Called when failure options window is closed via apply button so updates the parameters.'''
        self.write_step_to_db = write_step_to_db
        self.write_results_table = write_results_table
        self.store_n_e_atts = store_n_e_atts 
        
    #functions for metrics window
    def showwindow_metrics(self):
        '''Open the metrics window.'''
        self.w = MetricsWindow()
    def updatewindow_metrics(self):
        '''Called by the metrics window when opened to get the up-to-date variables'''
        return self.metrics 
    def updateGUI_metrics(self, metrics):
        '''Called when metrics window is closed to update the variables'''
        self.metrics = metrics
        self.basic_metrics_A, self.basic_metrics_B, self.option_metrics_A, self.option_metrics_B = self.metrics
    
    #functions for options window
    def showwindow_options(self):
        '''Open the extra parameter window.'''
        self.w = OptionsWindow()
        self.w.updatetimedelay(self.timedelay)
    
    def updatewindow_options(self):
        '''Called by the options window to get recent variable values when 
        opened. Returns the options as they have been stored for the option 
        parameter window.'''
        self.oldnxpglocation = self.nxpglocation
        return self.timedelay, self.coloractive, self.colorinactive, self.imagedestlocation,self.pertimestep,self.saveimage,self.analysistype,self.multiiterations, self.numofiterations, self.saveoutputfile, self.imagedpi, self.nxpglocation,self.runallseqmodels,self.nodesizingmeth,self.edgesizingmeth
    
    def updateGUI_options(self,destlocation,pertimesteps,saveimage,multiiterations,numofiterations,colactive,colinactive,timedelay,saveoutputfile,imagedpi,nxpglocation,runallseqmodels,nodesizingmeth,edgesizingmeth):
        '''Updates the state of the variables altered in the options window 
        when it is closed.'''
        self.imagedestlocation = destlocation
        self.pertimesteps = pertimesteps
        self.saveimage = saveimage
        self.multiiterations = multiiterations
        if self.multiiterations == True:
            self.ckbxviewnet.setEnabled(False) #this is undone in the UpdateUI function
        self.numofiterations = numofiterations
        self.colactive = colactive
        self.colinactive = colinactive
        self.timedelay = timedelay
        self.saveoutputfile = saveoutputfile
        self.imagedpi = imagedpi
        self.nxpglocation = nxpglocation
        if self.nxpglocation <> self.oldnxpglocation:
            self.try_nxpg_import() 
        self.oldnxpglocation = None
        self.runallseqmodels = runallseqmodels
        if self.runallseqmodels == True:
            self.ckbxSingle.setEnabled(False)
            self.ckbxSequential.setChecked(True)
            self.ckbxSequential.setEnabled(False)
            self.ckbxCascading.setEnabled(False)
            self.ckbxRandom.setEnabled(False)
            self.ckbxDegree.setEnabled(False)
            self.ckbxBetweenness.setEnabled(False)
        self.nodesizingmeth = nodesizingmeth
        self.edgesizingmeth = edgesizingmeth
    
    #functions for db connect window  
    
    def showwindow_db(self):
        '''Opens the GUI for the user to input the database connection 
        parameters. Also gets the successful working parameters.'''
        dlg = DbConnect()
        if dlg.exec_():
            dlg.getval()
        else:
            pass                       
                
    def updateGUI_db(self, dbconnect, G):
        '''Updates the stored database connection properties if the connection
        was successful when the databse options window closes. Called when 
        DbConnect is closed.'''
        self.dbconnect = dbconnect
        self.G = G
        
    def updatedb_db(self):
        '''Send the saved database connection parameters. Called when the 
        database connection window opens.'''
        return self.dbconnect
    
    def getdbnetwork(self, AorB):
        '''Coordiantes the oppening of the DbConnect input dialog and then the 
        populating of the text boxes in the main GUI.'''
        print 'getdbnetwork function'
        self.showwindow_db()
        if self.G == None:
            pass
        else:
            if AorB == 'A':
                self.txtparamA1.setText(str(self.G.nodes()))
                self.txtparamA2.setText(str(self.G.edges()))
                egl = self.G.edges()            
                nodelist = self.G.nodes()
                a = nodelist[0]
                i = a
                attributed = 0
                
                while attributed < self.G.number_of_edges():
                    a,b = egl[i]
                    atts = self.G.edge[i+1]
                    attkeys = atts.keys()
                    for key in attkeys:
                        if key <> 'length':
                            a = atts[key]['Node_F_ID']
                            b = atts[key]['Node_T_ID']
                            count = 0
                            while count < len(egl):
                                c,d = egl[count]
                                if a==c and b==d or a==d and b==c:
                                    self.G.edge[a][b]['length'] = float(atts[key]['length'])                                    
                                    count = len(egl)+100
                                    attributed +=1
                                else:
                                    count +=1
                    i += 1
            elif AorB == 'B':
                self.txtparamB1.setText(str(self.G.nodes()))
                self.txtparamB2.setText(str(self.G.edges()))
            else:
                QMessageBox.warning(self, 'Error!', "Internal error. Please close the application and re-open it. If this error continue to occur, please report it.",'&OK')
    
    #functions for view graphs window
    def updatewindow_viewgraphs(self):
        '''Used to transfer the values to the view graphs class. Called on
        first line of class.'''
        print '--------------------------'
        print self.parameters
        return self.values, self.parameters[0]
        
    def closeEvent(self, event):
        '''Over rides the automatic close event so can ask user if they 
        want to quit.'''
        reply = QMessageBox.question(self, 'Message',"Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes: #if the user clicks yes
            event.accept()
            self.cancel = True
            self.closeall()
        else: #if the user clicks no
            event.ignore()
            
    def updateUi(self):
        '''Called by the finished() signal, thus process the results, handles 
        the visualisations and the completion of the analysis as well as the 
        continument of the full analysis if applicable.'''
        #print 'THE THREAD HAS FINSIHED, NUMBER OF SIMULATIONS COMPLETE IS: ', self.iterationsdone
        if self.iterationsdone > self.numofiterations+1:
            print 'ERROR - more simulations done than required. (Source-updateUi)'
            exit()
               
        #update variables
        if self.timestep>0:
            forthread = self.thread.update()
            if forthread == 0001:
                QMessageBox.warning(self, 'Error!', "Error 0001. Could not remove chosen node from a network.",'&OK')
                print 'GOING TO EXIT NOW'
                exit()
            elif forthread == None:
                QMessageBox.warning(self, 'Error!', "Error.",'&OK')
            else:
                self.graphparameters, self.parameters, self.metrics, self.iterate = forthread
        else:
            self.graphparameters, self.parameters, self.metrics, self.iterate = self.forthread
        
        networks,i,node_list, to_b_nodes, from_a_nodes = self.graphparameters
        #networks,i,node_list, to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = self.graphparameters
        GtempA, GtempB, GA, GB = networks
        self.G = GtempA  
        
        #if image visualisation has been asked for
        if self.ckbxviewnet.isChecked() or self.saveimage == True:
            if self.ckbxviewnet.isChecked() == True: show = True
            else: show = False
            
            self.lbl4.setText('Drawing')
            self.lbl4.adjustSize()
            QApplication.processEvents()

            if self.timestep > -1:
                print 'the time step is: ', self.timestep
                #identify removed nodes and set as inactive
                if self.ckbxSingle.isChecked():

                    '-----------------------------------'
                    #need something here which deals with the geographic 
                    #    network and altering states of its nodes AND EDGES
                    for node in self.graphvis:
                        self.graphvis.node[node]['state'] = self.active #set all nodes as active
                    removednodes = set(self.graphvis.nodes()) - set(GA.nodes()) #need to convert to sets as lists cannot be subtracted
                    for node in removednodes:
                        self.graphvis.node[node]['state'] = self.inactive #set the removed node(s) as inactive
                    if self.geo_vis <> None:
                        for node in self.geo_vis:
                            #need think how this can be done
                            #hopefully the nodes match up, and then can go from there
                            #if they do - if the node is inactive, use the line 
                            #strings associated with it to mark the relevant edges asinactive
                            #need code elsewhere to mark all edges as active (along with their nodes??).
                            #first need to clean code up massively to make this much easier.
                            pass
                    '----------------------------------'
                     
                else:
                    removednodes = set(self.graphvis.nodes()) - set(GA.nodes()) #need to convert to sets as lists cannot be subtracted
                    for node in removednodes: #set the state to inactive for relavant nodes 
                        self.graphvis.node[node]['state'] = self.inactive
                #get node size
                self.graphvis = self.get_node_size_metric(GA, self.graphvis, self.nodesizingmeth)   
                
                print '--------------------------'
                #print self.selected_vis
                print '--------------------------'
                if self.multiiterations == True:
                    print 'SAVEING IMAGE FOR ITERATION'
                    self.imagedestlocation_withsim = self.imagedestlocation + '_sim' + str(self.iterationsdone+1)
                    #print  'NAME IS: ', self.imagedestlocation_withsim
                    #print 'when to save is: ', self.whenToSave
                    self.figureModel, self.timestep, self.whenToSave = draw(self.graphvis, self.positions, self.figureModel, self.timestep, self.coloractive, self.colorinactive, show, self.pertimestep, self.imagedestlocation_withsim, self.whenToSave, self.selected_vis, self.geo_vis)
                else:
                    print 'THIS IS THE CALL WHERE THE ERROR OCCURS'
                    print self.geo_vis
                    #exit()
                    self.figureModel, self.timestep, self.whenToSave = draw(self.graphvis, self.positions, self.figureModel, self.timestep, self.coloractive, self.colorinactive, show, self.pertimestep, self.imagedestlocation, self.whenToSave, self.selected_vis, self.geo_vis)
                    
                if self.fullanalysis == True:
                    QApplication.processEvents() #refresh gui
                    time.sleep(self.timedelay)
            else:
                #if not method is selected
                self.reset()
                self.lbl4.setText('Canceled - Now ready')
                self.lbl4.adjustSize()
    
        if self.iterate==False:
            self.iterationsdone+=1
        
        print '-------------------------------'
        print '%s/%s simulations done.' %(self.iterationsdone,self.numofiterations)
        #for the continued analysis of a network
        if self.fullanalysis == True and self.iterate==True and self.cancel==False:
            self.full_analysis(self.parameters)                      
        #for the end of a single iteration network analysis
        elif self.iterate==False and self.multiiterations == False:
            self.lbl4.setText('Analysis completed')
            self.lbl4.adjustSize()
            QApplication.processEvents() #refresh gui            
            ok = QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed. Do you want to view the metric graphs?" , '&No','&View Graphs')
            if ok == 1: #if the view graph option is clicked
                print 'when sending, self.metrics is:', self.metrics 
                self.values = res.outputresults(self.graphparameters, self.parameters, self.metrics)
                pl.close()
                self.q = ViewGraphs()
                self.btnstep.setEnabled(True) #allow the button to be pressed again
                self.btndraw.setEnabled(True) 
                self.iterationsdone = 0
                self.reset()
            else:
                pl.close()
                self.reset()    
               
        #for the end of an iteration of a multiple simulation analysis
        elif int(self.iterationsdone) <> int(self.numofiterations) and self.iterate == False and self.multiiterations == True:
            
            print '------------------------------------'
            self.lbl4.setText('Progress: %s/%s' %(str(self.iterationsdone),str(self.numofiterations)))
            #saves the results from the last simulation
            if self.saveoutputfile == True:
                
                if self.runallseqmodels == False:
                    self.values = res.outputresults(self.graphparameters, self.parameters)
                else:
                    '''
                    need some code here to customise the file path to add the method when using all three
                    '''
                    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = self.parameters
                    if RANDOM == True:
                        fileName = fileName+'_RANDOM'
                    elif DEGREE == True:
                        fileName = fileName+'_DEGREE'
                    elif BETWEENESS == True:
                        fileName = fileName+'_BETWEENNESS'
                    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges
                    self.values = res.outputresults(self.graphparameters, parameters)

            #reset networks from the master network
            GA = self.masterAnet.copy() 
            GtempA = self.masterAnet.copy()
            if self.masterBnet <> None:
                GB = self.masterBnet.copy()
                GtempB = self.masterBnet.copy()
            networks = GtempA, GtempB, GA, GB
            if self.ckbxviewnet.isChecked() == True or self.saveimage == True:
                self.graphvis = GA.copy()
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['state'] = self.active
            #reset these variables
            self.timestep = 0
            self.iterate = True
            if self.saveimage == True:            
                self.whenToSave = []
                r = 0    
                while r < GA.number_of_nodes():
                    self.whenToSave.append(r)
                    r += self.pertimestep
                  
            #reset all the containers for strong the results
            self.graphparameters = res.create_containers(GA, GB, self.parameters)
            if self.saveimage == True:
                #saves the initial image of the full network
                if self.ckbxviewnet.isChecked() == True: show = True
                else: show = False
                #get node size
                self.graphvis = self.get_node_size_metric(GA, self.graphvis, self.nodesizingmeth)
                self.graphvis = self.get_edge_size_metric(GA, self.graphvis, self.nodesizingmeth)
                self.imagedestlocation_withsim = self.imagedestlocation + '_sim' + str(self.iterationsdone+1)
                self.figureModel, self.timestep, self.whenToSave = draw(self.graphvis, self.positions, self.figureModel, self.timestep, self.coloractive, self.colorinactive, show, self.pertimestep, self.imagedestlocation_withsim, self.whenToSave, self.selected_vis, self.geo_vis)
                
            self.full_analysis(self.parameters)
            if int(self.iterationsdone) == int(self.numofiterations):
                self.lbl4.setText('completed all iterations')
                self.iterate == False
                self.multiiterations == False
                self.stop=True
                
        #for the end of a multiple iteration analysis
        #if self.runallseqmodels == True and self.iterate == False and int(self.iterationsdone) == int(self.numofiterations):
            #metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = self.parameters
        
        elif self.iterate == False and int(self.iterationsdone) == int(self.numofiterations):
            print '-----------------------------'            
            print 'ANALYSIS COMPLETED'
            #this writes the results from the last simulation to the text file
            if self.saveoutputfile == True:
                self.values = res.outputresults(self.graphparameters, self.parameters)
                                    
            self.lbl4.setText('Analysis completed')
            self.lbl4.adjustSize()
            QApplication.processEvents() #refresh gui
            #here need some code to calculate the the mean of the results already saved
            metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = self.parameters
            #networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = self.graphparameters

            if self.saveoutputfile == True and self.multiiterations == True:
                f = open(fileName,'a')
                f.write('\nAverage values are:\n')
                f.close()

                logfilepath = None
                if self.runallseqmodels == True:                
                    if RANDOM == True:
                        fileName = fileName+'_RANDOM'
                    elif DEGREE == True:
                        fileName = fileName+'_DEGREE'
                    elif BETWEENESS == True:
                        fileName = fileName+'_BETWEENNESS'
                    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges
                    self.values = res.outputresults(self.graphparameters, parameters,logfilepath,self.multiiterations)
                else:
                    self.values = res.outputresults(self.graphparameters, self.parameters,logfilepath,self.multiiterations)
                '''
                if error <> None:
                    if error == 0045:
                        QMessageBox.warning(self, 'Error', "Error when calcualting averages. There is an error in the reults textfile which prevents the results being averaged.")
                        return
                '''
            elif self.saveoutputfile == True and self.multiiterations == False:
                self.values = res.outputresults(self.graphparameters, self.parameters)
            '''
            In here need to send the code to another function which controls the analysis when runnig for all seq models.
            This does it after averaging the last results but before resetting everything.
            '''
            # checking to see if need to run again
            if self.runallseqmodels == True and BETWEENNESS <> True:
                self.runseqmodels()
            else:
                ok = QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed. Do you want to view the metric graphs?" , '&No','&View Graphs')
                if ok == 1: #if the view graph option is clicked
                    print '---------------------------'                    
                    print 'Outputting results'
                    pl.close()
                    self.q = ViewGraphs()
                    self.btnstep.setEnabled(True)#allow the button to be pressed again
                    self.btndraw.setEnabled(True)
                    self.ckbxviewnet.setEnabled(True)
                    self.reset_analysiscompleted()
                else:
                    pl.close()
                    self.reset_analysiscompleted()
                

                    
    def runseqmodels(self):
        #unpack the variables
        metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = self.parameters
        #update the variables        
        if RANDOM == True:
            RANDOM = False
            DEGREE = True
        elif DEGREE == True:
            DEGREE= False
            BETWEENNESS = True
        elif BETWEENNESS == True:
            print 'THIS SHOULD NEVER HAPPEN'
            exit()
        
        #reset networks from the master network
        GA = self.masterAnet.copy() 
        GtempA = self.masterAnet.copy()
        if self.masterBnet <> None:
            GB = self.masterBnet.copy()
            GtempB = self.masterBnet.copy()
        else: GB = None
        #networks = GtempA, GtempB, GA, GB
        if self.ckbxviewnet.isChecked() == True or self.saveimage == True:
            #reset the graphvis network
            self.graphvis = GA.copy()
            #loop through all the nodes setting them as active
            for node in self.graphvis.nodes_iter():  
                self.graphvis.node[node]['state'] = self.active
        #reset these variables
        self.iterationsdone = 0
        self.timestep = 0
        self.iterate = True
        #if the user wants images saved at set timesteps
        if self.saveimage == True:
            #create a list of time steps to save the images
            self.whenToSave = []
            r = 0    
            #populate the list given the time step between image saves as chosen by the user
            while r < GA.number_of_nodes():
                self.whenToSave.append(r)
                r += self.pertimestep
        #reset all the containers for strong the results
        self.graphparameters = res.core_analysis(GA, GB, self.parameters)
        #saves the initial image of the full network
        if self.saveimage == True:
            #does the user want the image to be shown as well as saved
            if self.ckbxviewnet.isChecked() == True: show = True
            else: show = False
            #get metric for node size
            self.graphvis = self.get_node_size_metric(GA, self.graphvis, 
                          self.nodesizingmeth)
            #get metric for edge thickness
            self.graphvis = self.get_edge_size_metric(GA, self.graphvis,
                          self.edgesizingmeth)         
            #get destination to save images
            self.imagedestlocation_withsim = self.imagedestlocation + '_'+ meth +'_sim_' + str(self.iterationsdone+1)
            #draw network
            self.figureModel, self.timestep, self.whenToSave = draw(self.graphvis,
                        self.positions, self.figureModel, self.timestep, 
                        self.coloractive, self.colorinactive, show, 
                        self.pertimestep, self.imagedestlocation_withsim,
                        self.whenToSave, self.selected_vis, self.geo_vis)

        print '=====================RUNNING FULL ANALYSIS================'
        #run the analysis
        self.full_analysis(self.parameters)
    
    def get_node_size_metric(self, G, graphvis, nodesizemethod):
        """This calcualtes the value which the size of the node will be based 
        on, if a method is selected."""
        
        #if method with idex of 0 is selected - no metric set
        if self.nodesizingmeth == 0:
            #create an empty list
            blist = []
            #loop through the nodes
            for node in G.nodes():
                #append teh default value
                blist.append(-999999)
        #if the method with index 1 is selected
        elif self.nodesizingmeth == 1:
            #get the degree of all nodes - only need the values
            blist_1 = G.degree().values()
            #need to normalise degree values to between 0 and 1
            #find the maximum value
            div = max(blist_1)
            #create an empty list
            blist = []
            #loop through all items in the list
            for item in blist_1:
                #if the div value is greater than 0
                if div <> 0:
                    #divide the degree by the maximum degree and append to list
                    blist.append(float(item)/float(div))
                else:
                    #if max is 0, then append zero for all nodes
                    blist.append(0) 
            #reset this list as none - nolonger needed
            blist_1 = None
        #if the index value is 2 - betweenness centrality
        elif self.nodesizingmeth == 2:
            #get the values for betweenness centrality
            #these already lie between 0 and 1
            blist = nx.betweenness_centrality(G).values()
        elif self.nodesizingmeth == 3:
            #get the clustering values for the nodes
            blist = nx.clustering(G).values()
        #loop through the nodes and assing the value
        p = 0
        for i in G.nodes_iter():
            #a value below 0.1 is two small - ie. wont be seen on the visualisation
            #this will set a value of 0.1 for all nodes concerned
            if blist[p] < 0.1:
                G.node[i]['size'] = 0.1
                graphvis.node[i]['size'] = 0.1
            #else assign calcualted value
            else:
                G.node[i]['size'] = blist[p]
                graphvis.node[i]['size'] = blist[p]
            p += 1
        return graphvis
    
    def get_edge_size_metric(self, G, graphvis, edgesizemethod):
        """Calcualte, if necasry, a value for every edge as requested by the 
        user."""
        #if the index value is zero - no metric option selected
        if self.edgesizingmeth == 0:
            #create empty list
            blist = []
            #loop through all the edges
            for ed in G.edges_iter():
                #append a default for for all edge into the list
                blist.append(-999999)
        #if the index value is set at one
        elif self.edgesizingmeth == 1:
            #get the edge betweenness values for each edge
            blist = nx.edge_betweenness_centrality(G,normalized=True).values()
        #assign the values to the edges in the network
        p = 0
        for o,d in G.edges_iter():
            G[o][d]['size'] = blist[p]
            graphvis[o][d]['size'] = blist[p]
            p += 1
        return graphvis        
        
    def drawview(self, changedA):
        """Draws the network without running any anlysis. Initiated by the Draw
        button and option in the edit menu."""
        #is there is a view window alrady open, close it
        pl.close()
        #get the network values from the input values
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()
        #see if any of the values have changed since a network was last built
        changedA = self.check_for_changes(param1,param2,param3, 'A')
        print "changedA is:", changedA
        #if the net is from the database it will not have changed
        if self.graph == 'Database':
            pass
        else:        
            if self.G == None or changedA == True:                 
                #checks if the user has changed any of the input values                
                self.positions = None #need to reset the positions as well
                self.G = self.buildnetwork(param1,param2,param3,'A')
                if self.G == None:
                    return
        #make a copy of the network for the graphvis network
        self.graphvis = self.G.copy()
        #set all nodes as active
        for node in self.graphvis.nodes_iter():  
            self.graphvis.node[node]['state'] = self.active
        #ask the user which type of visualisation they want
        selected = self.show_visselection()
        #if the user clicks cancel
        if selected == False:
            self.graphvis = None
            return
        #if geographic is selected
        if selected == 'Geographic':
            print "BEFORE GETTING POSITIONS"
            print self.G.edges()
            print '---------------------------'
            #get positions and network - this is much more detailed than the standard network
            self.geo_vis, self.positions = self.getpositions(selected, self.G)
            print "----------------------------"
            print "AFTER GETTING POSITIONS"
            print self.geo_vis.edges()
            print "----------------------------"
        else:
            #get the positions - the graphvis network is good enough
            self.positions = self.getpositions(selected, self.G)
            self.geo_vis = None
        #set the required variables
        self.timestep = -1
        self.figureModel = None
        #theses are needed for auto saving when running failure analysis        
        self.show = True
        #get metric for node thickness
        self.graphvis = self.get_node_size_metric(self.G, self.graphvis, 
                              self.nodesizingmeth)
        #get metric for edge thickness
        self.graphvis = self.get_edge_size_metric(self.G, self.graphvis, 
                              self.nodesizingmeth)
        #draw the network
        self.figureModel, self.timestep, self.whenToSave = draw(self.graphvis,
                            self.positions, self.figureModel, self.timestep,
                            self.coloractive, self.colorinactive, self.show, 
                            self.pertimestep, self.imagedestlocation, 
                            self.whenToSave,selected,self.geo_vis)

     
    def step_analysis(self, changedA):
        ''''Perform the resilience analysis through user control for each node
        removal process.'''
        print 'Performing STEP analysis'
        if self.timestep > 1:        
            self.forthread = self.thread.update()
            self.graphparameters, self.parameters, self.iterate = self.forthread
        else:
            pass
        
        self.btndraw.setEnabled(False)
        self.btnstep.setEnabled(False)
        self.btnstart.setText('Compelte')
        self.ckbxviewnet.setEnabled(False)
        self.disableallckbx()
        self.iterate = True        
        self.timestep += 1
        
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()
        changedA = self.check_for_changes(param1,param2,param3,'A')  

        #if the network has not been built yet
        if self.G == None or changedA == True:
            self.lbl4.setText('Intialising')
            self.lbl4.adjustSize()
            QApplication.processEvents()   
            self.G = self.buildnetwork(param1,param2,param3,'A')
            if self.G <> None:
                self.graphvis = None
                self.positions = None
                #create copy for visualisation and set active attribute
                self.graphvis=self.G.copy()
                print self.graphvis.number_of_nodes()
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['state'] = self.active
                self.parameters = self.get_analysis_type()   
            else:
                self.btnstep.setEnabled(True)
                self.btndraw.setEnabled(True)
                self.ckbxviewnet.setEnabled(True)
                self.enableallckbx()
                return
        else: 
            if self.graphvis == None or self.changedA == True: #if network has already been built and the inputs have not changed              
                self.positions = None
                self.graphvis=self.G.copy()
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['state'] = self.active      
        if self.parameters == None:
            self.parameters = self.get_analysis_type()
        metrics,STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges = self.parameters
        if self.GnetB == None and STAND_ALONE == False:
            param1 = self.txtparamB1.text()
            param2 = self.txtparamB2.text()
            param3 = self.txtparamB3.text()
            self.GnetB = self.buildnetwork(param1,param2,param3,'B')
            if self.GnetB == None:
                self.btnstep.setEnabled(True)
                self.btndraw.setEnabled(True)
                self.ckbxviewnet.setEnabled(True)
                self.enableallckbx()
                return
            if DEPENDENCY == True:
                a_to_b_edges = self.AtoBEdges()
            if INTERDEPENDENCY == True:
                a_to_b_edges = self.AtoBEdges()
                b_to_a_edges = self.BtoAEdges()          
            self.parameters = metrics,STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
        #self.metrics = self.sort_metrics(self.parameters)
        if fileName == None:
            fileName = self.setfilelocation_save()
            if fileName == '': #in case the user clicks cancel or the file cannot be accessed
                self.btndraw.setEnabled(True)
                self.btnstep.setEnabled(True)
                self.lbl4.setText('Ready')
                self.lbl4.adjustSize()
                self.timestep = -1
                self.btnstart.setText('Start')
                return
            self.parameters = self.metrics,STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
        
        if self.ckbxviewnet.isChecked() or self.saveimage == True:
            if self.positions == None:
                selected = self.show_visselection()
                self.selected_vis = selected
                G = self.G
                if selected == 'Geographic':
                    self.positions, self.geo_vis = self.getpositions(selected, G)
                else:
                    self.positions = self.getpositions(selected, G)

        if self.whenToSave == [] and self.saveimage == True:
            self.whenToSave = []
            r = 0    
            while r < self.G.number_of_nodes():
                self.whenToSave.append(r)
                r += self.pertimestep
                
        if self.parameters == None: #needed if network is drawn before doing analysis
            self.parameters = self.get_analysis_type()
        self.lbl4.setText('Processing')
        self.lbl4.adjustSize()
        QApplication.processEvents()
        
        if self.timestep == 0:
            #temporary until full dependence compatability
            #metrics = self.sort_metrics(self.parameters)
            self.parameters = self.metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
            if STAND_ALONE == True:
                self.GnetB = None 
            self.graphparameters = res.create_containers(self.G, self.GnetB, self.parameters)
            self.forthread = self.graphparameters, self.parameters, self.iterate
            self.updateUi()
        elif self.timestep == 1:            
            self.thread.setup(self.G, self.iterate, self.parameters, self.graphparameters)
        elif self.timestep > 1:
            self.forthread = self.graphparameters, self.parameters, self.iterate
            networks,i,node_list, to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = self.graphparameters
            GA,GATemp,GB,GBTemp = networks
            self.G = GA    
            self.thread.setup(self.G, self.iterate, self.parameters, self.graphparameters)
        else:
            print 'major error'
        self.btnstep.setEnabled(True)
        
    def full_analysis(self, parameters = None):
        '''Runs the analysis of the whole network in one go. Called by the 
        'Start' button and from the edit menu.'''
        #print 'Performing FULL analysis'
        #----------------set variables and interface
        self.btnstart.setText("Pause")
        if self.pause == True:
            self.running = False
            self.lbl4.setText("Paused")
            self.btnstart.setText("Re-Start")
            return
        if parameters <> None:
            self.parameters = parameters
 
        self.fullanalysis = True
        self.btnstep.setEnabled(False)
        self.btndraw.setEnabled(False)
        self.ckbxviewnet.setEnabled(False)
        self.disableallckbx()
        self.timestep += 1
        #-----------------build network A
        param1 = self.txtparamA1.text()
        param2 = self.txtparamA2.text()
        param3 = self.txtparamA3.text()
        changedA = self.check_for_changes(param1,param2,param3,'A')

        
        #----------------needs looking at-------------------------
        #this has had to be changed and has not been fully tested        
        if self.multiiterations <> None and self.graph <> 'Database':
            self.G = self.masterAnet
        #----------------above needs checking it still works

        if self.G == None or changedA == True:
            #print 'stuck here 4'
            self.lbl4.setText('Intialising')
            self.lbl4.adjustSize()
            QApplication.processEvents()
            #rebuild network if the inputs have changed
            if self.changedA == True:
                #print 'built network'
                self.G = self.buildnetwork(param1,param2,param3,'A')
            
            if self.G <> None:
                #create a copy for the vis and adds attribute state
                self.positions = None
                self.graphvis=self.G.copy()
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['state'] = self.active
                print 'THIS IS WHERE IT CALLS get analysis type'
                self.parameters = self.get_analysis_type()

            if self.G == None: #reset the interface as network could not be built
                self.btnstep.setEnabled(True)
                self.btndraw.setEnabled(True)
                self.ckbxviewnet.setEnabled(True)
                self.enableallckbx()
                return
        elif self.graphvis == None:
            print 'Creating a copy of G for graphvis'
            self.graphvis=self.G.copy()
            for node in self.graphvis.nodes_iter():  
                self.graphvis.node[node]['state'] = self.active
            self.parameters = self.get_analysis_type()
        #-----------------check parameters exist
        #this is needed if the user draws the network first       
        if self.parameters == None:
            self.parameters = self.get_analysis_type()

        #-----------------unpack parameters
        failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = self.parameters
        
        #-----------------check network B and build if needed
        
        self.GnetB = self.masterBnet
        if self.GnetB == None and failure['stand_alone'] == False:
            param1 = self.txtparamB1.text()
            param2 = self.txtparamB2.text()
            param3 = self.txtparamB3.text()
            self.GnetB = self.buildnetwork(param1,param2,param3,'B')
            failure['dependency'] = True #this is needed if dependency is not selected manually
            if self.GnetB <> None:            
                pass
            else:
                self.btnstep.setEnabled(True)
                self.btndraw.setEnabled(True)
                self.ckbxviewnet.setEnabled(True)
                self.enableallckbx()
                return
        #build edges if needed
        if failure['dependency'] == True:
            a_to_b_edges = self.AtoBEdges()
            #a_to_b_edges = self.txtparamt1.text()
            print 'a to b edges are: ', a_to_b_edges
        if failure['interdependency'] == True:
            a_to_b_edges = self.AtoBEdges()
            b_to_a_edges = self.BtoAEdges()
            
        self.parameters = failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length

        #------------------for safety reasons
        if self.parameters == None:
            print 'this is here for satefy. SHOULD NEVER BE USED'
            self.parameters = self.get_analysis_type()
        #-------------------sort metrics here - this is required when not stand_alone
        #if self.timestep == 0:
            #self.metrics = self.sort_metrics(self.parameters)        
        #------------------get file name and handle an error arising here
        if fileName == None and self.saveoutputfile == True:
            #print 'asks here as well'
            print fileName
            fileName = self.setfilelocation_save()
            if fileName == '':
                self.btndraw.setEnabled(True)
                self.btnstep.setEnabled(True)
                self.btnstart.setText("Start")
                self.btnstart.setEnabled(True)
                self.running = False
                self.pause = True
                self.lbl4.setText('Ready')
                self.lbl4.adjustSize()
                self.timestep = -1
                self.iterate = True
                self.fullanalysis = False
                self.enableallckbx()
                self.ckbxviewnet.setEnabled(True)
                return
            self.parameters = failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
            
        if self.whenToSave == [] and self.pertimestep > 0:
            self.whenToSave = []
            r = 0    
            while r < self.G.number_of_nodes():
                self.whenToSave.append(r)
                r += self.pertimestep
                
        #-------------------run the analysis-----------------------------------
        self.lbl4.setText('Processing')
        self.lbl4.adjustSize()
        QApplication.processEvents()
        if self.ckbxviewnet.isChecked() or self.saveimage == True:
            print 'this is where it is asking for the positions'
            if self.positions==None: 
                selected = self.show_visselection()
                self.selected_vis = selected
                G = self.G
                if selected == 'Geographic':
                    print 'USING THE CORRECT BIT'
                    self.geo_vis, self.positions = self.getpositions(selected, G)
                    print self.geo_vis
                    print self.geo_vis.number_of_nodes()
                else:
                    self.positions = self.getpositions(selected, G)
                    self.geo_vis = None
        
        print 'TIME STEP IS:', self.timestep
        if self.timestep == 0:
            #print 'running first time step'
            if failure['stand_alone'] == True: #this is tempory until we built in the ability to do dependency function
                self.GnetB = None
            
            #use metrics initial function to set up metric dicts and graph parameters
            self.metrics,self.graphparameters = res.metrics_initial(self.G,self.GnetB,self.metrics, failure, handling_variables, length, a_to_b_edges)          
            self.parameters = failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
            print '!!!!Need to sort out the, to_b_nodes, from_a_nodes!!!!'
          
            self.forthread = self.graphparameters, self.parameters, self.metrics, self.iterate
            self.updateUi()
        
        if self.timestep > 0:
            self.forthread = self.graphparameters, self.parameters, self.metrics, self.iterate               

            networks,i,node_list, to_b_nodes, from_a_nodes = self.graphparameters
            GtempA,GtempB,GA,GB = networks
            self.G = GA     
            self.thread.setup(self.G, self.iterate, self.metrics, self.parameters, self.graphparameters)
        
    def sort_metrics(self):
        '''Set the condition of all the posible metrics based on the parameters.'''
        #print 'Running SORT metrics'
        #failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = self.parameters
        basic_metrics_A = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,
                   'no_of_edges':True,'no_of_components':True,
                   'no_of_isolated_nodes':True,'isolated_nodes_removed':True,
                   'nodes_selected_to_fail':True}
        option_metrics_A = {'size_of_components':   False,                    
                    'giant_component_size':         False,
                    'avg_size_of_components':       False,
                    'isolated_nodes':               False,
                    'no_of_isolated_nodes_removed': False,
                    'subnodes':                     False,
                    'no_of_subnodes':               False,
                    'avg_path_length':              False,
                    'avg_path_length_of_components':False,
                    'avg_path_length_of_giant_component':   False,
                    'avg_geo_path_length':                  False,
                    'avg_geo_path_length_of_components':    False,
                    'avg_geo_path_length_of_giant_component':False,
                    'avg_degree':                   False,
                    'density':                      False,
                    'maximum_betweenness_centrality':False,
                    'avg_betweenness_centrality':   False,
                    'assortativity_coefficient':    False,
                    'clustering_coefficient':       False,
                    'transitivity':                 False,
                    'square_clustering':            False,
                    'avg_neighbor_degree':          False,
                    'avg_degree_connectivity':      False,
                    'avg_degree_centrality':        False,
                    'avg_closeness_centrality':     False,
                    'diameter':                     False}
        
        basic_metrics_B = basic_metrics_A.copy()
        option_metrics_B = option_metrics_A.copy()
    
        metrics = basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B
        return metrics

    def show_visselection(self):
        '''Loads a GUI where the user can select a method for positioning the 
        nodes when visualised.'''
        print 'IN SHOW_VISSELECTION'
        if self.graph == 'Database':
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)', 'Geographic'
        else:
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'

        method, ok = QInputDialog.getItem(self, 'Input Dialog', 
            'Select visualisation method:', items)
        if ok == False:
            method = False
        return method  

    def getpositions(self, selected, G):
        '''Uses the selected text from the combo box to calculate the positions
        for the nodes.'''
        'Random', 'Circle', 'Spring', 'Shell', 'Spectral', 'Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'
        print 'In getpositions'
        if selected == 'Random':
            positions=nx.random_layout(G)
        elif selected == 'Circle':
            positions=nx.circular_layout(G)
        elif selected == 'Spring':
            positions=nx.spring_layout(G)
        elif selected == 'Shell':
            positions=nx.shell_layout(G)
        elif selected == 'Spectral':
            positions=nx.spectral_layout(G)
        elif selected == 'Circle Tree (bfs)':
            bfs = True
            positions=vis.tree_circle(G, bfs)
        elif selected == 'Circle Tree (dfs)':
            bfs = False
            positions=vis.tree_circle(G, bfs)
        elif selected == 'Tree (dfs)':
            bfs = False
            positions=vis.tree(G, bfs)
        elif selected == 'Tree (bfs)':
            bfs = True
            positions=vis.tree(G, bfs)
        elif selected == 'Geographic':
            positions = None
            geo_vis, positions=vis.geo(self.G)
        else:
            print 'Error in the selection of vis method'
    
        if selected == 'Geographic':
            return geo_vis, positions
        else:
            return positions
        
    def get_analysis_type(self):
        '''Get the analysis type, the file location and if any of the other 
        options have been selected related to the analysis if the network.'''

        #as default, all are set as false, then changed if requested
        failure = {'stand_alone':False,'dependency':False,'interdependency':False,
                   'single':False,'sequential':False,'cascading':False,
                   'random':False,'degree':False,'betweenness':False}
        handling_variables = {'remove_subgraphs':False,'remove_isolates':False,'no_isolates':False}
        
        self.analysistype = self.cmboxtype.currentText()
        #get the type from the text from the drop down menu
        if self.analysistype == 'Single':failure['stand_alone']=True
        elif self.analysistype == 'Dependency':failure['dependency']=True
        elif self.analysistype == 'Interdependency':failure['interdependency']=True
        
        fileName = None
        if fileName == "": #if user clicks cancel, exits the routine
            QMessageBox.information(self, 'Information', "Successfully ended process.")
            self.nofilename = True   
            self.G = None
            self.reset()
            return
        else:
            pass
        if self.runallseqmodels == False:
            self.nofilename = False
            if self.ckbxSingle.isChecked() and self.ckbxRandom.isChecked():
                failure['single']=True
                failure['random']=True
            elif self.ckbxSequential.isChecked() and self.ckbxRandom.isChecked():
                failure['sequential']=True
                failure['random']=True
            elif self.ckbxSequential.isChecked() and self.ckbxDegree.isChecked():
                failure['sequential']=True
                failure['degree']=True
            elif self.ckbxSequential.isChecked() and self.ckbxBetweenness.isChecked():
                failure['sequential']=True
                failure['betweenness']=True
            elif self.ckbxCascading.isChecked() and self.ckbxRandom.isChecked():
                failure['cascading']=True
                failure['random']=True
            elif self.ckbxCascading.isChecked() and self.ckbxDegree.isChecked():
                failure['cascading']=True
                failure['degree']=True
            elif self.ckbxCascading.isChecked() and self.ckbxBetweenness.isChecked():
                failure['cascading']=True
                failure['betweenness']=True
            else:
                self.lbl4.setText("Error")
        else:
            failure['sequential']=True
            failure['random']=True
        
        self.lbl4.adjustSize()
        self.lbl4.show()
        QApplication.processEvents() #refresh gui
        handling_variables = {'remove_subgraphs':False,'remove_isolates':False,'no_isolates':False}
        if self.ckbxsubgraphs.isChecked():
            handling_variables['remove_subgraphs']=True
        if self.ckbxisolates.isChecked():
            handling_variables['remove_isolates']=True
        if self.ckbxnoisolates.isChecked():
            handling_variables['no_isolates']

        db_parameters = self.dbconnect
        a_to_b_edges = self.AtoBEdges
        
        print '!!!!length is undefined - need to be fixed!!!!'
        length = None

        write_step_to_db = self.write_step_to_db
        write_results_table = self.write_results_table
        store_n_e_atts = self.store_n_e_atts
        
        parameters = failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
        return parameters
    
    def setfilelocation_open(self):
        '''Ge the location of  file to open.'''
        fileName = QFileDialog.getOpenFileName(self, 'Open File', '.txt' )
        return fileName
        
    def setfilelocation_save(self):
        '''Set the file location for the output file.'''
        fileName = QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        return fileName  
        
    def networkselectionA(self, text):
        '''Alter the interface depending on what is selected in the combo box 
        for graph type for network A.'''
        self.graph = text
        if text == 'Random - GNM':
            self.clearA()
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamA2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389. Min = 1, Max = 6000') 
        elif text == 'Random - Erdos Renyi':
            self.clearA()
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamA2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
        elif text == 'Small-World':
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(True)
            self.txtparamA1.setToolTip('The number of nodes. eg.,34 or 178. Min = 1, Max = 2000')
            self.txtparamA2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15. Min = 1, Max = 200')
            self.txtparamA3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
        elif text == 'Scale-free':
            self.clearA()
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamA2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 50')
        elif text == 'Hierarchical Random':
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(True)
            self.txtparamA1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparamA2.setToolTip('The number of children from each new node. eg., 2 or 6. Min = 1, Max = 10')
            self.txtparamA3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Random +':
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(True)
            self.txtparamA1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparamA2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 10')
            self.txtparamA3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Communities':
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 4')
            self.txtparamA2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
        elif text == 'Tree':
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setToolTip('The number of child nodes per parent. eg., 3 or 5. Min = 1, Max = 50')
            self.txtparamA2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6. Min = 1, Max = 10')
        elif text == 'Database':
            self.clearA()
            self.txtparamA1.setEnabled(False)
            self.txtparamA2.setEnabled(False)
            self.txtparamA3.setEnabled(False)
            self.getdbnetwork('A')
        elif text == 'From CSV':
            self.clearA()
            self.txtparamA1.setEnabled(False)
            self.txtparamA2.setEnabled(False)
            self.txtparamA3.setEnabled(False)
            self.openfileA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA1.setEnabled(True)
        elif text == 'Lists':   
            self.clearA()
            self.txtparamA1.setEnabled(True)
            self.txtparamA2.setEnabled(True)
            self.txtparamA3.setEnabled(False)
            self.txtparamA1.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
            self.txtparamA2.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')
            ####open textbox for inputs, then display in list box
            ####could replace txtbox with a edit button, which when clicked opens window            
            
    def networkselectionB(self, text):
        '''Alter the interface depending on what is selected in the combo box 
        for graph type for network B.'''
        self.graph = text
        #print 'In networkselectionB'
        if self.graph <> 'None':
            self.cmboxtype.setCurrentIndex(1)
            DEPENDENCY = True
            self.txtparamt1.setEnabled(True)
        else:
            DEPENDENCY = False
        if text == 'None':
            self.clearB()
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setEnabled(False)
            self.txtparamB2.setEnabled(False)
        elif text == 'Random - GNM':
            self.clearB()
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamB2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389. Min = 1, Max = 6000') 
        elif text == 'Random - Erdos Renyi':
            self.clearB()
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamB2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
        elif text == 'Small-World':
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(True)
            self.txtparamB1.setToolTip('The number of nodes. eg.,34 or 178. Min = 1, Max = 2000')
            self.txtparamB2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15. Min = 1, Max = 200')
            self.txtparamB3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
        elif text == 'Scale-free':
            self.clearB()
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparamB2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 50')
        elif text == 'Hierarchical Random':
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(True)
            self.txtparamB1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparamB2.setToolTip('The number of children from each new node. eg., 2 or 6. Min = 1, Max = 10')
            self.txtparamB3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Random +':
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(True)
            self.txtparamB1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparamB2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 10')
            self.txtparamB3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Communities':
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 4')
            self.txtparamB2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
        elif text == 'Tree':
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setToolTip('The number of child nodes per parent. eg., 3 or 5. Min = 1, Max = 50')
            self.txtparamB2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6. Min = 1, Max = 10')
        elif text == 'Database':
            self.clearB()
            self.txtparamB1.setEnabled(False)
            self.txtparamB2.setEnabled(False)
            self.txtparamB3.setEnabled(False)
            self.getdbnetwork('B')
        elif text == 'From CSV':
            self.clearB()
            self.txtparamB1.setEnabled(False)
            self.txtparamB2.setEnabled(False)
            self.txtparamB3.setEnabled(False)    
            self.openfileB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
        elif text == 'Lists':   
            self.clearB()
            self.txtparamB1.setEnabled(True)
            self.txtparamB2.setEnabled(True)
            self.txtparamB3.setEnabled(False)
            self.txtparamB1.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
            self.txtparamB2.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')
            ####open textbox for inputs, then display in list box
            ####could replace txtbox with a edit button, which when clicked opens window            
        return DEPENDENCY
        
    def reset_failed_build(self):
        self.btnstart.setText('Start')
        self.pause = False
        self.running =False
        self.fullanalysis = False
        self.btnstep.setEnabled(True)
        self.btndraw.setEnabled(True)
        self.ckbxviewnet.setEnabled(True)
        self.disableallckbx()
        self.timestep += -1
        self.enableallckbx()
    
    #slot to be called when start button is clicekd
    def buildnetwork(self, param1,param2,param3, net):
        '''Builds the network using the user selected option as well as 
        checking for the correct input values. If graph not built, G = None'''
        if net == 'A':
            self.lastparam1A = param1[:]
            self.lastparam2A = param2[:]
            self.lastparam3A = param3[:]
        elif net == 'B':
            self.lastparam1B = param1[:]
            self.lastparam2B = param2[:]
            self.lastparam3B = param3[:]
        else:
            print 'Failure - net text did not match'
            exit()
        #self.G = None # this line should be moved to where this is called from allowing for it to clear A or B. In here they are not differentiatied 
        print 'Graph type used:', self.graph
        #build network
        if self.graph == "Small-World": #ws 
            #check contents is not blank
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', 
                                    "Input for parameter 1 is blank for network %s." %(net))
                self.reset_failed_build()                
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', 
                                    "Input for parameter 2 is blank for network %s." %(net))
                self.reset_failed_build()
                return
            if param3 == '':  
                QMessageBox.warning(self, 'Error!', 
                                    "Input for parameter 3 is blank for network %s." %(net))
                self.reset_failed_build()
                return
            #check can convert strings to intergers/floats
            try:        
                param1 = int(param1)
            except:        
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of nodes, is in an incorrect format. This value should be an integer." %(net))
                self.reset_failed_build()
                return
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the number of connected neighbours, is in an incorrect format. This value should be an interger."%(net))
                self.reset_failed_build()
                return
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of rewiring, is in an incorrect format. This needs to be a value between 0 and 1.")
                self.reset_failed_build()
                return
            #check specifics for the graph model
            if param2 >= param1:
                QMessageBox.warning(self, 'Error!', "Input parameter 2 needs to be less than input parameter 1.")
                self.reset_failed_build()
                return
            if param3 <0 or param3 >1:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3 is an incorrect value. This should be between 0 and 1.")
                self.reset_failed_build()
                return
            tempG = nx.watts_strogatz_graph(param1, param2, param3)
            if nx.is_connected(tempG)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase parameter 2 or decrease parameter 3.", '&OK')                  
                #would like to put a retry button on the message box, but not sure how we would know how to restart the analysis after doing this, as can be called from two places
                self.reset_failed_build()
                return #exit sub
        elif self.graph == "GNM": #gnm
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s. This needs to be an integer" %(net))
                self.reset_failed_build()
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s. This needs to be an integer." %(net))
                self.reset_failed_build()
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of nodes, is in an incorrect format. This needs to be an integer." %(net))             
                self.reset_failed_build()
                return        
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the nuber of edges, is in an incorrect format. This needs to be an integer." %(net))
                self.reset_failed_build()
                return
            tempG = nx.gnm_random_graph(param1, param2)
            if nx.is_connected(tempG)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                tempG = None #needs to reset G to none when graph is unconnected                
                self.btnstep.setEnabled(True)#allow the button to be pressed again                            
                self.reset_failed_build()                
                return #exit sub
        elif self.graph == "Scale-free": #ba
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                self.reset_failed_build()
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s." %(net))
                self.reset_failed_build()
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of nodes, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return           
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the nuber of edges, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return
            tempG = nx.barabasi_albert_graph(param1, param2)
            if nx.is_connected(tempG)==False:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                self.reset_failed_build()
                return #exit sub
        elif self.graph == "Random - Erdos Renyi": #er
            print 'its in here'
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                self.reset_failed_build()                
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blankfor network %s." %(net))
                self.reset_failed_build()
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of nodes, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return            
            try:            
                param2 = float(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the number of edges, is in an incorrect format. This should be a value between 0 and 1." %(net))
                self.reset_failed_build()
                return
            if param2 <0 or param2 >1:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s is an incorrect value. This should be a value between 0 and 1." %(net))
                self.reset_failed_build()
                return
            tempG = nx.erdos_renyi_graph(param1, param2)
            if nx.is_connected(tempG)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                self.reset_failed_build()
                return #exit sub
           
        elif self.graph == 'Hierarchical Random': #hr
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param3 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of child nodes per parent, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the number levels, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return 
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3 for network %s, the probability of new edges, is in an incorrect format. This should be a value between 0 and 1." %(net))
                self.reset_failed_build()
                return
            tempG = customnets.hr(param1,param2,param3)
        elif self.graph =='Hierarchical Random +': #ahr
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param3 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return                        
            try:          
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of child nodes per parent, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the number levels, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return 
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3 for network %s, the probability of new edges, is in an incorrect format. This should be a value between 0 and 1." %(net))
                self.reset_failed_build()
                return
            tempG = customnets.ahr(param1,param2,param3)
        elif self.graph == 'Hierarchical Communities': #hc
            #param1 = level
            #param2 = square/tri
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            try:          
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of levels, is in an incorrect format." %(net))
                self.reset_failed_build()
                return  
            try:          
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s,the type of sructure, is in an incorrect format." %(net))
                self.reset_failed_build()
                return   
            if param2 >= 2:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s,the type of sructure, is too high. It should be either 0 or 1." %(net))
            
            if param2 == 0:
                if param1 == 0 or param1 >= 6:
                    QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of levels, is incorrect. Should be between 1 and 5." %(net))
                else:
                    tempG = customnets.square(param1)
            elif param2 == 1:
                if param1 == 0 or param1 >= 5:
                    QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of levels, is incorrect. Should be between 1 and 4." %(net))
                else:
                    tempG = customnets.tri(param1)
            else:
                print 'There has been an error'
           
        elif self.graph == 'Tree': #trees
            #param 1 is the number of new nodes
            #param 2 is the number of level excluding the source
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank for network %s." %(net))
                 self.reset_failed_build()
                 return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 for network %s, the number of child nodes per parent, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 for network %s, the number levels, is in an incorrect format. This should be an integer." %(net))
                self.reset_failed_build()
                return  
            tempG = nx.balanced_tree(param1, param2)
        elif self.graph =='CSV':
            
            if param1 =='' or param2=='':
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please enter node and edge lists or select a different option.")
                self.reset_failed_build()
                return #exit sub
            tempG = nx.Graph()
            param1 = replace_all(param1, {' ':'','[':'',']':'',')':'','(':''})
            param1 = param1.split(',')
            nodelist=[]            
            for item in param1:
                item = int(item)
                nodelist.append(item)
            try:
                self.tempG.add_nodes_from(nodelist)
            except:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The node list for network %s does not fit the required format." %(net))
                self.reset_failed_build()
                return #exit sub
            param2 = replace_all(param2, {')':'',']':'','[':'',' ':''}) #clean the list
            param2 = param2.split('(') #split the list (also removes them)
            edgelist = [] #create the new edges list
            for item in param2: #for each item in the list
                if item == "": #if blank, skip
                    item = item
                else:
                    item = item.split(',') #split each itm on the comma
                    templist = [] #create a temp list to store the nodes for a list
                    for each in item: #for each node in the list
                        if each == "":
                            each = each                              
                        else:
                            each = int(each) #convert to integer
                            templist.append(each) #add to the node pair for an edge
                    edgelist.append(templist) #append the node pair list to the edge list
            try:
                tempG.add_edges_from(edgelist)
            except:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The edge list for network %s is not in the correct formart." %(net))         
                self.reset_failed_build()
                return #exit sub
        elif self.graph == 'Database':
            print '-------------SHOULD NOT HAVE TO DO ANYTHING--------------------'
            print self.G
            print self.G.number_of_nodes()
            print self.G.number_of_edges()
            tempG = self.G
            graph_edges = tempG.edges()   
            print graph_edges[0]
            print '---------------------------------------------------------------'
            print '---------------------------------------------------------------'
            
            
        elif self.graph == 'Lists': # or self.graph == 'Database': #lists
            #param1 is a list of nodes  #param2 is a list of egdes
            #need to convert the input strings to lists with integers in the correct format
            if param1 =='' or param2=='':
                if self.graph == 'Lists':
                    QMessageBox.warning(self, 'Error!', "Graph could not be created. Please enter node and edge lists or select a different option.")
                elif self.graph == 'Database':
                    QMessageBox.warning(self, 'Error!', "Graph could not be created. Please check the network or select a different option.")
                self.reset_failed_build()
                return #exit sub
            tempG = nx.Graph()
            param1 = replace_all(param1, {' ':'','[':'',']':'',')':'','(':''})
            param1 = param1.split(',')
            print 'len of param one is:', len(param1)
            print param1
            nodelist=[]            
            for item in param1:
                item = int(item)
                nodelist.append(item)
            try:
                tempG.add_nodes_from(nodelist)
            except:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The node list for network %s does not fit the required format." %(net))
                self.reset_failed_build()
                return #exit sub
            param2 = replace_all(param2, {')':'',']':'','[':'',' ':''}) #clean the list
            param2 = param2.split('(') #split the list (also removes them)
            edgelist = [] #create the new edges list
            for item in param2: #for each item in the list
                if item == "": #if blank, skip
                    item = item
                else:
                    item = item.split(',') #split each itm on the comma
                    templist = [] #create a temp list to store the nodes for a list
                    for each in item: #for each node in the list
                        if each == "":
                            each = each                              
                        else:
                            each = int(each) #convert to integer
                            templist.append(each) #add to the node pair for an edge
                    edgelist.append(templist) #append the node pair list to the edge list
            try:
                tempG.add_edges_from(edgelist)
            except:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The edge list for network %s is not in the correct formart." %(net))
                self.reset_failed_build()
                return #exit sub
        elif self.graph == 'None':
            QMessageBox.warning(self, 'Error!', "Error! Please try again. No graph method was selected. Self.graph was: %s!" %(self.graph))          
            self.reset_failed_build()
            return #exit sub
        else: 
            print 'self.graphs is:', self.graph
            QMessageBox.warning(self, 'Error!', "Error! Apollogies, the cause is unknown.")          
            self.reset_failed_build()
            return #exit sub
        self.param1 = param1 #make these freely accessable
        self.param2 = param2
        self.param3 = param3
        if tempG == None:
            self.cancel = True
            QMessageBox.warning(self, 'Error!', "Error! Apollogies, the cause is unknown.")
            return
        else:
            print 'Network built successfully. N = %s' %(tempG.number_of_nodes())
            if net == 'A':
                self.masterAnet = tempG.copy()
            elif net == 'B':
                self.masterBnet = tempG.copy()
            return tempG 
        
class Worker(QThread):

    def __init__(self, parent = None):
        print '***the thread is running***'
        QThread.__init__(self, parent)     
        graphparameters = None
        parameters = None
        metrics = None
        iterate = True
        self.forthread = graphparameters, parameters, metrics, iterate
    def __del__(self):
        self.exiting = True
        self.wait() 
    def setup(self, G, iterate, metrics, parameters, graphparameters):
        '''Controls the processes run in the work thread and starts it.'''
        self.G = G
        self.iterate = iterate
        self.parameters = parameters
        self.metrics = metrics
        self.graphparameters = graphparameters
        self.start() 
    def run(self):
        '''Runs the analysis by calling the function in the resilience module.'''
        #Note: This is never called directly. Always use .start to start the workthread.
        logfilepath = None
        args = res.step(self.graphparameters, self.parameters, self.metrics, self.iterate, logfilepath)
        if args == 0001:
            print 'ERROR! - 0001'
            return args
        elif args == None:
            print 'ERROR! - None returned'
            return args
        else:
            self.graphparameters, self.parameters, self.metrics, self.iterate = args
                    
        self.forthread = self.graphparameters, self.parameters, self.metrics, self.iterate
    def update(self):
        ''''''
        self.forthread = self.graphparameters, self.parameters, self.metrics, self.iterate
        return self.forthread

def draw(G, positions, figureModel, timestep, coloractive, colorinactive, show, pertimestep,imagedestlocation,whenToSave,selected_vis,geo_vis):
    '''Handles the initial setup parameters for drawing the network as well as then calling the function to draw the network'''
    #print 'In draw'    
    if figureModel == None or figureModel.canvas.manager.window == None: #if figure model window has not been opened yet
        #this line sets the dpi correctly
        figureModel = pl.figure(dpi = 100)
        pl.ion()
        if show == True:
            pl.show()
    
    #need this in case the user closes the window 
    try:
        figureModel.canvas.set_window_title('Network View') 
    except:
        figureModel = None
        figureModel = pl.figure(dpi = 100)
        figureModel.canvas.set_window_title('Network View') 
    pl.cla()    
    drawnet(G, positions, timestep, coloractive, colorinactive, selected_vis, geo_vis) 

    if pertimestep > 0 and len(whenToSave) > 0 and len(imagedestlocation) > 0:
        #print 'when to save is:' , whenToSave
        #print 'timestep is: ', timestep
        #print 'when to save zero is: ', whenToSave[0]
        if timestep == whenToSave[0]:
            i = 0
            while i < len(imagedestlocation):
                if imagedestlocation[i]=='.':
                    imagedestlocation=imagedestlocation[i:]
                    break
                i+=1
            imagedestlocation = imagedestlocation+'_%s.png' %(timestep)
            try:            
                #need to create a variable for the dpi
                print 'saving image at: ', imagedestlocation
                pl.savefig(str(imagedestlocation))
            except:
                QMessageBox.question('Message',
                    "Error when saving image. Continue analysis without saving \nthe images or terminate the analysis.", QMessageBox.Yes, QMessageBox.Ok)
                if QMessageBox.Yes:
                    whenToSave = []
                else:
                    return
            whenToSave.pop(0)
        else: pass
    if show ==True:
        pl.show()  
        figureModel.canvas.manager.window.update()  #gets error here when the window is closed by whatever means  
      
    return figureModel, timestep, whenToSave
      
def drawnet(G, positions, timestep, coloractive, colorinactive, selected_vis, geo_vis):
    '''Draws the network'''   
    pl.cla()
    #cheat way of removing the axis and labels quickly
    g1 = nx.Graph() 
    nx.draw(g1)
    #conditionals to change size of nodes depending on the number of them
    if G.number_of_nodes() <=50:
        size_mult = 300
    elif G.number_of_nodes()>50 and G.number_of_nodes()<=100:
        size_mult = 100
    elif G.number_of_nodes()>100 and G.number_of_nodes()<=250:
        size_mult = 50
    else:
        size_mult = 30
 
    if timestep <> -1:
        pl.title('iteration = ' + str(timestep))
    timestep+=1
    
    #get failed and working edges
    inactive_edges = []
    active_edges = []
    for o,d in G.edges_iter():
        if G.node[o]['state'] == 0 or G.node[d]['state'] == 0:
            temp = o,d            
            inactive_edges.append(temp)
        else:
            temp = o,d
            active_edges.append(temp)  
            inactive_nodes = []
            
    #get failed and working nodes
    inactive_nodes = []
    active_nodes = []
    for nd in G.nodes_iter():
        if G.node[nd]['state'] == 0:
            inactive_nodes.append(nd)
        elif G.node[nd]['state'] == 1:
            active_nodes.append(nd)
    
    if selected_vis == 'Geographic':
        #this works for tyne wear metro, not for eden though
        #not 100% why not for eden, could be due to way linstrings are handled in geo vis algorithm
        #plots all metro nodes, but not all eden nodes???
        Geo = geo_vis
        #this means geo vis only good for drawing, not for vis during failure modelling
        active_edges = Geo.edges()
        #active_nodes = Geo.nodes()
        print len(active_nodes)
        print G.number_of_nodes()
        print len(positions)
        nx.draw_networkx_nodes(G,
                    pos = positions,
                    nodelist = active_nodes,
                    node_color = str(coloractive),
                    node_size = 6#[Geo.node[i]['size'] *size_mult for i in Geo.nodes_iter()],
                    )
                    
        nx.draw_networkx_nodes(G,
                    pos = positions,
                    nodelist = inactive_nodes,
                    node_color = str(colorinactive),
                    node_size = 6#0.1*size_mult
                    )
                    
        
        nx.draw_networkx_edges(Geo, 
                           pos = positions, 
                           edgelist = inactive_edges,
                           edge_width = 6.0,
                           edge_color = 'r')#str(colorinactive)) 
        nx.draw_networkx_edges(Geo,
                           pos=positions,
                           edgelist=active_edges,
                           edge_width=6.0,
                           edge_color='g')#str(colorinactive)) 
        
        
        
        
        ''' #may allow for a basemap
        from mpl_toolkits.basemap import Basemap
        map1 = Basemap(projection='tmerc', width=1100000, height=1100000, lat_0=55,lon_0=-3 ,resolution='l')
        map1.drawcoastlines(linewidth=0.25)
        map1.drawcountries(linewidth=0.25)
        map1.fillcontinents(color='coral',lake_color='aqua')
        '''
    else:
        ''' #this is done outside the if statement at the moment
        inactive_edges = []
        active_edges = []
        for o,d in G.edges_iter():
            if G.node[o]['state'] == 0 or G.node[d]['state'] == 0:
                temp = o,d            
                inactive_edges.append(temp)
            else:
                temp = o,d
                active_edges.append(temp)
        '''
        print active_edges
        print positions.keys()
        #the edge widths should be changing, but they are not - not too sure why
        nx.draw_networkx_edges(G, 
                               pos = positions, 
                               edge_width = [G[o][d]['size'] *size_mult for o,d in G.edges_iter()], 
                               edgelist = inactive_edges,
                               edge_color = str(colorinactive)) 
        nx.draw_networkx_edges(G,
                               pos = positions,
                               edge_width = [G[o][d]['size'] *size_mult for o,d in G.edges_iter()],
                               edgelist = active_edges,
                               edge_color = str(coloractive))
        '''
        #i think that when a node becomes isolated, it is not being classed as inactive
        inactive_nodes = []
        active_nodes = []
        for nd in G.nodes_iter():
            if G.node[nd]['state'] == 0:
                inactive_nodes.append(nd)
            elif G.node[nd]['state'] == 1:
                active_nodes.append(nd)
        ''' 
        nx.draw_networkx_nodes(G,
                    pos = positions,
                    nodelist = active_nodes,
                    node_color = str(coloractive),
                    node_size = [G.node[i]['size'] *size_mult for i in G.nodes_iter()],
                    )
        nx.draw_networkx_nodes(G,
                    pos = positions,
                    nodelist = inactive_nodes,
                    node_color = str(colorinactive),
                    node_size = 0.1*size_mult
                    )
        
        print 'active nodes = ', len(active_nodes)
        print 'inactive nodes = ', len(inactive_nodes)
    
        
def replace_all(text, dic):
    'Used to modify strings to make them suitable for purpose.'
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text

    
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())      
    