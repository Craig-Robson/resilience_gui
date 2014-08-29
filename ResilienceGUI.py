# -*- coding: utf-8 -*-
"""
This is the script file for the whole GUI which can vusaliase networks and also
 run a range of resileince models over any network which imported/created.




Need to add a whole lot of stuff here about the code, what it does and how to use it. Less important now that GUI works though.


"""

import sys
from PyQt4 import QtGui, QtCore
#import networkx as nx
import pylab as pl
import matplotlib as mp
import visalgorithms_v10_1 as vis
import interdependency_analysis_v5_0_1 as res #this one needs updating/changing for the required setup
import inhouse_algorithms as customnets
import time
#from matplotlib.widgets import CheckButtons #could be used but appears on outputs so not worth it
global valueset, forthread, timedelay
figureModel = None
valueset = 0
sys.path.append('C:/a8243587_DATA/GitProjects/nx_pgnet')

try:
    import osgeo.ogr as ogr
except:
    #QtGui.QMessageBox.warning(self,'Error!', "Could not import the osgeo.ogr library. There will be no database connectivity as a result.")
    pass
try:
    import nx_pg, nx_pgnet
except:
    #QtGui.QMessageBox.warning('Error!', "Could not import nx_pg or nx_pgnet. There will be no database connectivity as a result.")
    pass
try:
    import networkx as nx
except:
    #QtGui.QMessageBox.warning('Error!', "Could not import networkx. The application cannot work without this.")
    pass

class ViewGraphs(QtGui.QDialog):   
    "Class for the window which allows the viewing of the results in terms of the graph metrics."
    def __init__(self, parent=None):
        global valueset
        QtGui.QDialog.__init__(self, parent)  
        self.figureGraph = None
        self.lblop1 = QtGui.QLabel('Plot 1:', self)
        self.lblop1.adjustSize()
        self.lblop1.move(25, 28)        
        self.option1 = QtGui.QComboBox(self)
        self.metriclist=['Average path length', 'Number of components', 'Average degree', 'Nodes count removed', 'Isolated node count', 'Number of isolates', 'None']
        self.option1.addItems(self.metriclist)
        self.option1.move(90, 25)
        self.lblop2 = QtGui.QLabel('Plot 2:', self)
        self.lblop2.adjustSize()
        self.lblop2.move(25, 58) 
        self.option2 = QtGui.QComboBox(self)
        self.option2.addItems(self.metriclist)      
        self.option2.move(90, 55)
        self.applybtn = QtGui.QPushButton('Apply', self)
        self.applybtn.setToolTip('View the selected metrics')
        self.applybtn.move(55, 80)
        self.applybtn.clicked.connect(self.applyclick)
        self.cancelbtn = QtGui.QPushButton('Close', self)
        self.cancelbtn.setToolTip('Close the window')        
        self.cancelbtn.move(135, 80)
        self.cancelbtn.clicked.connect(self.cancelclick)

        self.option1.activated[str].connect(self.option1changed)             
        self.option2.activated.connect(self.option2changed)
        #just need to sort this out so the variable values can be transfered into this class easily
        #attempt to get the metric values for the graphs from the mian window class

        self.values = valueset #converts global valueset into the self.values, which is the metric values to be displayed
        self.setGeometry(900,500,280,110)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Graph parameters')  #title of windpw          
        self.show()#show GUI window  
        self.option1value = 0        
        self.option2value = 1
        
        self.figureGraph = pl.figure() #create the figure
        self.figureGraph = pl.gcf() #allow the title to be changed
        self.figureGraph.canvas.set_window_title('Results plot') #assign a title
        pl.ion() #make the plot interactive so the update process is easier
        pl.show() #this displays a blank plot which I then want the graph to be displayed in
        self.option2.removeItem(self.option1value)
        self.option1.removeItem(self.option2value)
        self.applyclick()
        
    def option1changed(self):
        '''Update the option in combo box 2 and draw the graph.'''
        #clear the list in box 2
        self.option2.clear()
        #add all option back to the list2
        self.option2.addItems(self.metriclist)
        #set option 2 to what it was on before
        self.option2.setCurrentIndex(self.option2value)
        #get the position for the data 
        self.option1value = self.identifymetric(self.option1.currentText()) #get metric index for data list
        self.option2.removeItem(self.option1value)     
        self.applyclick()
        
    def option2changed(self):
        '''Update the options in combo box 1 and draw the graph.'''
        self.option1.clear()
        self.option1.addItems(self.metriclist)
        self.option1.setCurrentIndex(self.option1value)
        #get the position value for data in its list of lists
        self.option2value = self.identifymetric(self.option2.currentText()) #get metric index for data list
        #remove the item from box1 selected in box2
        self.option1.removeItem(self.option2value)
        self.applyclick()
        
    def applyclick(self):
        '''Runs the code to identify the metrics requested for the visualisation.'''
        #self.metric1 = self.option1.currentText()
        #self.metric2 = self.option2.currentText()
        #self.metric1 = self.identifymetric(self.metric1)
        #self.metric2 = self.identifymetric(self.metric2)
        self.metric1 = self.option1value
        self.metric2 = self.option2value
        #if self.metric1 == self.metric2:
            #QtGui.QMessageBox.information(self, 'Warning','The same parameters have been selected for both options. Please change one.','&OK')
            #return
        #else:
        #need to get the values so this can work - means working on the other code before it even gets here            
        self.valuenames = 'average path length', 'number of components', 'average degree','nodes removed count','isolates removed',  'number of isolates' #list for the labels, needs updating manually
        self.values = list(self.values)
        #one, two, three, four, five, six = self.values          
        
        if self.figureGraph == None or self.figureGraph.canvas.manager.window == None: #if figure model window has not been opened yet
            self.figureGraph = pl.figure()
            pl.ion()
            pl.show()  
        #need this in case the user closes the window 
        try:
            self.figureGraph.canvas.set_window_title('Results plot') 
        except:
            self.figureGraph = None
            self.figureGraph = pl.figure()
            self.figureGraph.canvas.set_window_title('Results plot') 
        
        pl.subplot(211)
        pl.cla() #clear the plot   
        pl.plot(self.values[self.metric1], 'b', linewidth=2, label=self.valuenames[self.metric1])
        pl.xlabel('Number of nodes removed')

        print 'option 1 says: ', self.option1.currentText()
        print 'option 2 says: ', self.option2.currentText()
        pl.ylabel(self.option1.currentText())
        pl.subplot(212)    
        pl.cla()
        if self.metric2<>99:
            pl.plot(self.values[self.metric2], 'r', linewidth=2, label=self.valuenames[self.metric2])            
        pl.xlabel('Number of nodes removed')
        pl.ylabel(self.option2.currentText())            
        #self.figureGraph.canvas.manager.window.update() #refresh the plot
        #pl.canvas.set_window_title('Results plot')
        pl.show() #show a window 

    def cancelclick(self):
        '''Close the slection box and graph window when the cancel button is clicked.'''
        self.close()            
        pl.close()
        
    def getval(self):
        '''Used to pass varaibles between classes.'''
        return self.metric1, self.metric2

    def closeEvent(self, event):
        pl.close()

    def identifymetric(self, metric):
        '''Method to idenitfy the metric requested, and assign the correct value for the position of its data in the lists of lists.'''
        if metric == 'Average path length':
            metric = 0
        elif metric == 'Number of components':
            metric = 1
        elif metric == 'Average degree':
            metric = 2
        elif metric == 'Nodes count removed':
            metric = 3
        elif metric == 'Isolated node count':
            metric = 4
        elif metric == 'Number of isolates':
            metric = 5
        elif metric == 'None': #this should never happen
            metric = 99
        else:
            print 'Uncategorised'
        return metric
        
class DbConnect(QtGui.QDialog):    
    '''Class for the database parameters connection window.'''
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
        self.applybtn.setToolTip('Connect to the database and run the analysis')
        self.applybtn.move(170, 185)
        self.applybtn.adjustSize()
        self.applybtn.clicked.connect(self.savetext)
        
        self.cancelbtn = QtGui.QPushButton('Cancel', self)
        self.cancelbtn.setToolTip('Cancel the analysis and close the window')
        self.cancelbtn.move(10, 185)
        self.cancelbtn.adjustSize()
        self.cancelbtn.clicked.connect(self.cancel)

        self.restore = QtGui.QPushButton('Restore', self)
        self.restore.setToolTip('Restore the settings from the previous successful analyiss this session')
        self.restore.move(90, 185)
        self.restore.adjustSize()
        self.restore.clicked.connect(self.restoreinputs)

        self.setGeometry(300,500,250,220)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('db Connection Parameters')  #title of windpw          
        self.show()#show window   
     
    def savetext(self):
        '''Save the text from that was in the text boxes when function called.'''
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
        '''Clear the text boxes and close the window when the cancel button is clicked.'''
        self.DBNAME = ''
        self.HOST = ''
        self.PORT = ''
        self.USER = ''
        self.PASSWORD = ''
        self.NETNAME = '' 
        self.close()
        
    def getval(self):
        '''Used to pass data between classes.'''
        return self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME
    
    def restoreinputs(self):
        '''Restore the previusoly saved vlaues from the last successful execution of the database connection. Data is retireved from a global variable.'''
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

                
class ExtraParamWindow(QtGui.QWidget): # not sure if I will need this after all
    def __init__(self):  
        QtGui.QWidget.__init__(self)
        self.initUI()
        
    def initUI(self):
        global timedelay
        self.lbltimedelay = QtGui.QLabel("Time(secs) between iterations: ",self)
        self.lbltimedelay.move(15,25)
        self.lbltimedelay.adjustSize()
        self.txttimedelay = QtGui.QLineEdit(self) 
        self.txttimedelay.move(170,22)
        self.txttimedelay.setFixedWidth(50)
        self.txttimedelay.setText(str(timedelay))
        self.txttimedelay.setToolTip('The minimum time(seconds) between iterations. Min = 0, Max = 300')        
        self.validator = QtGui.QIntValidator(0,300,self.txttimedelay)       
        self.txttimedelay.setValidator(self.validator)
        
        self.apply = QtGui.QPushButton("Apply", self)
        self.apply.adjustSize()
        self.apply.move(145,50)
        self.apply.clicked.connect(self.applyandclose)
                
        self.setGeometry(300,500,230,80) #above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Parameter Window') #title of window  
        self.show()#show window  

    def applyandclose(self):
        global timedelay
        timedelay = int(self.txttimedelay.text())
        self.close()
        
class MainWindow(QtGui.QMainWindow):
                
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        global DBinputs, figureModel, timedelay
        #here to save having to type them in every time at the moment
        self.DBNAME = 'inter_london'
        self.HOST = 'localhost'
        self.PORT = '5433'
        self.USER = 'postgres'
        self.PASSWORD = 'aaSD2011'        
        self.NETNAME = 'power_lines'
        DBinputs = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        
        self.threadPool = []
        figureModel = None
        self.first = True
        self.figureModel = None
        self.iterate = True
        self.timestep = 0
        self.cancel = False
        self.positions = None
        timedelay = 2
        self.pausetime = timedelay
        
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
        
        resetAction = QtGui.QAction('&Cancel/Reset', self)
        resetAction.setStatusTip('Cancel the analysis')
        resetAction.triggered.connect(self.reset)
        
        clearAction = QtGui.QAction('&Clear inputs', self)
        clearAction.setShortcut('Ctrl+E')
        clearAction.setStatusTip('Clear the input text boxes')
        clearAction.triggered.connect(self.clear)
        
        self.built = False               
        viewnetAction = QtGui.QAction('&View Network', self)
        viewnetAction.setShortcut('Ctrl+D')
        viewnetAction.setStatusTip('View the network')
        self.built = viewnetAction.triggered.connect(self.viewnet)               
    
        self.statusBar() #create status bar 
        menubar=self.menuBar() #create menu bar
        fileMenu = menubar.addMenu('&File') #add file menu
        editMenu = menubar.addMenu('&Edit') #add edit menu
        
        #add actions to file and edit menu's
        editMenu.addAction(RunAction)
        editMenu.addAction(viewnetAction)
        editMenu.addAction(resetAction)
        editMenu.addAction(extraAction) #not need for the moment 
        #editMenu.addAction(dbAction)
        editMenu.addAction(clearAction)
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
        self.ckbx4.toggle()
        self.ckbx5 = QtGui.QCheckBox("Degree", self)
        self.ckbx5.adjustSize()        
        self.ckbx5.move(130,65)
        self.ckbx5.setToolTip("Select the node with the highest degree")
        self.ckbx6 = QtGui.QCheckBox("Betweenness", self)
        self.ckbx6.adjustSize()
        self.ckbx6.move(130,85) 
        self.ckbx6.setToolTip(
        "Select the node with the highest betweenness value")
        Group2 = QtGui.QButtonGroup(self)     
        Group2.addButton(self.ckbx4)
        Group2.addButton(self.ckbx5)
        Group2.addButton(self.ckbx6)
        Group2.exclusive()
        #set when initated as not chackable as single is the defualt option
        self.ckbx5.setEnabled(False)
        self.ckbx6.setEnabled(False)
    
        self.lbl1 = QtGui.QLabel("Network Type", self)
        self.lbl1.setFont(fontbold)
        self.lbl1.adjustSize()
        self.lbl1.move(275, 25)
        
        self.graph = 'GNM' #means this is the default, so if menu option not changed/used, will persume GNM graph
        inputs = ('GNM','Erdos Renyi','Watts Strogatz','Barabasi Albert',
                  'Hierarchical Random','Hierarchical Random +',
                  'Hierarchical Communities','Tree','Database','Lists',)
        self.cmbox = QtGui.QComboBox(self)
        self.cmbox.move(275,40)
        self.cmbox.addItems(inputs)
        self.cmbox.setToolTip("Select the graph type or graph input method")
        self.cmbox.activated[str].connect(self.networkselection)           
        
        self.lbl10 = QtGui.QLabel("Graph Inputs", self)
        self.lbl10.setFont(fontbold)
        self.lbl10.adjustSize()
        self.lbl10.move(400, 25)
        self.txtparam1 = QtGui.QLineEdit(self)        
        self.txtparam1.move(400, 45)
        self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM        
        self.txtparam2 = QtGui.QLineEdit(self)
        self.txtparam2.move(400, 80)
        self.txtparam2.setToolTip(
        'The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtparam3 = QtGui.QLineEdit(self)
        self.txtparam3.move(400, 115)
        self.txtparam3.setEnabled(False)        
          
        self.lbl5 = QtGui.QLabel("Remove subgraphs/isolated nodes", self)
        self.lbl5.setFont(fontbold)
        self.lbl5.adjustSize()
        self.lbl5.move(25,105)
        self.ckbxsubgraphs = QtGui.QCheckBox("Subgraphs", self)  
        self.ckbxsubgraphs.adjustSize()
        self.ckbxsubgraphs.move(25, 120)
        self.ckbxsubgraphs.setToolTip(
        "Select if subgraphs are to be removed when they appear in the network")
        self.ckbxisolates = QtGui.QCheckBox("Isolates", self)
        self.ckbxisolates.adjustSize()
        self.ckbxisolates.move(130, 120)
        self.ckbxisolates.setToolTip(
        "Select if nodes are to be removed when they become isolated")
        self.ckbxnoisolates = QtGui.QCheckBox("Exclude isolates", self)
        self.ckbxnoisolates.adjustSize()
        self.ckbxnoisolates.move(235, 120)
        self.ckbxnoisolates.setToolTip("Tick if nodes, one isolated, should not be selected for removal when running resilience analysis")
        self.ckbxisolates.stateChanged.connect(self.limitoptions)

        self.viewfailures = False
        self.ckbxviewnet = QtGui.QCheckBox("View net failure", self)
        self.ckbxviewnet.adjustSize()
        self.ckbxviewnet.move(275, 85)
        self.ckbxviewnet.setToolTip("View the network failure as nodes are removed")
        self.ckbxviewnet.stateChanged.connect(self.viewfailure) #not sure if needed as calls can be based on if the box is checked
        
        self.btndraw = QtGui.QPushButton('Draw', self)
        self.btndraw.move(275, 150)
        self.btndraw.setToolTip('Draw the network')
        self.btndraw.adjustSize()
        self.built = self.btndraw.clicked.connect(self.viewnet) #view the network and set built as true 
        self.btnstart = QtGui.QPushButton('Start', self)
        self.btnstart.setToolTip('Run the analysis')
        self.btnstart.move(425, 150)
        self.btnstart.adjustSize()
        self.btnstart.clicked.connect(self.runsim)        
        self.btnstep = QtGui.QPushButton('Step', self)
        self.btnstep.setToolTip('Run the first step of the analysis')
        self.btnstep.move(350, 150)
        self.btnstep.adjustSize()
        self.btnstep.clicked.connect(self.stepanalysis)
        self.btnreset = QtGui.QPushButton('Reset/Cancel', self)
        self.btnreset.setToolTip('Cancel and/or reset the analysis')
        self.btnreset.move(200, 150)
        self.btnreset.adjustSize()
        self.btnreset.clicked.connect(self.reset)        
        
        self.setGeometry(300,300,515,195)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Network Tool v1.2') #title of window 
        self.show() #show window
               
    def showepwindow(self):
        '''Open the extra parameter window.'''
        self.w = ExtraParamWindow()
        self.w.show()
    def showdbwindow(self):
        '''Open the database connection window.'''
        inputDlg = DbConnect(self)
        inputDlg.show() 
    def ckbxoptionlimited(self):
        '''Change the enabled checkboxes for node slection when single analysis
        is selected and check the only valid option.'''
        self.ckbx5.setEnabled(False)
        self.ckbx6.setEnabled(False)
        self.ckbx5.setChecked(False)
        self.ckbx6.setChecked(False)
        self.ckbx4.setChecked(True)
        QtGui.QApplication.processEvents() #refresh gui
    def ckbxoptionall(self):
        '''Set all the node selection check boxes as checkable again.'''
        self.ckbx5.setEnabled(True)
        self.ckbx6.setEnabled(True)
    def limitoptions(self):
        '''Change the state of the option checkboxes when the isolates check 
        box is selected.'''
        if self.ckbxisolates.isChecked():
            self.ckbxnoisolates.setEnabled(False)
            self.ckbxnoisolates.setChecked(True)
        else:
            self.ckbxnoisolates.setEnabled(True)
            self.ckbxnoisolates.setChecked(False)
    def reset(self):
        '''Executed when the analysis is completed, or it is ended for any 
        reason. Resets all the appropraie values and settings back to the 
        starting state and closes and plotting window which is open.'''
        #this should be used for reseting all values and appropriate varables back to zero, meaning any current analysis is deleted
        self.first = True
        self.iterate = True
        self.built = False
        self.timestep = 0
        self.cancel = True
        self.figureModel = None
        self.positions = None
        self.built = False
        self.btndraw.setEnabled(True) #draw button
        self.btnstep.setEnabled(True) #allow the button to be pressed again
        self.btnstart.setEnabled(True)
        self.ckbxviewnet.setEnabled(True) #view graph checkbox       
        pl.close('all') #not seem to be working
        #pl.close()
        
    def clear(self):
        '''Clear the three QLinEdit/input text boxes.'''
        self.txtparam1.setText('')
        self.txtparam2.setText('')
        self.txtparam3.setText('')
        
    def closeall(self):
        '''Closes the other windows if they are open when Exit chosen from 
        File menu.'''
        pl.close('all') #closes the network visualisation window
        #need to add some more here
        
    def viewfailure(self):  
        '''Sets the viewfailure varaible based on if the appropraite checkbox 
        is checked.'''
        #when the eternal module is called, would make sence to send the required variables for the visualisation method to the module        
        if self.ckbxviewnet.isChecked():         
            self.viewfailures = True
        else:
            self.viewfailures = False
        
    def networkselection(self, text):
        '''Alter the interface depending on what is selected in the combo box 
        for graph type.'''
        self.graph = text
        if text == 'GNM':
            self.clear()
            self.txtparam3.setEnabled(False)
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389. Min = 1, Max = 6000') 
            self.QValidator = QtGui.QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,6000,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
        elif text == 'Erdos Renyi':
            self.clear()
            self.txtparam3.setEnabled(False)
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
            self.QValidator = QtGui.QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.txtparam2.setInputMask("B.9")
        elif text == 'Watts Strogatz':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg.,34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15. Min = 1, Max = 200')
            self.txtparam3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
            self.QValidator = QtGui.QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,200,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Barabasi Albert':
            self.clear()
            self.txtparam3.setEnabled(False)
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 50')
            self.QValidator = QtGui.QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,50,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
        elif text == 'Hierarchical Random':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2.setToolTip('The number of children from each new node. eg., 2 or 6. Min = 1, Max = 10')
            self.txtparam3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.QValidator = QtGui.QIntValidator(1,10,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Hierarchical Random +':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 10')
            self.txtparam3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.QValidator = QtGui.QIntValidator(1,10,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Hierarchical Communities':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(False)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 4')
            self.txtparam2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
            self.QValidator = QtGui.QIntValidator(1,4,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(0,1,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
        elif text == 'Tree':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(False)
            self.txtparam1.setToolTip('The number of child nodes per parent. eg., 3 or 5. Min = 1, Max = 50')
            self.txtparam2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6. Min = 1, Max = 10')
            self.QValidator = QtGui.QIntValidator(1,50,self.txtparam1)       
            self.txtparam1.setValidator(self.QValidator)
            self.QValidator = QtGui.QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.QValidator)
        elif text == 'Database':
            self.clear()
            self.txtparam1.setEnabled(False)
            self.txtparam2.setEnabled(False)
            self.txtparam3.setEnabled(False)
        elif text == 'Lists':   
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(False)
            self.txtparam1.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
            self.txtparam2.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')
    def openfile(self):
        '''Function for opening a text file and adding the lists to the input 
        boxes on the GUI.'''
        #load in a csv, add lists to text boxes, then select lists for the input 
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        text = 'Lists'
        self.networkselection(text)
        
        text=open(fname).read()
        text1, text2 = text.split('\n')
        self.txtparam1.setText(text1)
        self.txtparam2.setText(text2)
        self.cmbox.setCurrentIndex(9)
        
        
        
    def setfilelocation(self):
        '''Set the file location for the output file.'''
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        return fileName

    def viewnet(self):
        '''Function to view the network using the range of options. Activated 
        through the draw button or the draw menu option.'''
        
        param1 = self.txtparam1.text() 
        param2 = self.txtparam2.text()
        param3 = self.txtparam3.text() 
        self.buildnet(param1, param2, param3) #desptie geeting a warning here still appear to be built??
        if self.G == None:            
            return
        else:
            self.built = True
            self.method = self.showcombo() #open selection window for layout
            if self.method == 'Random':
                self.positions = nx.random_layout(self.G)
            elif self.method == 'Circle':
                self.positions = nx.circular_layout(self.G)
            elif self.method == 'Spring':
                self.positions = nx.spring_layout(self.G)
            elif self.method == 'Shell':
                self.positions = nx.shell_layout(self.G)
            elif self.method == 'Spectral':
                self.positions = nx.spectral_layout(self.G)
            elif self.method == 'Circle Tree (bfs)':
                self.positions = vis.tree_circle(self.G, bfs = True)                
            elif self.method == 'Circle Tree (dfs)':
                self.positions = vis.tree_circle(self.G, bfs = False) 
            elif self.method == 'Tree (bfs)':
                self.positions = vis.tree(self.G, bfs=True)
            elif self.method == 'Tree (dfs)':
                self.positions = vis.tree(self.G, bfs=False)
            elif self.method == 'Geographic':
                self.positions = vis.geo(self.G)
            elif self.method == False:
                QtGui.QMessageBox.information(self, 'Message', "Visualisation process canceled.") 
                return
            else:
                print 'ERROR!'
            self.graphviz = self.G.copy()
            for node in self.graphviz.nodes_iter():
                self.graphviz.node[node]['state'] = 1
            self.timestep = -1
            self.figureModel, self.timestep = draw(self.graphviz, self.positions, self.figureModel, self.timestep)
        return 
                    
    def showcombo(self):
        '''Loads a GUI where the use selects the method of positioning the nodes.'''
        if self.graph == 'Database':
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)', 'Geographic'
        else:
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'

        method, ok = QtGui.QInputDialog.getItem(self, 'Input Dialog', 
            'Select visualisation method:', items)
        if ok == False:
            method = False
        return method
                      
    def runsim(self):
        '''Runs the analysis in one go, initiated by the start button. Also 
        allows for the cancel button to work.'''
        self.cancel = False #set as false as this will allow the analysis to run
        
        
        while self.iterate == True:
            self.btnstep.setEnabled(False)
            self.ckbxviewnet.setEnabled(False)
            self.btndraw.setEnabled(False) 
            self.btnstart.setEnabled(False)
            if self.cancel == False:
                self.stepanalysis()
                if self.G==None: #this stops the analysis if the network is empty after the build process. Pos a better way earlier in the process available, but still works.
                    self.cancel = True
                    self.reset()
            else:
                self.lbl4.setText("Ready - Analysis Canceled") #changes the text in the GUI   
                self.lbl4.adjustSize()
                QtGui.QApplication.processEvents() #refresh gui
                self.iterate = False #this not needed I think
                self.reset()
                return
        if self.iterate == False:
            self.values = res.outputresults(self.graphparameters, self.parameters)     
            path_length_A, node_count_removed_A, isolated_n_count_removed_A, averagedegree, numofcomponents, isolates_n_count_A = self.values
            #put print messages in here to monitor the values if the metrics form the analysis
               
            result = True #This should come from the analysis module at some point to confirm the analysis has been successfull        
            self.analysisfinished(result, self.values)
            
                
    def analysisfinished(self,result, values):        
        '''When the analysis finished, displays the GUI with the next option 
        to view the metric graphs.'''
        global valueset
        self.reset()
        if result == True:   
            self.lbl4.setText('Analysis Completed')
            self.lbl4.adjustSize()
            QtGui.QApplication.processEvents() #refresh gui         
            ok = QtGui.QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed. Do you want to view the metric graphs?" , '&No','&View Graphs')
            if ok == 1: #if the view graph option is clicked
                valueset= self.values
                pl.close()
                inputdlg = ViewGraphs()
                self.btnstep.setEnabled(True)#allow the button to be pressed again
                inputdlg()
                self.btndraw.setEnabled(True)
        else:
            self.lbl4.setText("Analysis failed")            
        self.lbl4.adjustSize()
        

    #function which will run the analysis one step at a time
    def runstep(self, graphparameters, parameters, iterate):
        '''Run the analysis.'''
        graphparameters, iterate = res.step(graphparameters, parameters, iterate)
        return graphparameters, iterate

    def stepanalysis(self):
        '''Activated by the step button. Runs one step of analysis.'''
        self.lbl4.setText("Processing")
        self.lbl4.adjustSize()
        QtGui.QApplication.processEvents() #refresh gui
        self.cancel = False
        self.btnstep.setEnabled(False)#so button cannot be pressed while process is running
        active = 1
        inactive = 0
        global forthread, timedelay
        self.ckbxviewnet.setEnabled(False)
        if self.first == True:   
            self.btndraw.setEnabled(False)
            self.lbl4.setText("Initiating")
            self.lbl4.adjustSize()
            QtGui.QApplication.processEvents() #refresh gui
            param1 = self.txtparam1.text() 
            param2 = self.txtparam2.text()
            param3 = self.txtparam3.text() 
            self.timestep = 0 #set the counter to 0 as this must be the first run through (in theory at least)
            if self.built == True:
                pass
            else:
                self.buildnet(param1, param2, param3)                
                if self.G == None:     
                    self.reset()
                    return                
            self.parameters = self.checkanalysistype() #get the type of analysis to be performed
            if self.nofilename == True:
                self.cancel = True
                self.lbl4.setText("Ready")
                self.lbl4.adjustSize()
                QtGui.QApplication.processEvents() #refresh gui
                self.btnstep.setEnabled(True)#allow the button to be pressed again
                self.btndraw.setEnabled(True)
                self.ckbxviewnet.setEnabled(True)
                return
            #network and variables included in graphparameters                      
            self.graphparameters = res.core_analysis(self.G)    
            forthread = self.graphparameters, self.parameters, self.iterate
            #if the network is to be visualiased when failing
            if self.ckbxviewnet.isChecked():
                 if self.positions == None:
                     selected = self.showcombo() 
                     #need the relavnt method here to identify the option which is selected and use of in the nx.draw line
                     self.getpositions(selected)
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
            self.timestep+=1 #should iterate timestep now
            self.graphparameters, self.parameters, self.iterate = forthread
            forthread = self.graphparameters, self.parameters, self.iterate
            self.workThread = WorkThread() #name workthread
            i, nodes_removed_A, node_count_removed_A, node_count_removed_B, inter_removed_count, GA, GB, GtempA, GtempB,dlist,removed_nodes,subnodes_A, isolated_nodes_A,node_list,nodes_removed_A,to_nodes, from_nodes,numofcomponents, sizeofcomponents, avpathlengthofcomponents, giantcomponentavpathlength, giantcomponentsize, avnodesincomponents, averagedegree, isolated_nodes_B,subnodes_B,path_length_B,subnodes_count_B,isolated_n_count_removed_B,path_length_A,subnodes_count_A,isolated_n_count_removed_A,B_count_nodes_left,inter_removed_nodes, A_count_nodes_left, dead, deadlist, figureModel, isolated_n_count_A, isolated_n_count_B = self.graphparameters
            if self.iterate == True: #self.iterate used to be part of a global variable
                self.threadPool.append( WorkThread() )
                #this recieves the stuff and calls the function to add the text to the list
                self.connect( self.threadPool[len(self.threadPool)-1], QtCore.SIGNAL("update(QString)"), self.runstep )
                self.threadPool[len(self.threadPool)-1].start()  
                
                #gets the results refreshed                
                self.graphparameters, self.parameters, self.iterate = forthread
                i, nodes_removed_A, node_count_removed_A, node_count_removed_B, inter_removed_count, GA, GB, GtempA, GtempB,dlist,removed_nodes,subnodes_A, isolated_nodes_A,node_list,nodes_removed_A,to_nodes, from_nodes,numofcomponents, sizeofcomponents, avpathlengthofcomponents, giantcomponentavpathlength, giantcomponentsize, avnodesincomponents, averagedegree, isolated_nodes_B,subnodes_B,path_length_B,subnodes_count_B,isolated_n_count_removed_B,path_length_A,subnodes_count_A,isolated_n_count_removed_A,B_count_nodes_left,inter_removed_nodes, A_count_nodes_left, dead, deadlist, figureModel, isolated_n_count_A, isolated_n_count_B = self.graphparameters

                if self.ckbxviewnet.isChecked(): #would appear that the visualisation is current but I'm not 100% sure this is correct                               
                    print 'the nodes in G are : ', self.G.nodes()
                    if self.ckbx1.isChecked(): #reset all to active
                        #draw for single analysis
                        print 'nodes removed is :', nodes_removed_A
                        for node in self.graphviz.nodes_iter(): #set the state to inactive for relavant nodes 
                            self.graphviz.node[node]['state'] = active
                        print 'the number of nodes in GtempA is: ', GtempA.number_of_nodes()
                        removednodes = set(self.graphviz.nodes()) - set(GtempA.nodes())
                        for node in removednodes:
                            self.graphviz.node[node]['state'] = inactive
                        print 'the removed node was: ', removednodes        
                        #self.graphviz.node[len(nodes_removed_A)-1]['state'] = inactive
                    else:
                        removednodes = set(self.graphviz.nodes()) - set(self.G.nodes()) #need to convert to sets as lists cannot be subtracted
                        print 'the removed nodes are: ', removednodes
                        for node in removednodes: #set the state to inactive for relavant nodes 
                            self.graphviz.node[node]['state'] = inactive 
                    self.lbl4.setText("Drawing")
                    self.lbl4.adjustSize()
                    QtGui.QApplication.processEvents() #refresh gui
                    self.figureModel, self.timestep = draw(self.graphviz, self.positions, self.figureModel, self.timestep)
                    self.pausetime = timedelay                    
                    time.sleep(self.pausetime) 
            elif self.iterate == False: #when the iterate variable changes to False, which means the analysis has finished
                self.values = res.outputresults(self.graphparameters, self.parameters)     
                path_length_A, numofcomponents,  averagedegree, node_count_removed_A, isolated_n_count_removed_A,  isolates_n_count_A = self.values
                #put print messages in here to monitor the values if the metrics form the analysis
               
                result = True #This should come from the analysis module at some point to confirm the analysis has been successfull        
                self.analysisfinished(result, self.values)
                self.iterate = False
            else:
                 print 'Critical error somewhere!' #never seen this so no worries here   
        self.btnstep.setEnabled(True)#allow the button to be pressed again
        self.lbl4.setText("Ready")
        self.lbl4.adjustSize()
        QtGui.QApplication.processEvents() #refresh gui
    
    def getpositions(self, selected):
        '''Using the selected text from the combo box, calculate the positions
        for the nodes.'''
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
        elif selected == 'Geographic':
            self.positions=vis.geo(self.G)
        else:
            print 'Error in the selection of vis method'

    def checkanalysistype(self):
        '''Get the analysis type, the file location and if any of the other 
        options have been selected related to the analysis if the network.'''
        SINGLE = False
        SEQUENTIAL = False
        CASCADING = False
        RANDOM = False
        DEGREE = False
        BETWEENNESS = False
        REMOVE_SUBGRAPHS = False
        REMOVE_ISOLATES = False
        NO_ISOLATES = False
        
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
            elif self.ckbx2.isChecked() and self.ckbx4.isChecked():
                SEQUENTIAL = True
                RANDOM = True            
            elif self.ckbx2.isChecked() and self.ckbx5.isChecked():
                SEQUENTIAL = True
                DEGREE = True            
            elif self.ckbx2.isChecked() and self.ckbx6.isChecked():
                SEQUENTIAL = True
                BETWEENNESS = True            
            elif self.ckbx3.isChecked() and self.ckbx4.isChecked():
                CASCADING = True
                RANDOM = True            
            elif self.ckbx3.isChecked() and self.ckbx5.isChecked():
                CASCADING = True
                DEGREE = True            
            elif self.ckbx3.isChecked() and self.ckbx6.isChecked():
                CASCADING = True
                BETWEENNESS = True
            else:
                self.lbl4.setText("Error")
            
            self.lbl4.adjustSize()
            self.lbl4.show()
            QtGui.QApplication.processEvents() #refresh gui
            if self.ckbxsubgraphs.isChecked():
                REMOVE_SUBGRAPHS = True
            if self.ckbxisolates.isChecked():
                REMOVE_ISOLATES = True
            if self.ckbxnoisolates.isChecked():
                NO_ISOLATES = True
                
            parameters = SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName
            return parameters
              
              
    def closeEvent(self, event):
        '''Over rides the automatic close event so can ask user if they 
        want to quit.'''
        reply = QtGui.QMessageBox.question(self, 'Message',"Are you sure you want to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.Yes: #if the user clicks yes
            event.accept()
            self.cancel = True
            self.closeall()
        else: #if the user clicks no
            event.ignore()
            
    def getdbparameters(self):
        '''Open the GUI for the user to input the database connection 
        parameters. This needs looking at as works, but not as intended. 
        Could thus do with cleaning up.'''
        self.failed = False        
        dlg = DbConnect()
        if dlg.exec_():
            data =dlg.getval()
        else:
            self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME = dlg.getval()
        if self.NETNAME == '':
            self.failed = True
            return 
        else:
            return 
        
    def getdbnetwork(self):
        '''Connect to the database and pull the network into the system.'''
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
        '''Build the network given the input parametrs.'''
        #means if the network is not built, G still exists, but will be set ot None, thus this can be caught easily
        self.G = None 
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
            self.G = nx.watts_strogatz_graph(param1, param2, param3)
            if nx.is_connected(self.G)==False:
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
            self.G = nx.gnm_random_graph(param1, param2)
            if nx.is_connected(self.G)==False:
                #bring up error message box
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                self.G = None #needs to reset G to none when graph is unconnected                
                self.btnstep.setEnabled(True)#allow the button to be pressed again                            
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
            self.G = nx.barabasi_albert_graph(param1, param2)
            if nx.is_connected(self.G)==False:
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
            self.G = nx.erdos_renyi_graph(param1, param2)
            if nx.is_connected(self.G)==False:
                #bring up error message box
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.graph == 'Database': #database connection  -currently only allows a single network
            self.G = self.getdbnetwork()
            if self.G == None:
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
            self.G = customnets.hr(param1,param2,param3)
        elif self.graph =='Hierarchical Random +': #ahr
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
            self.G = customnets.ahr(param1,param2,param3)
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
                    self.G = customnets.square(param1)
            elif param2 == 1:
                if param1 == 0 or param1 >= 5:
                    QtGui.QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is incorrect. Should be between 1 and 4.")
                else:
                    self.G = customnets.tri(param1)
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
            self.G=nx.balanced_tree(param1, param2)
        elif self.graph == 'Lists': #lists
            #param1 is a list of nodes  #param2 is a list of egdes
            #need to convert the input strings to lists with integers in the correct format
            if param1 =='' or param2=='':
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. Please enter node and edge lists or select a different option.")
                                
                return #exit sub
            self.G = nx.Graph()
            param1 = replace_all(param1, {' ':'','[':'',']':'',')':'','(':''})
            param1 = param1.split(',')
            nodelist=[]            
            for item in param1:
                item = int(item)
                nodelist.append(item)
            try:
                self.G.add_nodes_from(nodelist)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. The node list does not fit the required format.")
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
                self.G.add_edges_from(edgelist)
            except:
                QtGui.QMessageBox.warning(self, 'Error!', "Graph could not be created. The edge list is not in the correct formart.")            
                return #exit sub
        else: 
            QtGui.QMessageBox.warning(self, 'Error!', "Error! Please try again.")          
            return #exit sub
        self.param1 = param1 #make these freely accessable
        self.param2 = param2
        self.param3 = param3
        if self.G == None:
            self.cancel = True
            return
        else:
            return  
    
class WorkThread(QtCore.QThread): #create the worker thread, where the sresilience analysis will be run
    def __init__(self): #initiate the thread
        QtCore.QThread.__init__(self)
   
    def __del__(self):
        self.wait()
        
    def run(self): #run the thread
        '''Run the analysis on a second thread to help stop the GUI freezing.'''
        global valueset, forthread
        graphparameters, parameters, iterate = forthread
        #need to put in the method to call the step code here
        graphparameters, iterate = res.step(graphparameters, parameters, iterate) #run one step of the analysis
        print 'iterate in the work thread is: ', iterate
        forthread = graphparameters, parameters, iterate
        #self.emit( QtCore.SIGNAL('forthread[list]'), "from work thread " + str(forthread) )
        #them some signal to tranfer messages and data to the main application

def draw(G, positions, figureModel, timestep):
    '''Handles the initial setup parameters for drawing the network as well as then calling the function to draw the network'''
    if figureModel == None or figureModel.canvas.manager.window == None: #if figure model window has not been opened yet
        figureModel = pl.figure()
        pl.ion()
        pl.show()
    #need this in case the user closes the window 
    try:
        figureModel.canvas.set_window_title('Network View') 
    except:
        figureModel = None
        figureModel = pl.figure()
        figureModel.canvas.set_window_title('Network View') 
        
    pl.cla()    
    drawnet(G, positions, timestep)   
    pl.show()  
    figureModel.canvas.manager.window.update()  #gets error here when the window is closed by whatever means  
      
    return figureModel, timestep
      
def drawnet(G, positions, timestep):
    '''Draws the network.'''
    inactivenodes=[]
    activenodes=[]
    inactiveedges=[]
    activeedges=[]
    pl.cla()
    #cheat way of removing the axis and labels quickly
    g1 = nx.Graph() 
    nx.draw(g1)
    #conditionals to change size of nodes depending on the number of them
    if G.number_of_nodes() <=50:
        size = 300
    elif G.number_of_nodes()>50 and G.number_of_nodes()<=100:
        size = 100
    elif G.number_of_nodes()>100 and G.number_of_nodes()<=250:
        size = 50
    else:
        size = 30
    nx.draw_networkx_nodes(G, positions, node_size= size, node_color = 'g', with_labels=True)
    nx.draw_networkx_edges(G, positions, edge_width=6, edge_color = 'g')
    if timestep <> -1:
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
    nx.draw_networkx_nodes(G, positions, node_size=size, nodelist = inactivenodes, node_color = 'r', with_labels=True)   
    #nx.draw_networkx_edges(G, positions, edgelist = inactiveedges, edge_color = 'b')
    #nx.draw_networkx_edges(G, positions, edgelist = activeedges, edge_color = 'r')

def replace_all(text, dic):
    '''Used to modify strings to make them suitable for purpose.'''
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text
        
def main():
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
   
if __name__ == '__main__':
    main()    
