# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/home/craig/.spyder2/.temp.py
"""

import sys
from PyQt4 import QtGui, QtCore
import networkx as nx
import pylab as pl
import matplotlib as mp
import visalgorithms_v8 as vis
import interdependency_analysis_v3_2 as res
import inhouse_algorithms as customnets
#from matplotlib.widgets import CheckButtons

try:
    import osgeo.ogr as ogr
except:
    print 'ERROR! OGR cannot be found. There will be no database functionality.'    
sys.path.append('C:/a8243587_DATA/GitProjects/nx_pgnet')
try:
    import nx_pg, nx_pgnet
except:
    print 'ERROR! Cannot find nx_pg functions, thus there will be limited or no data base functionality.'


class pickparameters(QtGui.QDialog):    
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)  
        self.lblop1 = QtGui.QLabel('Option 1:', self)
        self.lblop1.adjustSize()
        self.lblop1.move(25, 28)        
        self.option1 = QtGui.QComboBox(self)
        self.metriclist=['Average path length', 'Number of components', 'Average degree', 'Nodes count removed', 'Isolated node count', 'None']
        self.option1.addItems(self.metriclist)
        self.option1.move(90, 25)
        self.lblop2 = QtGui.QLabel('Option 2:', self)
        self.lblop2.adjustSize()
        self.lblop2.move(25, 58) 
        self.option2 = QtGui.QComboBox(self)
        self.option2.addItems(self.metriclist)      
        self.option2.move(90, 55)
        self.applybtn = QtGui.QPushButton('Apply', self)
        self.applybtn.move(55, 80)
        self.applybtn.clicked.connect(self.applyclick)
        self.cancelbtn = QtGui.QPushButton('Cancel', self)
        self.cancelbtn.move(135, 80)
        self.cancelbtn.clicked.connect(self.cancelclick)
        
        self.setGeometry(700,500,280,110)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Graph parameters')  #title of windpw          
        self.show()#show window  
    
    def applyclick(self):
        self.metric1 = self.option1.currentText()
        self.metric2 = self.option2.currentText()
        self.metric1 = self.identifymetric(self.metric1)
        self.metric2 = self.identifymetric(self.metric2)
        if self.metric1 == self.metric2:
            QtGui.QMessageBox.information(self, 'Warning','The same parameters have been selected for both options. Please change one.','&OK')
            return
        else:
            pl.close()
            self.close()
                    
    def cancelclick(self):
        self.close()            
    def getval(self):
        return self.metric1, self.metric2
    def identifymetric(self, metric):
        if metric == 'Average path length':
            metric = 0
        elif metric == 'Nodes count removed':
            metric = 1
        elif metric == 'Isolated node count':
            metric = 2
        elif metric == 'Average degree':
            metric = 3
        elif metric == 'Number of components':
            metric = 4
        elif metric == '':
            metric = 5
        elif metric == 'None':
            metric = 99
        else:
            print 'Uncategorised'
        return metric
        
class dbconnect(QtGui.QDialog):    
    def __init__(self, parent=None):
        #super(dbconnect, self).__init__(parent)
        QtGui.QDialog.__init__(self, parent)   
        #parametes for database connection     
        exitAction = QtGui.QAction('&Exit',self)
        exitAction.triggered.connect(QtGui.qApp.quit)
        self.DBNAME= ""
        self.HOST = "" 
        self.PORT = ""
        self.USER = ""
        self.PASSWORD = ""        
        self.lbl1 = QtGui.QLabel('dbname: ', self)
        self.lbl1.move(25,30)
        self.lbl1.adjustSize()
        self.txtinput1 = QtGui.QLineEdit(self)        
        self.txtinput1.move(75, 25)
        self.txtinput1.setText(self.DBNAME)
        self.txtinput1.setToolTip('name of database')
        self.lbl2 = QtGui.QLabel('host: ', self)
        self.lbl2.move(25,55)
        self.lbl2.adjustSize()
        self.txtinput2 = QtGui.QLineEdit(self)        
        self.txtinput2.move(75, 50)
        self.txtinput2.setToolTip('host of database')
        self.lbl3 = QtGui.QLabel('port: ', self)
        self.lbl3.move(25,80)
        self.lbl3.adjustSize()        
        self.txtinput3 = QtGui.QLineEdit(self)        
        self.txtinput3.move(75, 75)
        self.txtinput3.setToolTip('port')
        self.lbl4 = QtGui.QLabel('user: ', self)
        self.lbl4.move(25,105)
        self.lbl4.adjustSize()
        self.txtinput4 = QtGui.QLineEdit(self)        
        self.txtinput4.move(75, 100)
        self.txtinput4.setToolTip('user')
        self.lbl5 = QtGui.QLabel('password: ', self)
        self.lbl5.move(25,130)
        self.lbl5.adjustSize()
        self.txtinput5 = QtGui.QLineEdit(self)        
        self.txtinput5.move(75, 125)
        self.txtinput5.setToolTip('password')
        self.lbl6 = QtGui.QLabel('net name: ', self)
        self.lbl6.move(25,160)
        self.lbl6.adjustSize()
        self.txtinput6 = QtGui.QLineEdit(self)        
        self.txtinput6.move(75, 155)
        self.txtinput6.setToolTip('network name in database')

        self.applybtn = QtGui.QPushButton('Apply', self)
        self.applybtn.move(45, 185)
        self.applybtn.clicked.connect(self.savetext)
        
        self.cancelbtn = QtGui.QPushButton('Cancel', self)
        self.cancelbtn.move(130, 185)
        self.cancelbtn.clicked.connect(self.cancel)

        self.setGeometry(300,500,250,220)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('db Connection Parameters')  #title of windpw          
        self.show()#show window   
     
    def savetext(self):
        self.DBNAME = self.txtinput1.text()
        self.HOST = self.txtinput2.text()
        self.PORT = self.txtinput3.text()
        self.USER = self.txtinput4.text()
        self.PASSWORD = self.txtinput5.text()        
        self.NETNAME = self.txtinput6.text()
        self.DBconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        self.close()
    
    def cancel(self):
        self.close()
        
    def getval(self):
        return self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME

    def showDialog(self):     
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter your name:')      
        if ok:
            self.le.setText(str(text))
    def getValues(self):
        correct = 45
        return correct
                
class extraparamwindow(QtGui.QWidget): # not sure if I will need this after all
    
    def __init__(self):  
        QtGui.QWidget.__init__(self)
        self.initUI()
        
    def initUI(self):
        self.setGeometry(300,500,550,150) #above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Parameter Window') #title of window  
        self.show()#show window      

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        
        #create actions for file menu
        RunAction = QtGui.QAction('&Run',self)
        RunAction.setShortcut('Ctrl+R')
        RunAction.setStatusTip('Run the selected analysis')
        RunAction.triggered.connect(self.RunAnalysis)       
        
        exitAction = QtGui.QAction('&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        extraAction = QtGui.QAction('&Extra', self)
        extraAction.setShortcut('Ctrl+P')
        extraAction.setStatusTip('Open extra parameter window')
        extraAction.triggered.connect(self.showepWindow)

        dbAction = QtGui.QAction('&DB Connection', self)
        dbAction.setShortcut('Ctrl+B')
        dbAction.setStatusTip('Open db connection properties')
        dbAction.triggered.connect(self.showdbWindow)
        
        openAction = QtGui.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load node and edge lists from .txt file')
        openAction.triggered.connect(self.Open)
        
        self.built = False               
        viewnetAction = QtGui.QAction('&View Network', self)
        viewnetAction.setShortcut('Ctrl+D')
        viewnetAction.setStatusTip('View the network')
        self.built = viewnetAction.triggered.connect(self.View)               
    
        self.statusBar() #create status bar 
        menubar=self.menuBar() #create menu bar
        fileMenu = menubar.addMenu('&File') #add file menu
        editMenu = menubar.addMenu('&Edit') #add edit menu
        
        #add actions to file and edit menu's
        editMenu.addAction(RunAction)
        editMenu.addAction(viewnetAction)
        editMenu.addAction(extraAction)
        editMenu.addAction(dbAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
  
        self.lbl4 = QtGui.QLabel("STATE", self)
        self.lbl4.move(70,145)
        self.lbl4.adjustSize() 
        fontbold = QtGui.QFont("Calibri", 10, QtGui.QFont.Bold)      

        self.lbl6 = QtGui.QLabel("STATE: ", self)
        self.lbl6.move(25,144)
        self.lbl6.setFont(fontbold)
        self.lbl6.adjustSize() 
                
        self.lbl2 = QtGui.QLabel("Analysis types",self)
        self.lbl2.setFont(fontbold)
        self.lbl2.adjustSize()        
        self.lbl2.move(25,25)
        self.ckbx1 = QtGui.QCheckBox("Single",self)
        self.ckbx1.adjustSize()
        self.ckbx1.move(25,45)
        self.ckbx1.setToolTip("Remove one node and relpace before the next node is removed")
        self.ckbx1.toggle()
        self.ckbx1.stateChanged.connect(self.labelUpdate)
        self.ckbx2 = QtGui.QCheckBox("Sequential",self)
        self.ckbx2.adjustSize()
        self.ckbx2.move(25,65) 
        self.ckbx2.setToolTip("Remove nodes one after each other until none are left")
        self.ckbx2.stateChanged.connect(self.labelUpdate)
        self.ckbx3 = QtGui.QCheckBox("Cascading",self)
        self.ckbx3.adjustSize()
        self.ckbx3.move(25,85)
        self.ckbx3.setToolTip("Remove a node, them all it's neighbours, then all of their neighbours etc,")
        self.ckbx3.stateChanged.connect(self.labelUpdate)
        Group1 = QtGui.QButtonGroup(self)
        Group1.addButton(self.ckbx1)
        Group1.addButton(self.ckbx2)
        Group1.addButton(self.ckbx3)
        Group1.exclusive()
        
        self.lbl3 = QtGui.QLabel("Node selection method",self)
        self.lbl3.setFont(fontbold)
        self.lbl3.adjustSize()        
        self.lbl3.move(130,25)
        self.ckbx4 = QtGui.QCheckBox("Random", self)
        self.ckbx4.adjustSize()
        self.ckbx4.move(130,45)
        self.ckbx4.setToolTip("Select the node to remove at random")
        self.ckbx4.stateChanged.connect(self.labelUpdate)
        self.ckbx4.toggle()
        self.ckbx5 = QtGui.QCheckBox("Degree", self)
        self.ckbx5.adjustSize()        
        self.ckbx5.move(130,65)
        self.ckbx5.setToolTip("Select the node with the highest degree")
        self.ckbx5.stateChanged.connect(self.labelUpdate)        
        self.ckbx6 = QtGui.QCheckBox("Betweenness", self)
        self.ckbx6.adjustSize()
        self.ckbx6.move(130,85) 
        self.ckbx6.setToolTip("Select the node with the highest betweenness value")
        self.ckbx6.stateChanged.connect(self.labelUpdate)
        Group2 = QtGui.QButtonGroup(self)     
        Group2.addButton(self.ckbx4)
        Group2.addButton(self.ckbx5)
        Group2.addButton(self.ckbx6)
        Group2.exclusive()
        
        self.lbl1 = QtGui.QLabel("Network Options", self)
        self.lbl1.setFont(fontbold)
        self.lbl1.adjustSize()
        self.lbl1.move(275, 25)
        self.ckbx7 = QtGui.QCheckBox("WS", self)
        self.ckbx7.adjustSize()
        self.ckbx7.move(275, 45)
        self.ckbx8 = QtGui.QCheckBox("GNM", self)
        self.ckbx8.adjustSize()
        self.ckbx8.move(325, 45)
        self.ckbx7.toggle()
        self.ckbx9 = QtGui.QCheckBox("BA", self)
        self.ckbx9.adjustSize()
        self.ckbx9.move(275, 65)
        self.ckbx10 = QtGui.QCheckBox("ER", self)
        self.ckbx10.adjustSize()
        self.ckbx10.move(325, 65)
        self.ckbx12 = QtGui.QCheckBox("HR", self)
        self.ckbx12.adjustSize()
        self.ckbx12.move(275, 85)
        self.ckbx13 = QtGui.QCheckBox("HR+", self)
        self.ckbx13.adjustSize()
        self.ckbx13.move(275, 105)        
        self.ckbx14 = QtGui.QCheckBox("HC", self)
        self.ckbx14.adjustSize()
        self.ckbx14.move(325, 85)        
        self.ckbx15 = QtGui.QCheckBox("Tree", self)
        self.ckbx15.adjustSize()
        self.ckbx15.move(325, 105)
        self.ckbx11 = QtGui.QCheckBox("dB", self)
        self.ckbx11.adjustSize()
        self.ckbx11.move(275, 125)
        self.ckbx18 = QtGui.QCheckBox("Lists", self)
        self.ckbx18.adjustSize()
        self.ckbx18.move(325, 125)
        Group3 = QtGui.QButtonGroup(self)
        Group3.addButton(self.ckbx7)
        Group3.addButton(self.ckbx8)
        Group3.addButton(self.ckbx9)
        Group3.addButton(self.ckbx10)
        Group3.addButton(self.ckbx11)
        Group3.addButton(self.ckbx12)
        Group3.addButton(self.ckbx13)
        Group3.addButton(self.ckbx14)
        Group3.addButton(self.ckbx15)
        Group3.addButton(self.ckbx18)
        Group3.exclusive()
     
        self.lbl10 = QtGui.QLabel("Graph Inputs", self)
        self.lbl10.setFont(fontbold)
        self.lbl10.adjustSize()
        self.lbl10.move(400, 25)
        self.txtinput1 = QtGui.QLineEdit(self)        
        self.txtinput1.move(400, 45)
        self.txtinput1.setToolTip('The number of nodes')
        self.txtinput2 = QtGui.QLineEdit(self)
        self.txtinput2.move(400, 80)
        self.txtinput2.setToolTip('Number of neighbours connected to a node')
        self.txtinput3 = QtGui.QLineEdit(self)
        self.txtinput3.move(400, 115)
        self.txtinput3.setToolTip('Probability of being rewired eg.,0.4')
        
        self.ckbx7.stateChanged.connect(self.wsck)
        self.ckbx8.stateChanged.connect(self.gnmck)
        self.ckbx9.stateChanged.connect(self.back)
        self.ckbx10.stateChanged.connect(self.erck)  
        self.ckbx11.stateChanged.connect(self.dbc)
        self.ckbx12.stateChanged.connect(self.hrck)
        self.ckbx13.stateChanged.connect(self.ahrck)
        self.ckbx14.stateChanged.connect(self.hcck)
        self.ckbx15.stateChanged.connect(self.trck)
        self.ckbx18.stateChanged.connect(self.lick)
        
        self.lbl5 = QtGui.QLabel("Remove subgraphs/isolated nodes", self)
        self.lbl5.setFont(fontbold)
        self.lbl5.adjustSize()
        self.lbl5.move(25,105)
        self.ckbx16 = QtGui.QCheckBox("Subgraphs", self)  
        self.ckbx16.adjustSize()
        self.ckbx16.move(25, 120)
        self.ckbx16.setToolTip("Select if subgraphs are to be removed when they appear in the network")
        self.ckbx17 = QtGui.QCheckBox("Isolates", self)
        self.ckbx17.adjustSize()
        self.ckbx17.move(130, 120)
        self.ckbx17.setToolTip("Select if nodes are to be removed when they become isolated")

        self.ckbx19 = QtGui.QCheckBox("View net failure", self)
        self.ckbx19.adjustSize()
        self.ckbx19.move(200, 155)
        self.ckbx19.setToolTip("View the network failure as nodes are removed")
        #may be don't need a variable here, as can use the function below
        #self.ckbx19.stateChanged.connect(self.viewfailure) -dont need this here anymore. all action performed in the draw function

        self.btn2 = QtGui.QPushButton('Draw', self)
        self.btn2.move(300, 150)

        self.btn1 = QtGui.QPushButton('Start', self)
        self.btn1.move(400, 150)
        self.built = self.btn2.clicked.connect(self.View) #view the network and set built as true

        #self.btn1.clicked.connect(self.getdbparameters)
        self.btn1.clicked.connect(self.RunAnalysis)     
                
        self.setGeometry(300,300,515,185)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Resilience Analysis') #title of window 
        self.show() #show window
        
    def showepWindow(self):
        self.w = extraparamwindow()
        self.w.show()
    def showdbWindow(self):
        inputDlg = dbconnect(self)
        inputDlg.show() 
        
    def viewfailure(self):  #function to set state of variable for the visualising the network as it fails
        print 'runnning function'        
        if self.ckbx19.isChecked():
            print 'box checked'
            self.viewfaliures = True
        else:
            print 'box not checked'
            self.viewfailures = False
        print 'sucessfully checked state'
        return self.viewfaliures
        
    def Open(self):
        print 'needs finishing'
        self.ckbx18.toggle()
        self.lick()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        text=open(fname).read()
        text1, text2 = text.split('\n')
        self.txtinput1.setText(text1)
        self.txtinput2.setText(text2)
        #load in a csv, add lists to text boxes, then select lists for the input               
    def wsck(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(True)
        self.txtinput1.setToolTip('The number of nodes. eg.,34 or 178')
        self.txtinput2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15')
        self.txtinput3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
    def gnmck(self):
        self.txtinput3.setEnabled(False)
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
        self.txtinput2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389')   
    def back(self):
        self.txtinput3.setEnabled(False)
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
        self.txtinput2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6')
    def erck(self):
        self.txtinput3.setEnabled(False)
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
        self.txtinput2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
    def hrck(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(True)
        self.txtinput1.setToolTip('The number of level. eg., 2 or 4')
        self.txtinput2.setToolTip('The number of children from each new node. eg., 2 or 6')
        self.txtinput3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
    def ahrck(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(True)
        self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
        self.txtinput2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6')
        self.txtinput3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
    def hcck(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(False)
        self.txtinput1.setToolTip('The number of levels. eg., 2 or 4 (max is 4)')
        self.txtinput2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
    def trck(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(False)
        self.txtinput1.setToolTip('The number of child nodes per parent. eg., 3 or 5')
        self.txtinput2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6')
    def dbc(self):
        self.txtinput1.setEnabled(False)
        self.txtinput2.setEnabled(False)
        self.txtinput3.setEnabled(False)
    def lick(self):
        self.txtinput1.setEnabled(True)
        self.txtinput2.setEnabled(True)
        self.txtinput3.setEnabled(False)
        self.txtinput1.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
        self.txtinput2.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')
    def labelUpdate(self):
        self.lbl4.clear()
    def setLabel(self):
        self.lbl4.setText('Analysis running')
        self.lbl4.adjustSize()           
    def setFileLocation(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        return fileName
    """
    def checkconnection(self):
        dbconnect=False
        appl1 = self.showDialog1()
        if appl1 == True:
            appl2 = self.showDialog2()
            if appl2 == True:
                appl3 = self.showDialog3()
                if appl3==True:
                    appl4 = self.showDialog4()
                    if appl4 ==True:
                        appl5 = self.showDialog5()
                        if appl5 == True:
                            appl6 = self.showDialog6()
                            if appl6==True:
                                try:
                                    connection = str('PG:dbname = ')+str(self.dbName)+str(" host='")+str(self.host)+str("' port='")+str(self.port)+str("' user='")+str(self.user)+str("' password='")+str(self.password)+str("'")                  
                                    conn = ogr.Open(connection)
                                    G = nx_pgnet.read(conn).pgnet(self.network)   #load in network from database and create networkx instance
                                    return G
                                except:
                                    QtGui.QMessageBox.warning(self, 'Error!', "Could not connect to database and find the data. Please check your inputs and try again. The parameters were: \ndbname: "+self.dbName+"\nhost: "+self.host+"\nuser: "+self.user+"\nport: " +self.port+"\npassword: "+self.password+"\nnetwork: "+self.network,'&OK')
                                    #QtGui.QMessageBox.warning(self, 'Error!', "Could not connect to database and retireve data. Please check your inputs and try again.",'&OK')
                                    return dbconnect
                            else:
                                QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
                                return dbconnect
                        else:
                            QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
                            return dbconnect
                    else:
                        QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
                        return dbconnect
                else:
                    QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
                    return dbconnect
            else:
                QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
                return dbconnect
        else:
            QtGui.QMessageBox.information(self, 'Information','Database connection process terminated.','&OK')
            return dbconnect        
        
    def showDialog1(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 'dbName:')      
        if appl == True:
            self.dbName =(str(text))
        else:
            self.dbName = "Canceled"
        return appl
    def showDialog2(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 'host:')      
        if appl==True:
            self.host =(str(text))
        else:
            self.host = "Canceled"
        return appl
    def showDialog3(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 'port:')
        if appl == True:
            self.port =(str(text)) 
        else:
            self.port = "Canceled"
        return appl
    def showDialog4(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 'user:') 
        if appl==True:
            self.user =(str(text))
        else:
            self.user = "Canceled"
        return appl
    def showDialog5(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 'password:')
        if appl==True:
            self.password =(str(text))    
        else:
            self.password = "Canceled"
        return appl
    def showDialog6(self):     
        text, appl = QtGui.QInputDialog.getText(self, 'Input Dialog', 
                 'network name:')      
        if appl == True:
            self.network =(str(text))
        else:
            self.network = "Canceled"
        return appl
    """    
    def View(self):
        param1 = self.txtinput1.text() #size
        param2 = self.txtinput2.text()
        param3 = self.txtinput3.text() 
        G, param1, param2, param3 = self.buildNet(param1, param2, param3)
        if G == None:            
            return
        else:
            built = True
            fig = pl.gcf()
            self.method = self.showcombo()
            if self.method == 'Default(Random)':
                fig.canvas.set_window_title('Default visualisation')
                nx.draw(G,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
            elif self.method == 'Circle':
                nx.draw_circular(G,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Circle visualisation')
            elif self.method == 'Spring':
                nx.draw_spring(G,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Spring visualisation')
            elif self.method == 'Shell':
                nx.draw_shell(G,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Shell visualisation')
            elif self.method == 'Spectral':
                nx.draw_spectral(G,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Spectral visualisation')
            elif self.method == 'Circle Tree (bfs)':
                if param2 > 4:
                    QtGui.QMessageBox.information(self, 'Message', "Warning. This visulaisation may not appear as expected due to the high param 2 value.") 
                pos = vis.tree_circle(G, bfs = True)                
                nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Circle Tree (bfs) visualisation')
            elif self.method == 'Circle Tree (dfs)':
                if param2 > 4:
                    QtGui.QMessageBox.information(self, 'Message', "Warning. This visulaisation may not appear as expected due to the high param 2 value.") 
                pos = vis.tree_circle(G, bfs = False) 
                nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Circle Tree (dfs) visualisation')
            elif self.method == 'Tree (bfs)':
                pos = vis.tree(G, bfs=True)
                nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Tree (bfs) visualisation')
            elif self.method == 'Tree (dfs)':
                pos = vis.tree(G, bfs=False)
                nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Tree (dfs) visualisation')
            elif self.method == False:
                QtGui.QMessageBox.information(self, 'Message', "Visualisation process canceled.") 
                return
            else:
                print 'ERROR!'
            pl.show()
        return built
                    
    def showcombo(self):
        items = 'Default(Random)', 'Circle', 'Spring', 'Shell', 'Spectral', 'Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'
        method, ok = QtGui.QInputDialog.getItem(self, 'Input Dialog', 
            'Select visualisation method:', items)
        if ok == False:
            method = False
        return method
                  
    #this function is for the start button to run the analysis
    def RunAnalysis(self):
        self.lbl4.clear()
        QtGui.QApplication.processEvents() #refresh gui
        SINGLE = False
        SEQUENTIAL = False
        CASCADING = False
        RANDOM = False
        DEGREE = False
        BETWEENNESS = False
        REMOVE_SUBGRAPHS = False
        REMOVE_ISOLATES = False
        param1 = self.txtinput1.text() #size
        param2 = self.txtinput2.text()
        param3 = self.txtinput3.text() 

        if self.built == True:
            print self.G.number_of_nodes()
        else:
            G, param1, param2, param3 = self.buildNet(param1, param2, param3)
            if G == None:            
                return
         
        fileName = self.setFileLocation()
        if fileName == "": #if user clicks cancel, exits the routine
            QtGui.QMessageBox.information(self, 'Information', "Successfully ended process.")
            return
        
        if self.ckbx1.isChecked() and self.ckbx4.isChecked():
            SINGLE = True
            RANDOM = True
            self.lbl4.setText("Running single analysis with random node removal")
        elif self.ckbx1.isChecked() and self.ckbx5.isChecked():
            SINGLE = True
            DEGREE = True     
            self.lbl4.setText("Running single analysis with degree based node removal")
        elif self.ckbx1.isChecked() and self.ckbx6.isChecked():
            SINGLE = True
            BETWEENNESS = True
            self.lbl4.setText("Running single analysis with betweenness based node removal")
        elif self.ckbx2.isChecked() and self.ckbx4.isChecked():
            SEQUENTIAL = True
            RANDOM = True            
            self.lbl4.setText("Running sequential analysis with random node removal")
        elif self.ckbx2.isChecked() and self.ckbx5.isChecked():
            SEQUENTIAL = True
            DEGREE = True            
            self.lbl4.setText("Running sequential analysis with degree based node removal")
        elif self.ckbx2.isChecked() and self.ckbx6.isChecked():
            SEQUENTIAL = True
            BETWEENNESS = True            
            self.lbl4.setText("Running sequential analysis with betweenness based node removal")
        elif self.ckbx3.isChecked() and self.ckbx4.isChecked():
            CASCADING = True
            RANDOM = True            
            self.lbl4.setText("Running cascading analysis with random node removal")
        elif self.ckbx3.isChecked() and self.ckbx5.isChecked():
            CASCADING = True
            DEGREE = True            
            self.lbl4.setText("Running cascading analysis with degree based node removal")
        elif self.ckbx3.isChecked() and self.ckbx6.isChecked():
            CASCADING = True
            BETWEENNESS = True            
            self.lbl4.setText("Running cascading analysis with betweenness based node removal")
        else:
            self.lbl4.setText("Error in checking of check boxes.")
        
        self.lbl4.adjustSize()
        self.lbl4.show()
        QtGui.QApplication.processEvents() #refresh gui
        if self.ckbx16.isChecked():
            REMOVE_SUBGRAPHS = True
        if self.ckbx17.isChecked():
            REMOVE_ISOLATES = True
            
        parameters = SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, fileName
        #run code here call to external function/module 
        result, values = res.main(G,parameters)
        path_length_A, node_count_removed_A, isolated_n_count_A, averagedegree, numofcomponents = values
        #change the text in lbl4 here to say completed
        if result == True:
            self.lbl4.setText("Analysis Completed")     
            ok = QtGui.QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed." , '&OK','&View Graph')
            while ok == 1: #if the view graph option is clicked
                self.drawgraph(values)
            else:
                self.lbl4.setText("Analysis failed")            
        self.lbl4.adjustSize()
        
    def drawgraph(self, values):
        #get the two mtrics to display from the combobox window        
        inputdlg = pickparameters()
        if inputdlg.exec_():
            data = inputdlg.getval()
            return
        else:
             metric1, metric2 = inputdlg.getval()
        values = list(values)
        valuenames = 'average path length', 'nodes removed count','isolated nodes count','average degree', 'number of components' #list for the labels, needs updating manually
        #here add a call to a new window where the items to be displaye on the graph can be specified. Limit to two to make it easier to begin with anyway.
        fig = pl.gcf()
        fig.canvas.set_window_title('Results plot')
        one, two, three, four, five = values
        p1=pl.plot(values[metric1], 'b', linewidth=2, label=valuenames[metric1])
        if metric2<>99:
            p2=pl.plot(values[metric2], 'r', linewidth=2, label=valuenames[metric2])
        
        #p3=pl.plot(numofcomponents, 'y', linewidth=2, label='number of components')
        pl.xlabel('Number of iterations')              
        #pl.legend(bbox_to_anchor=(1.05, 1), loc=2, mode="expand",borderaxespad=0.)
        pl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)                
        pl.show() #in future have it work dynamically so can pick the results it displays from some check boxes
                
    def getdbparameters(self):
        dlg = dbconnect()
        if dlg.exec_():
            data =dlg.getval()
        else:
            print 'this does not work properly yet, but does work'
            self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = dlg.getval()
        return self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME
        
    def getdbnetwork(self):
        self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = self.getdbparameters()
        try:
            print self.DBNAME
            print self.HOST
            print self.PORT
            """
            self.DBNAME = 'inter_london'
            self.HOST = 'localhost'
            self.PORT = '5433'
            self.USER = 'postgres'
            self.PASSWORD = 'aaSD2011'
            self.NETNAME = 'power_lines'
            """            
            #connection = str('PG:dbname = ')+str(self.DBNAME)+str(" host='")+str(self.HOST)+str("' port='")+str(self.PORT)+str("' user='")+str(self.USER)+str("' password='")+str(self.PASSWORD)+str("'")   
            connection = str('PG:dbname = ')+self.DBNAME+str(" host='")+self.HOST+str("' port='")+self.PORT+str("' user='")+self.USER+str("' password='")+self.PASSWORD+str("'")   
            
            print 'connection: ', connection               
            conn = ogr.Open(connection)
            G = nx_pgnet.read(conn).pgnet(self.NETNAME)   #load in network from database and create networkx instance
            return G
        except:
            QtGui.QMessageBox.warning(self, 'Error!', "Could not connect to database and find the data. Please check your inputs and try again. The parameters were: \ndbname: "+self.DBNAME+"\nhost: "+self.HOST+"\nuser: "+self.USER+"\nport: " +self.PORT+"\npassword: "+self.PASSWORD+"\nnetwork: "+self.NETNAME,'&OK')
            dbconnect = False            
            return dbconnect 
    
    def buildNet(self, param1, param2, param3):
        #build network
        if self.ckbx7.isChecked(): #ws
            if param1 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            if param3 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                return            
            try:        
                param1 = int(param1)
            except:        
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return
            try:
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number of connected neighbours, is in an incorrect format.")
                return
            try:
                param3 = float(param3)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of rewiring, is in an incorrect format.")
                return
            if param2 >= param1:
                QtGui.QMessageBox.warning(self, 'Error!', "Input parameter 2 needs to be less than input parameter 1.")
                return
            if param3 <0 or param3 >1:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3 is an incorrect value.")
                return
            G = nx.watts_strogatz_graph(param1, param2, param3)
            if nx.is_connected(G)==False:
                #bring up error message box
                ok = QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase parameter 2 or decrease parameter 3.", '&OK')                  
                #would like to put a retry button on the message box, but not sure how we would know how to restart the analysis after doing this, as can be called from two places
                return #exit sub
        elif self.ckbx8.isChecked(): #gnm
            if param1 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return        
            try:
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            maxno = (param1)*(param1/2)
            if maxno < param2:
                QtGui.QMessageBox.warning(self, 'Warning!', "Warning. This network may have duplicate edges or edges which begin and end at the same node.")
            else:
                G = nx.gnm_random_graph(param1, param2)
                if nx.is_connected(G)==False:
                    #bring up error message box
                    QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                    return #exit sub
        elif self.ckbx9.isChecked(): #ba
            if param1 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return           
            try:
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            G = nx.barabasi_albert_graph(param1, param2)
            if nx.is_connected(G)==False:
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.ckbx10.isChecked(): #er
            if param1 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return            
            try:            
                param2 = float(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            if param2 <0 or param2 >1:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3 is an incorrect value.")
                return
            G = nx.erdos_renyi_graph(param1, param2)
            if nx.is_connected(G)==False:
                #bring up error message box
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.ckbx11.isChecked(): #database connection  -currently only allows a single network
            #G = self.checkconnection()
            G = self.getdbnetwork()
            if G == False:
                return
        elif self.ckbx12.isChecked(): #hr
            if param1 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            if param3 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                 return
            try:        
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return 
            try:
                param3 = float(param3)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of new edges, is in an incorrect format.")
                return
            G = customnets.hr(param1,param2,param3)
        elif self.ckbx13.isChecked(): #ahr
            if param1 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            if param3 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                 return                        
            try:          
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return 
            try:
                param3 = float(param3)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of new edges, is in an incorrect format.")
                return
            G = customnets.ahr(param1,param2,param3)
        elif self.ckbx14.isChecked(): #hc
            #param1 = level
            #param2 = square/tri
            if param1 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            try:          
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is in an incorrect format.")
                return  
            try:          
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2,the type of sructure, is in an incorrect format.")
                return   
            if param2 >= 2:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2,the type of sructure, is too high. It should be either 0 or 1.")
            
            if param2 == 0:
                if param1 == 0 or param1 >= 6:
                    QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is incorrect. Should be between 1 and 5.")
                else:
                    G = customnets.square(param1)
            elif param2 == 1:
                if param1 == 0 or param1 >= 5:
                    QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is incorrect. Should be between 1 and 4.")
                else:
                    G = customnets.tri(param1)
            else:
                print 'There has been an error'
           
        elif self.ckbx15.isChecked(): #trees
            #param 1 is the number of new nodes
            #param 2 is the number of level excluding the source
            if param1 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            try:        
                param1 = int(param1)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return  
            G=nx.balanced_tree(param1, param2)
        elif self.ckbx18.isChecked(): #list
            #param1 is a list of nodes  #param2 is a list of egdes
            #need to convert the input strings to lists with integers in the correct format
            if param1 =='' or param2=='':
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please enter node and edge lists or select a different option.")
                return #exit sub
            G = nx.Graph()
            param1 = replace_all(param1, {' ':'','[':'',']':'',')':'','(':''})
            param1 = param1.split(',')
            nodelist=[]            
            for item in param1:
                item = int(item)
                nodelist.append(item)
            try:
                G.add_nodes_from(nodelist)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. The node list does not fit the required format.")
                return #exit sub
            param2 = replace_all(param2, {')':'',']':'','[':'',' ':''}) #clean the list
            param2 = param2.split('(') #split the list (also removes them)
            edgelist = [] #crea teh new edges list
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
            print 'the edge list is: ', edgelist
            try:
                G.add_edges_from(edgelist)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. The edge list is not in the correct formart.")            
                return #exit sub
        else: 
            QtGui.QMessageBox.warning(self, 'Error!', "Error! Please try again.")          
            return #exit sub
        return G, param1, param2, param3

#method not working yet
#live drawing of the graph
def draw(G):
    mw = MainWindow
    print 'calling function'
    viewnet = mw.viewfailure(mw)
    if viewnet == True:
        print 'the box is checked'
        print 'it is drawing the graph'
        pl.cla()
        #positions = vis.tree_circle(G, bfs=True)
        nx.draw_circular(G, with_labels = False)
        #,cmap = PL.cm.jet, vmin = 0) node_color = [network.node[nd]['load'] for nd in network.nodes_iter()])
        #PL.title('t = ' + str(time))
        pl.show()
    elif viewnet == False:
        print 'it is false'
        sys.exitsub()
    print 'done everything else'
    
    
def replace_all(text, dic):
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text
        
def main():
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
   
if __name__ == '__main__':
    main()    
