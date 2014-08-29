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
import interdependency_analysis_v4_6 as res #this one needs updating/changing for the required setup
import inhouse_algorithms as customnets
import time
#from matplotlib.widgets import CheckButtons

figureModel = None
global valueset, forthread
valueset = 0

try:
    import osgeo.ogr as ogr
except:
    print 'ERROR! OGR cannot be found. There will be no database functionality.'    
sys.path.append('C:/a8243587_DATA/GitProjects/nx_pgnet')
try:
    import nx_pg, nx_pgnet
except:
    print 'ERROR! Cannot find nx_pg functions, thus there will be limited or no data base functionality.'

class ViewGraphs(QtGui.QDialog):   
    def __init__(self, parent=None):
        global valueset
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
        self.cancelbtn = QtGui.QPushButton('Close', self)
        self.cancelbtn.move(135, 80)
        self.cancelbtn.clicked.connect(self.cancelclick)
        #just need to sort this out so the variable values can be transfered into this class easily
        #attempt to get the metric values for the graphs from the mian window class

        self.values = valueset #converts global valueset into the self.values, which is the metric values to be displayed
        self.setGeometry(900,500,280,110)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Graph parameters')  #title of windpw          
        self.show()#show GUI window  
        
        self.figureGraph = pl.figure() #create the figure
        self.figureGraph = pl.gcf() #allow the title to be changed
        self.figureGraph.canvas.set_window_title('Results plot') #assign a title
        pl.ion() #make the plot interactive so the update process is easier
        pl.show() #this displays a blank plot which I then want the graph to be displayed in
        
    #may have to use a similar methodology to that used when trying to visualise the networks as they fail
    #all the code the displaying the results should possibly go in here, would mean that it will be easier to modify and make run smoother
    #the only effect this would havee is the appropraite parameters would need to be sent/got to this class.
    #would also mean when the apply button is clicked, would change the graphs without having to be closed and re-opened.
    #would appear much more dynamic, running off trigger functions.
    def applyclick(self):
        self.metric1 = self.option1.currentText()
        self.metric2 = self.option2.currentText()
        self.metric1 = self.identifymetric(self.metric1)
        self.metric2 = self.identifymetric(self.metric2)
        
        if self.metric1 == self.metric2:
            QtGui.QMessageBox.information(self, 'Warning','The same parameters have been selected for both options. Please change one.','&OK')
            return
        else:
            #need to get the values so this can work - means working on the other code before it even gets here            
            valuenames = 'average path length', 'nodes removed count','isolated nodes count','average degree', 'number of components' #list for the labels, needs updating manually
            self.values = list(self.values)
            one, two, three, four, five = self.values
            
            pl.cla() #clean the plot            
            p1=pl.plot(self.values[self.metric1], 'b', linewidth=2, label=valuenames[self.metric1])
            if self.metric2<>99:
                p2=pl.plot(self.values[self.metric2], 'r', linewidth=2, label=valuenames[self.metric2])            
            pl.xlabel('Number of iterations')
            pl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)                
            self.figureGraph.canvas.manager.window.update() #refresh the plot
            pl.show() #show a window
            
    def drawgraph(self, values):
        #get the two mtrics to display from the combobox window        
        inputdlg = ViewGraphs()
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
                    
    def cancelclick(self):
        self.close()            
        pl.close()
        
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
        
class DbConnect(QtGui.QDialog):    
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
        self.applybtn.move(170, 185)
        self.applybtn.adjustSize()
        self.applybtn.clicked.connect(self.savetext)
        
        self.cancelbtn = QtGui.QPushButton('Cancel', self)
        self.cancelbtn.move(10, 185)
        self.cancelbtn.adjustSize()
        self.cancelbtn.clicked.connect(self.cancel)

        self.restore = QtGui.QPushButton('Restore', self)
        self.restore.move(90, 185)
        self.restore.adjustSize()
        self.restore.clicked.connect(self.restoreinputs)

        self.setGeometry(300,500,250,220)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('db Connection Parameters')  #title of windpw          
        self.show()#show window   
     
    def savetext(self):
        global DBinputs
        self.DBNAME = self.txtinput1.text()
        self.HOST = self.txtinput2.text()
        self.PORT = self.txtinput3.text()
        self.USER = self.txtinput4.text()
        self.PASSWORD = self.txtinput5.text()        
        self.NETNAME = self.txtinput6.text()
        self.DBconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        DBinputs = self.DBconnect        
        self.close()
    
    def cancel(self):
        self.DBNAME = ''
        self.HOST = ''
        self.PORT = ''
        self.USER = ''
        self.PASSWORD = ''
        self.NETNAME = '' 
        self.close()
        
    def getval(self):
        return self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME
    
    def restoreinputs(self):
        global DBinputs
        if DBinputs == None:
            #when no inputs have been used suceesfully yet
            QtGui.QMessageBox.warning(self, 'Warning', "No inputs to restore. Inputs must have been used already before they can be restored." , '&OK')
        else:
            self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = DBinputs
            self.txtinput1.setText(self.DBNAME)
            self.txtinput2.setText(self.HOST)
            self.txtinput3.setText(self.PORT)
            self.txtinput4.setText(self.USER)
            self.txtinput5.setText(self.PASSWORD)         
            self.txtinput6.setText(self.NETNAME)

    def showdialog(self):     
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter your name:')      
        if ok:
            self.le.setText(str(text))
                
class ExtraParamWindow(QtGui.QWidget): # not sure if I will need this after all
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
        global DBinputs
        DBinputs = None
        self.first = True
        self.figureModel = None
        self.iterate = True
        self.timestep = 0
        self.cancel = False
        #self.failed = False
  
        
        #create actions for file menu
        RunAction = QtGui.QAction('&Run',self)
        RunAction.setShortcut('Ctrl+R')
        RunAction.setStatusTip('Run the selected analysis')
        RunAction.triggered.connect(self.runsim)       
        
        exitAction = QtGui.QAction('&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        exitAction.triggered.connect(self.closeall)

        extraAction = QtGui.QAction('&Extra', self)
        extraAction.setShortcut('Ctrl+P')
        extraAction.setStatusTip('Open extra parameter window')
        extraAction.triggered.connect(self.showepwindow)

        dbAction = QtGui.QAction('&DB Connection', self)
        dbAction.setShortcut('Ctrl+B')
        dbAction.setStatusTip('Open db connection properties')
        dbAction.triggered.connect(self.showdbwindow)
        
        openAction = QtGui.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load node and edge lists from .txt file')
        openAction.triggered.connect(self.openfile)
        
        self.built = False               
        viewnetAction = QtGui.QAction('&View Network', self)
        viewnetAction.setShortcut('Ctrl+D')
        viewnetAction.setStatusTip('View the network')
        self.built = viewnetAction.triggered.connect(self.view)               
    
        self.statusBar() #create status bar 
        menubar=self.menuBar() #create menu bar
        fileMenu = menubar.addMenu('&File') #add file menu
        editMenu = menubar.addMenu('&Edit') #add edit menu
        
        #add actions to file and edit menu's
        editMenu.addAction(RunAction)
        editMenu.addAction(viewnetAction)
        #editMenu.addAction(extraAction) #not need for the moment 
        editMenu.addAction(dbAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
  
        self.lbl4 = QtGui.QLabel("Ready", self)
        self.lbl4.move(68,153)
        self.lbl4.adjustSize() 
        fontbold = QtGui.QFont("Calibri", 10, QtGui.QFont.Bold)      

        self.lbl6 = QtGui.QLabel("STATE: ", self)
        self.lbl6.move(25,152)
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
        self.ckbx1.stateChanged.connect(self.ckbxoptionlimited)
        self.ckbx2 = QtGui.QCheckBox("Sequential",self)
        self.ckbx2.adjustSize()
        self.ckbx2.move(25,65) 
        self.ckbx2.setToolTip("Remove nodes one after each other until none are left")
        self.ckbx2.stateChanged.connect(self.ckbxoptionall)
        self.ckbx3 = QtGui.QCheckBox("Cascading",self)
        self.ckbx3.adjustSize()
        self.ckbx3.move(25,85)
        self.ckbx3.setToolTip("Remove a node, them all it's neighbours, then all of their neighbours etc,")
        self.ckbx3.stateChanged.connect(self.ckbxoptionall)
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
        #self.ckbx4.stateChanged.connect(self.labelupdate)
        self.ckbx4.toggle()
        self.ckbx5 = QtGui.QCheckBox("Degree", self)
        self.ckbx5.adjustSize()        
        self.ckbx5.move(130,65)
        self.ckbx5.setToolTip("Select the node with the highest degree")
        #self.ckbx5.stateChanged.connect(self.labelupdate)        
        self.ckbx6 = QtGui.QCheckBox("Betweenness", self)
        self.ckbx6.adjustSize()
        self.ckbx6.move(130,85) 
        self.ckbx6.setToolTip("Select the node with the highest betweenness value")
        #self.ckbx6.stateChanged.connect(self.labelupdate)
        Group2 = QtGui.QButtonGroup(self)     
        Group2.addButton(self.ckbx4)
        Group2.addButton(self.ckbx5)
        Group2.addButton(self.ckbx6)
        Group2.exclusive()
        #set when initated as not chackable as single is the defualt option
        self.ckbx5.setCheckable(False)
        self.ckbx6.setCheckable(False)
    
    
        self.lbl1 = QtGui.QLabel("Network Type", self)
        self.lbl1.setFont(fontbold)
        self.lbl1.adjustSize()
        self.lbl1.move(275, 25)
        
        self.graph = 'GNM' #means this is the default, so if menu option not changed/used, will persume GNM graph
        inputs = ('GNM','Erdos Renyi','Watts Strogatz','Barabasi Albert','Hierarchical Random','Hierarchical Random +','Hierarchical Communities','Tree','Database','Lists',)
        self.cmbox = QtGui.QComboBox(self)
        self.cmbox.move(275,40)
        self.cmbox.addItems(inputs)
        self.cmbox.activated[str].connect(self.cmbxselection)           
        
        self.lbl10 = QtGui.QLabel("Graph Inputs", self)
        self.lbl10.setFont(fontbold)
        self.lbl10.adjustSize()
        self.lbl10.move(400, 25)
        self.txtinput1 = QtGui.QLineEdit(self)        
        self.txtinput1.move(400, 45)
        self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM
        self.txtinput2 = QtGui.QLineEdit(self)
        self.txtinput2.move(400, 80)
        self.txtinput2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtinput3 = QtGui.QLineEdit(self)
        self.txtinput3.move(400, 115)
        self.txtinput3.setEnabled(False)        
          
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

        self.viewfailures = False
        self.ckbx19 = QtGui.QCheckBox("View net failure", self)
        self.ckbx19.adjustSize()
        self.ckbx19.move(275, 85)
        self.ckbx19.setToolTip("View the network failure as nodes are removed")
        self.ckbx19.stateChanged.connect(self.viewfailure) #not sure if needed as calls can be based on if the box is checked
        
        self.btn2 = QtGui.QPushButton('Draw', self)
        self.btn2.move(275, 150)
        self.btn1 = QtGui.QPushButton('Start', self)
        self.btn1.move(425, 150)
        self.built = self.btn2.clicked.connect(self.view) #view the network and set built as true
        #self.btn1.clicked.connect(self.runanalysis)     
        self.btn1.clicked.connect(self.runsim)        
        self.btn3 = QtGui.QPushButton('Step', self)
        self.btn3.move(350, 150)
        self.btn3.clicked.connect(self.stepanalysis)
        self.btn4 = QtGui.QPushButton('Reset/Cancel', self)
        self.btn4.move(200, 150)
        self.btn4.clicked.connect(self.reset)        
        self.btn4.adjustSize()
        self.btn3.adjustSize()
        self.btn2.adjustSize()
        self.btn1.adjustSize()
        self.setGeometry(300,300,515,185)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Resilience Analysis') #title of window 
        self.show() #show window
               
    def showepwindow(self):
        self.w = ExtraParamWindow()
        self.w.show()
    def showdbwindow(self):
        inputDlg = DbConnect(self)
        inputDlg.show() 
    def ckbxoptionlimited(self):
        'Set these two options as not checkable as there is only one option for single analysis.'
        self.ckbx5.setCheckable(False)
        self.ckbx6.setCheckable(False)
        self.ckbx5.setChecked(False)
        self.ckbx6.setChecked(False)
        self.ckbx4.setChecked(True)
        QtGui.QApplication.processEvents() #refresh gui
    def ckbxoptionall(self):
        'Set all check boxes as checkable.'
        self.ckbx5.setCheckable(True)
        self.ckbx6.setCheckable(True)
    def reset(self):
        print 'the reset button has been pressed'
        #this should be used for reseting all values and appropriate varables back to zero, meaning any current analysis is deleted
        self.first = True
        self.iterate = True
        self.built = False
        self.timestep = 0
        self.cancel = True
        
    def closeall(self):
        'Closes the other windows if they are open when Exit chosen from File menu.'
        pl.close() #closes the network visualisation window
        #need to add some more here
        
    def viewfailure(self):  #function to set state of variable for the visualising the network as it fails
        'Sets the viewfailure varaible based on if the appropraite checkbox is checked.'        
        #when the eternal module is called, would make sence to send the required variables for the visualisation method to the module        
        if self.ckbx19.isChecked():         
            self.viewfailures = True
        else:
            self.viewfailures = False
        
    def cmbxselection(self, text):
        'Alter the interface depending on what is selected in the combo box for graph type.'
        self.graph = text
        if text == 'GNM':
             self.txtinput3.setEnabled(False)
             self.txtinput1.setEnabled(True)
             self.txtinput2.setEnabled(True)
             self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
             self.txtinput2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389')   
        elif text == 'Erdos Renyi':
            self.txtinput3.setEnabled(False)
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
            self.txtinput2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
        elif text == 'Watts Strogatz':
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput3.setEnabled(True)
            self.txtinput1.setToolTip('The number of nodes. eg.,34 or 178')
            self.txtinput2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15')
            self.txtinput3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
        elif text == 'Barabasi Albert':
            self.txtinput3.setEnabled(False)
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
            self.txtinput2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6')
        elif text == 'Hierarchical Random':
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput3.setEnabled(True)
            self.txtinput1.setToolTip('The number of level. eg., 2 or 4')
            self.txtinput2.setToolTip('The number of children from each new node. eg., 2 or 6')
            self.txtinput3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Random +':
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput3.setEnabled(True)
            self.txtinput1.setToolTip('The number of nodes. eg., 34 or 178')
            self.txtinput2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6')
            self.txtinput3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
        elif text == 'Hierarchical Communities':
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput3.setEnabled(False)
            self.txtinput1.setToolTip('The number of levels. eg., 2 or 4 (max is 4)')
            self.txtinput2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
        elif text == 'Tree':
             self.txtinput1.setEnabled(True)
             self.txtinput2.setEnabled(True)
             self.txtinput3.setEnabled(False)
             self.txtinput1.setToolTip('The number of child nodes per parent. eg., 3 or 5')
             self.txtinput2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6')
        elif text == 'Database':
            self.txtinput1.setEnabled(False)
            self.txtinput2.setEnabled(False)
            self.txtinput3.setEnabled(False)
        elif text == 'Lists':   
            self.txtinput1.setEnabled(True)
            self.txtinput2.setEnabled(True)
            self.txtinput3.setEnabled(False)
            self.txtinput1.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
            self.txtinput2.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')

    def openfile(self):
        'Function for opening a text file and adding the lists to the input boxes on the GUI.'
        print 'needs finishing, needs adjusting so the combobox will display the Database entry' #this needs adjusting so the combobox will display the Database entry
        #need something here which tells the combobox it has been changed to lists option, or add a add file option 
        #not sure I can actually do this though. could have message box to tell user to select lists
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        text=open(fname).read()
        text1, text2 = text.split('\n')
        self.txtinput1.setText(text1)
        self.txtinput2.setText(text2)
        #load in a csv, add lists to text boxes, then select lists for the input                  
        
    def setfilelocation(self):
        'Set the file location for the output file.'
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        return fileName

    def view(self):
        'Function to view the network using the range of options. Activated through the draw button or the draw menu option.'
        param1 = self.txtinput1.text() 
        param2 = self.txtinput2.text()
        param3 = self.txtinput3.text() 
        G, param1, param2, param3 = self.buildnet(param1, param2, param3)
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
                #if param2 > 4:
                #    QtGui.QMessageBox.information(self, 'Message', "Warning. This visulaisation may not appear as expected due to the high param 2 value.") 
                pos = vis.tree_circle(G, bfs = True)                
                nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
                fig.canvas.set_window_title('Circle Tree (bfs) visualisation')
            elif self.method == 'Circle Tree (dfs)':
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
        'Loads a GUI where the use selects the method of positioning the nodes.'
        items = 'Default(Random)', 'Circle', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'
        method, ok = QtGui.QInputDialog.getItem(self, 'Input Dialog', 
            'Select visualisation method:', items)
        if ok == False:
            method = False
        return method
                      
    def runsim(self):
        'Runs the analysis in one go, initiated by the start button. Also allows for the cancel button to work.'
        self.cancel = False #set as false as this will allow the analysis to run
        #if self.failed == False:
        while self.iterate == True:
            if self.cancel == False:
                self.stepanalysis()
            else:
                self.lbl4.setText("Ready - Analysis Canceled") #changes the text in the GUI   
                self.lbl4.adjustSize()
                QtGui.QApplication.processEvents() #refresh gui
                return
                self.iterate = False
                
    def analysisfinished(self,result, values):        
        'When the analysis finished, displays the GUI with the next option to view the metric graphs.'        
        global valueset
        self.reset()
        if result == True:
            self.lbl4.setText("Analysis Completed") #changes the text in the GUI   
            self.lbl4.adjustSize()
            QtGui.QApplication.processEvents() #refresh gui
            ok = QtGui.QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed. Do you want to view the metric graphs?" , '&No','&View Graphs')
            if ok == 1: #if the view graph option is clicked
                valueset= self.values
                inputdlg = ViewGraphs()
                inputdlg()
        else:
            self.lbl4.setText("Analysis failed")            
        self.lbl4.adjustSize()

    #function which will run the analysis one step at a time
    def runstep(self, graphparameters, parameters, iterate):
        'Run the analysis.'
        graphparameters, iterate = res.step(graphparameters, parameters, iterate)
        return graphparameters, iterate

    def stepanalysis(self):
        'Activated by the step button. Runs one step of analysis.'
        self.lbl4.setText("Processing")
        self.lbl4.adjustSize()
        QtGui.QApplication.processEvents() #refresh gui
        self.cancel = False
        active = 1
        inactive = 0
        global forthread
        #if i can make this step button work, thenI might be able to get some of the visualisations to work at least for this method
        #need to set this button as in active until the run button has been clicked, or some way of idetifying if the inital core function needs executing
        #once that is done then the runstep function obe can be exeuted as needed along with the other required code        
        #easier to create a global variable whoch can be used to store if the run button has been clicked
        #this is by no means anywhere near perfect but should work
        #will also need resetting when the analysis finishes ie. when iterate = False
        if self.first == True:          
            self.lbl4.setText("Initiating")
            self.lbl4.adjustSize()
            QtGui.QApplication.processEvents() #refresh gui
            param1 = self.txtinput1.text() 
            param2 = self.txtinput2.text()
            param3 = self.txtinput3.text() 
    
            if self.built == True:
                print self.G.number_of_nodes()
            else:
                self.G, param1, param2, param3 = self.buildnet(param1, param2, param3)
                if self.G == None:            
                    return                
            
            self.parameters = self.checkanalysistype() #get the type of analysis to be performed
            if self.nofilename == True:
                return
            #network and variables included in graphparameters                      
            self.graphparameters = res.core_analysis(self.G)    
            forthread = self.graphparameters, self.parameters, self.iterate

            if self.ckbx19.isChecked():
                 #this line will also have to change to accomodate the user chosing a layout for the visualisation
                 selected = self.showcombo() 
                 #need the relavnt method here to identify the option which is selected and use of in the nx.draw line
                 self.getpositions(selected)
                 #self.positions = nx.circular_layout(self.G) #assign the positions for the drawing of the network
                 #copy the network
                 self.graphviz = self.G.copy()
                 #add a new atrribute and set as active            
                 for node in self.graphviz.nodes_iter():
                    self.graphviz.node[node]['state'] = active
                 self.lbl4.setText("Drawing")
                 self.lbl4.adjustSize()
                 QtGui.QApplication.processEvents() #refresh gui
                 self.figureModel, self.timestep = draw(self.graphviz, self.positions, self.figureModel, self.timestep)
            self.first = False #keep this at the end of the if
        else:
            self.graphparameters, self.parameters, self.iterate = forthread
            forthread = self.graphparameters, self.parameters, self.iterate
            self.workThread = WorkThread() #name workthread

            if self.iterate == True: #self.iterate used to be part of a global variable
                self.connect(self.workThread, QtCore.SIGNAL("self.forthread[list]"), self.runstep)
                self.workThread.start()
                time.sleep(1) #still need some changes here so can get rid of this sleep bit
                if self.ckbx19.isChecked(): #would appear that the visualisation is current but I'm not 100% sure this is correct                               
                    removednodes = set(self.graphviz.nodes()) - set(self.G.nodes()) #need to convert to sets as lists cannot be subtracted
                    print 'the removed nodes are: ', removednodes
                    for node in removednodes: #set the state to inactive for relavant nodes 
                        self.graphviz.node[node]['state'] = inactive 
                    self.lbl4.setText("Drawing")
                    self.lbl4.adjustSize()
                    QtGui.QApplication.processEvents() #refresh gui
                    self.figureModel, self.timestep = draw(self.graphviz, self.positions, self.figureModel, self.timestep)
            elif self.iterate == False: #when the iterate variable changes to False, which means the analysis has finished
                self.values = res.outputresults(self.graphparameters, self.parameters)        
                path_length_A, node_count_removed_A, isolated_n_count_A, averagedegree, numofcomponents = self.values
                result = True #This should come from the analysis module at some point to confirm the analysis has been successfull        
                self.analysisfinished(result, self.values)
                self.iterate = False
            else:
                 print 'Critical error somewhere!' #never seen this so no worries here   
        self.lbl4.setText("Ready")
        self.lbl4.adjustSize()
        QtGui.QApplication.processEvents() #refresh gui
    
    def getpositions(self, selected):
        'Default(Random)', 'Circle', 'Spring', 'Shell', 'Spectral', 'Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'
        if selected == 'Default(Random)':
            self.positions=nx.random_layout(self.G)
        elif selected == 'Circle':
            self.positions=nx.circular_layout(self.G)
        elif selected == 'Spring':
            self.positions=nx.spring_layout(self.G)
        elif selected == 'Shell':
            self.positions=nx.shell_layout(self.G)
        elif selected == 'Spectral':
            self.positions=nx.spectral_layout(self.G)
        elif selected == 'Circle Tree (bfs)':
            bfs = True
            self.positions=vis.tree_circle(self.G, bfs)
        elif selected == 'Circle Tree (dfs)':
            bfs = False
            self.positions=vis.tree_circle(self.G, bfs)
        elif selected == 'Tree (dfs)':
            bfs = False
            self.positions=vis.tree(self.G, bfs)
        elif selected == 'Tree (bfs)':
            bfs = True
            self.positions=vis.tree(self.G, bfs)
        else:
            print 'Error in the selection of vis method'

    def checkanalysistype(self):
        'Get the analysis type, the file location and if any of the other options have been selected related to the analysis if the network.'
        SINGLE = False
        SEQUENTIAL = False
        CASCADING = False
        RANDOM = False
        DEGREE = False
        BETWEENNESS = False
        REMOVE_SUBGRAPHS = False
        REMOVE_ISOLATES = False
        
        fileName = self.setfilelocation()
        if fileName == "": #if user clicks cancel, exits the routine
            QtGui.QMessageBox.information(self, 'Information', "Successfully ended process.")
            self.nofilename = True            
            return
        else:
            self.nofilename = False
            if self.ckbx1.isChecked() and self.ckbx4.isChecked():
                SINGLE = True
                RANDOM = True
                #self.lbl4.setText("Running single analysis with random node removal")
            elif self.ckbx1.isChecked() and self.ckbx5.isChecked():
                SINGLE = True
                DEGREE = True     
                #self.lbl4.setText("Running single analysis with degree based node removal")
            elif self.ckbx1.isChecked() and self.ckbx6.isChecked():
                SINGLE = True
                BETWEENNESS = True
                #self.lbl4.setText("Running single analysis with betweenness based node removal")
            elif self.ckbx2.isChecked() and self.ckbx4.isChecked():
                SEQUENTIAL = True
                RANDOM = True            
                #self.lbl4.setText("Running sequential analysis with random node removal")
            elif self.ckbx2.isChecked() and self.ckbx5.isChecked():
                SEQUENTIAL = True
                DEGREE = True            
                #self.lbl4.setText("Running sequential analysis with degree based node removal")
            elif self.ckbx2.isChecked() and self.ckbx6.isChecked():
                SEQUENTIAL = True
                BETWEENNESS = True            
                #self.lbl4.setText("Running sequential analysis with betweenness based node removal")
            elif self.ckbx3.isChecked() and self.ckbx4.isChecked():
                CASCADING = True
                RANDOM = True            
                #self.lbl4.setText("Running cascading analysis with random node removal")
            elif self.ckbx3.isChecked() and self.ckbx5.isChecked():
                CASCADING = True
                DEGREE = True            
                #self.lbl4.setText("Running cascading analysis with degree based node removal")
            elif self.ckbx3.isChecked() and self.ckbx6.isChecked():
                CASCADING = True
                BETWEENNESS = True            
                #self.lbl4.setText("Running cascading analysis with betweenness based node removal")
            else:
                self.lbl4.setText("Error")
            
            self.lbl4.adjustSize()
            self.lbl4.show()
            QtGui.QApplication.processEvents() #refresh gui
            if self.ckbx16.isChecked():
                REMOVE_SUBGRAPHS = True
            if self.ckbx17.isChecked():
                REMOVE_ISOLATES = True
                
            parameters = SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, fileName
            return parameters
              
    def getdbparameters(self):
        'Open the GUI for the user to input the database connection parameters. This needs looking at as works, but not as intended. Could thus do with cleaning up.'
        self.failed = False        
        dlg = DbConnect()
        if dlg.exec_():
            data =dlg.getval()
        else:
            print 'this does not work properly yet, but does work. could replace with the global parameter though.'
            self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = dlg.getval()
        if self.NETNAME == '':
            self.failed = True
            return 
        else:
            return 
        
    def getdbnetwork(self):
        'Connect to the database and pull the network into the system.'
        self.getdbparameters()
        if self.failed == False:           
            try:
                #needed to convert the items to strings for the connection
                self.DBNAME = str(self.DBNAME)
                self.HOST = str(self.HOST)
                self.PORT = str(self.PORT)
                self.USER = str(self.USER)
                self.PASSWORD = str(self.PASSWORD)
                self.NETNAME = str(self.NETNAME)              
                
                """ paramers for a safe conenction that should always work
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
        else:
            self.cancel = True
            return
    def buildnet(self, param1, param2, param3):
        'Build the network given the input parametrs.'
        #build network
        if self.graph == 'Watts Strogatz': #ws 
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
        elif self.graph == 'GNM': #gnm
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
            '''
            maxno = (param1)*(param1/2)
            if maxno < param2:
                QtGui.QMessageBox.warning(self, 'Warning!', "Warning. This network may have duplicate edges or edges which begin and end at the same node.")
                #sys.exitfunc() 
                return
            else:
            '''
            G = nx.gnm_random_graph(param1, param2)
            if nx.is_connected(G)==False:
                #bring up error message box
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.graph == 'Barabasi Albert': #ba
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
        elif self.graph == 'Erdos Renyi': #er
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
                QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 2 is an incorrect value.")
                return
            G = nx.erdos_renyi_graph(param1, param2)
            if nx.is_connected(G)==False:
                #bring up error message box
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.graph == 'Database': #database connection  -currently only allows a single network
            G = self.getdbnetwork()
            if G == None:
                print 'G = NONE AGAIN'
                return
        elif self.graph == 'Hierarchical Random': #hr
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
        elif self.graph=='Hierarchical Random +': #ahr
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
        elif self.graph == 'Hierarchical Communities': #hc
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
           
        elif self.graph == 'Tree': #trees
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
        elif self.graph == 'Lists': #list
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
        self.G = G
        print G.number_of_nodes()
        return G, param1, param2, param3   
    
class WorkThread(QtCore.QThread): #create the worker thread, where the sresilience analysis will be run
    def __init__(self): #initiate the thread
        QtCore.QThread.__init__(self)
        
    def run(self): #run the thread
        'Run the analysis on a second thread to help stop the GUI freezing.'
        global valueset, forthread
        graphparameters, parameters, iterate = forthread
        print 'this is the work thread'#this is where the code to run the thread should go I think
        #need to put in the method to call the step code here
        graphparameters, iterate = res.step(graphparameters, parameters, iterate) #run one step of the analysis
        print 'the value set in the workthread is', valueset
        print 'iterate in the work thread is: ', iterate
        forthread = graphparameters, parameters, iterate
        #self.emit( QtCore.SIGNAL('forthread[list]'), "from work thread " + str(forthread) )
        #them some signal to tranfer messages and data to the main application

#live drawing of the graph
def draw(G, positions, figureModel, timestep):
    'Handles the initial setup parameters for drawing the network as well as then calling the function to draw the network'
    if figureModel == None or figureModel.canvas.manager.window == None:
        figureModel = pl.figure()
        pl.ion()
        pl.show()
    print 'drawing the graph, figure model = ', figureModel
    drawnet(G, positions, timestep)
    timestep+=1
    figureModel.canvas.manager.window.update()  #gets error here when the window is closed by whatever means
    return figureModel, timestep
      

def drawnet(G, positions, timestep):
    'Draws the network'
    inactivenodes=[]
    activenodes=[]
    inactiveedges=[]
    activeedges=[]
    pl.cla()
    #cheat way of removing the axis and labels in two lines
    g1 = nx.Graph() 
    nx.draw(g1)
    nx.draw_networkx_nodes(G, positions, node_color = 'g')
    nx.draw_networkx_edges(G, positions, edge_width=6, edge_color = 'g')
    
    pl.title('iteration = ' + str(timestep))
    timestep+=1
    for node in G.nodes_iter():
        if G.node[node]['state'] == 0: #inactive
            inactivenodes.append(node)
            edgelist = G.edges(node)
            nx.draw_networkx_edges(G, positions, edge_width=6.1, edgelist = edgelist, edge_color = 'r')
        elif G.node[node]['state']== 1: #active
            activenodes.append(node)
            edgelist = G.edges(node)
            #nx.draw_networkx_edges(G, positions, edgelist = edgelist, edge_width = 7,edge_color = 'r')
            #activeedges.append(G.edges(node))
    
    #nx.draw(G,positions,node_size=20,alpha=0.5,node_color="blue", with_labels=False) #this is the original method
    #nx.draw(G, positions, nodelist = activenodes, node_color = 'r')#, with_labels=False)
    #nx.draw(G, positions, nodelist = inactivenodes, node_color = 'b')#, with_labels=False)
    #nx.draw_networkx_nodes(G, positions, nodelist = activenodes, node_color = 'g')
    nx.draw_networkx_nodes(G, positions, nodelist = inactivenodes, node_color = 'r')    
    #nx.draw_networkx_edges(G, positions, edgelist = inactiveedges, edge_color = 'b')
    #nx.draw_networkx_edges(G, positions, edgelist = activeedges, edge_color = 'r')

def replace_all(text, dic):
    'Used to modify strings to make them suitable for purpose.'
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text
        
def main():
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
   
if __name__ == '__main__':
    main()    
