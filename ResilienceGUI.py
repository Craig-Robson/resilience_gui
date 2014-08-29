# -*- coding: utf-8 -*-
"""
Version v2_0_0 - development for dependency analysis
All changes made to be listed here


Plans:
second combo box with none option -allows for single, dependency and interdependency analysis
inputing variables/data for two networks
    -two sets of input boxes, second set disabled until combobox on a graph type
    -add the open option to both list (instead of having lists when open)
    -make the input boxes smaller
    -have a gui open for lists when selected
        -as also needs to be eddited, need a edit button
        -would also need this for open option
        -new class or inbuilt widget? - new class would give greater flexability
    -how to specify dependency or interdependency analysis
        -simple checkboxes
        -simple combobox
        -could be linked to method where dependencies are specified
    -how so specify the nodes in the dependency
        -need to now how the database works
        -might have a list of edges in it
        -lists of nodes in a listbox
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
import interdependency_analysis_v5_0_1 as res 
import inhouse_algorithms as customnets
import visalgorithms_v10_1 as vis

class DbConnect(QDialog):    
    '''Class for the database parameters connection window.'''
    def __init__(self, parent=None):
        #super(dbconnect, self).__init__(parent)
        QDialog.__init__(self, parent)   
        #parametes for database connection     
        exitAction = QAction('&Exit',self)
        exitAction.triggered.connect(qApp.quit)
        print 'building db connection window'
        self.DBNAME= ""
        self.HOST = "" 
        self.PORT = ""
        self.USER = ""
        self.PASSWORD = ""        
        self.lbl1 = QLabel('dbname: ', self)
        self.lbl1.move(25,30)
        self.lbl1.adjustSize()
        self.txtinput1 = QLineEdit(self)        
        self.txtinput1.move(75, 25)
        self.txtinput1.setText(self.DBNAME)
        self.txtinput1.setToolTip('name of database')
        self.lbl2 = QLabel('host: ', self)
        self.lbl2.move(25,55)
        self.lbl2.adjustSize()
        self.txtinput2 = QLineEdit(self)        
        self.txtinput2.move(75, 50)
        self.txtinput2.setToolTip('host of database')
        self.lbl3 = QLabel('port: ', self)
        self.lbl3.move(25,80)
        self.lbl3.adjustSize()        
        self.txtinput3 = QLineEdit(self)        
        self.txtinput3.move(75, 75)
        self.txtinput3.setToolTip('port')
        self.lbl4 = QLabel('user: ', self)
        self.lbl4.move(25,105)
        self.lbl4.adjustSize()
        self.txtinput4 = QLineEdit(self)        
        self.txtinput4.move(75, 100)
        self.txtinput4.setToolTip('user')
        self.lbl5 = QLabel('password: ', self)
        self.lbl5.move(25,130)
        self.lbl5.adjustSize()
        self.txtinput5 = QLineEdit(self)        
        self.txtinput5.move(75, 125)
        self.txtinput5.setToolTip('password')
        self.lbl6 = QLabel('net name: ', self)
        self.lbl6.move(25,160)
        self.lbl6.adjustSize()
        self.txtinput6 = QLineEdit(self)        
        self.txtinput6.move(75, 155)
        self.txtinput6.setToolTip('network name in database')

        self.applybtn = QPushButton('Apply', self)
        self.applybtn.setToolTip('Connect to the database and run the analysis')
        self.applybtn.move(170, 185)
        self.applybtn.adjustSize()
        self.applybtn.clicked.connect(self.applyclick)
        
        self.cancelbtn = QPushButton('Cancel', self)
        self.cancelbtn.setToolTip('Cancel the analysis and close the window')
        self.cancelbtn.move(10, 185)
        self.cancelbtn.adjustSize()
        self.cancelbtn.clicked.connect(self.cancel)

        self.restore = QPushButton('Restore', self)
        self.restore.setToolTip('Restore the settings from the previous successful analyiss this session')
        self.restore.move(90, 185)
        self.restore.adjustSize()
        self.restore.clicked.connect(self.restoreinputs)

        self.setGeometry(300,500,250,220)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('db Connection Parameters')  #title of windpw          
        self.show()#show window   
   
    def updateparameters(self, dbconnect):
        ''''''
        print 'updating db parameters'
        self.dbconnect = dbconnect
    def applyclick(self):
        '''Save the text from that was in the text boxes when function called.'''
        self.DBNAME = self.txtinput1.text()
        self.HOST = self.txtinput2.text()
        self.PORT = self.txtinput3.text()
        self.USER = self.txtinput4.text()
        self.PASSWORD = self.txtinput5.text()        
        self.NETNAME = self.txtinput6.text()
        self.dbconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        #DBinputs = self.DBconnect   
        print 'performing window update'
        window.updatedb(self.dbconnect)
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
        if self.dbconnect == None:
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

class OptionsWindow(QWidget): # not sure if I will need this after all
    def __init__(self, parent = None):  
        QWidget.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        self.colactive = None
        self.colinactive = None
        self.timedelay, self.col1, self.col2 = window.updateoptions()        
        self.timedelay = str(self.timedelay)
        self.lbltimedelay =QLabel("Time(secs) between iterations: ",self)
        self.lbltimedelay.move(15,25)
        self.lbltimedelay.adjustSize()
        self.txttimedelay = QLineEdit(self) 
        self.txttimedelay.move(170,22)
        self.txttimedelay.setFixedWidth(50)
        self.txttimedelay.setText(str(self.timedelay))
        self.txttimedelay.setToolTip('The minimum time(seconds) between iterations. Min = 0, Max = 300')        
        self.validator = QIntValidator(0,300,self.txttimedelay)       
        self.txttimedelay.setValidator(self.validator)
        
        self.lblcolor1 = QLabel("Active features", self)
        self.lblcolor1.adjustSize()        
        self.lblcolor1.move(12,50)
        self.lblcolor2 = QLabel("Inactive features", self)
        self.lblcolor2.adjustSize()
        self.lblcolor2.move(12,75)
        self.colors= 'red','green','blue', 'black', 'cyan', 'magenta', 'yellow'
        self.cmbxcolor1 = QComboBox(self)
        self.cmbxcolor1.move(130,50)
        self.cmbxcolor1.addItems(self.colors)
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col1:
                self.cmbxcolor1.setCurrentIndex(int(index))        
                index = 999
            index += 1
        self.cmbxcolor2 = QComboBox(self)
        self.cmbxcolor2.move(130,75)
        self.cmbxcolor2.addItems(self.colors)
        index = 0
        while index < len(self.colors):
            if self.colors[index]==self.col2:
                self.cmbxcolor2.setCurrentIndex(int(index))
                index = 999
            index += 1
        self.cmbxcolor1.activated[str].connect(self.getcoloractive)        
        self.cmbxcolor2.activated[str].connect(self.getcolorinactive)
        
        self.apply = QPushButton("Apply", self)
        self.apply.adjustSize()
        self.apply.move(145,150)
        self.apply.clicked.connect(self.applyandclose)
        self.apply.setToolTip("Apply any changes and close the window.")
        self.closebtn = QPushButton("Close", self)
        self.closebtn.adjustSize()
        self.closebtn.move(70,150)
        self.closebtn.clicked.connect(self.closeclick)
        self.closebtn.setToolTip("Close the window without saving any changes.")
                
        self.setGeometry(300,500,230,180) #above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Parameter Window') #title of window  
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
        window.updatetimedelay(self.timedelay)
        window.updatecolors(self.colactive, self.colinactive)
        self.close() 
    def closeclick(self):
        self.close()
class ViewGraphs(QDialog):   
    "Class for the window which allows the viewing of the results in terms of the graph metrics."
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        
        self.valueset = window.updatevalueset()        
        self.figureGraph = None
        self.lblop1 = QLabel('Plot 1:', self)
        self.lblop1.adjustSize()
        self.lblop1.move(15, 28)        
        self.option1 = QComboBox(self)
        self.metriclist=['Average path length', 'Number of components', 'Average degree', 'Nodes count removed', 'Isolated node count', 'Number of isolates', 'None']
        self.option1.addItems(self.metriclist)
        self.option1.move(60, 25)
        self.lblop2 = QLabel('Plot 2:', self)
        self.lblop2.adjustSize()
        self.lblop2.move(15, 58) 
        self.option2 = QComboBox(self)
        self.option2.addItems(self.metriclist)      
        self.option2.move(60, 55)
        self.cancelbtn = QPushButton('Close', self)
        self.cancelbtn.setToolTip('Close the window')        
        self.cancelbtn.move(124, 80)
        self.cancelbtn.clicked.connect(self.cancelclick)

        self.option1.activated[str].connect(self.option1changed)             
        self.option2.activated.connect(self.option2changed)
        #just need to sort this out so the variable values can be transfered into this class easily
        #attempt to get the metric values for the graphs from the mian window class

        self.setGeometry(900,500,210,110)#above; vertical place on screen, hoz place on screen, width of window, height of window
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
        self.metric1 = self.option1value
        self.metric2 = self.option2value
        self.valuenames = 'average path length', 'number of components', 'average degree','nodes removed count','isolates removed',  'number of isolates' #list for the labels, needs updating manually
        self.valueset = list(self.valueset)  
        
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
        
        pl.subplot(211)
        pl.cla() #clear the plot   
        pl.plot(self.valueset[self.metric1], 'b', linewidth=2, label=self.valuenames[self.metric1])
        pl.xlabel('Number of nodes removed')
        pl.ylabel(self.option1.currentText())
        pl.ylim(ymin=0)
        ymax =max(self.valueset[self.metric1])
        pl.ylim(ymax=ymax+0.5)  
        pl.xlim(xmin=0)        
        pl.subplot(212)    
        pl.cla()
        if self.metric2<>99:
            pl.plot(self.valueset[self.metric2], 'r', linewidth=2, label=self.valuenames[self.metric2])            
        pl.xlabel('Number of nodes removed')
        pl.ylabel(self.option2.currentText())
        pl.ylim(ymin=0)
        ymax =max(self.valueset[self.metric2])
        pl.ylim(ymax=ymax+0.5)  
        pl.xlim(xmin=0)            
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

class Window(QMainWindow):
    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        #Check  networkx files can be loaded
        try:
            import networkx as nx
        except:
            QMessageBox.warning(self, 'Import Error', 'Could not import networksx. The application will now close.')
            qApp.quit
        #Check the files for the database connection can be loaded.
        try:
            import osgeo.ogr as ogr
        except:
            QMessageBox.warning(self,'Import Error!', "Could not import the osgeo.ogr library. There will be no database connectivity as a result.")        
        try:
            try:            
                sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
                import nx_pgnet, nx_pg
            except:
                pass
            sys.path.append('C:/Users/Craig/Documents/GitRepo/nx_pgnet')
        except:
            QMessageBox.warning(self, 'Import Error!', 'Could not import the nx_pgnet or nx_pg modules. This will not allow the database conection to work.')
        
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
        self.DBNAME = ''
        self.HOST = ''
        self.PORT = ''
        self.USER = ''
        self.PASSWORD = ''        
        self.NETNAME = ''
        self.dbconnect = self.DBNAME, self.HOST, self.PORT, self.USER, self.PASSWORD, self.NETNAME    
        self.parameters = None
        self.running = False
        self.pause = False
        self.first = True
        self.figureModel = None
        self.iterate = True
        self.timestep = -1
        self.cancel = False
        self.positions = None
        self.G = None
        self.fullanalysis = False
        self.active = 1
        self.inactive = 0
        self.timedelay = 2
        self.coloractive = 'green'
        self.colorinactive = 'red'       
        self.dosingle = True
        self.G1 = None
        
        #create actions for file menu
        RunAction = QAction('&Run',self)
        RunAction.setShortcut('Ctrl+R')
        RunAction.setStatusTip('Run the selected analysis')
        RunAction.triggered.connect(self.full_analysis)       
        
        exitAction = QAction('&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        exitAction.triggered.connect(self.closeall)

        extraAction = QAction('&Options', self)
        extraAction.setShortcut('Ctrl+P')
        extraAction.setStatusTip('Open options window')
        extraAction.triggered.connect(self.showoptionswindow)

        dbAction = QAction('&DB Connection', self)
        dbAction.setShortcut('Ctrl+B')
        dbAction.setStatusTip('Open db connection properties')
        dbAction.triggered.connect(self.showdbwindow)
        
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load node and edge lists from .txt file')
        openAction.triggered.connect(self.openfile)
        
        resetAction = QAction('&Cancel/Reset', self)
        resetAction.setStatusTip('Cancel the analysis')
        resetAction.triggered.connect(self.reset)
        
        clearAction = QAction('&Clear inputs', self)
        clearAction.setShortcut('Ctrl+E')
        clearAction.setStatusTip('Clear the input text boxes')
        clearAction.triggered.connect(self.clear)
        
        viewnetAction = QAction('&View Network', self)
        viewnetAction.setShortcut('Ctrl+D')
        viewnetAction.setStatusTip('View the network')
        viewnetAction.triggered.connect(self.drawview)               
    
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
        #create and set some lables
        self.lbl4 = QLabel("Ready", self)
        self.lbl4.move(68,153)
        self.lbl4.adjustSize() 
        fontbold = QFont("Calibri", 10, QFont.Bold)      

        self.lbl6 = QLabel("STATE: ", self)
        self.lbl6.move(25,152)
        self.lbl6.setFont(fontbold)
        self.lbl6.adjustSize() 
        #set and create GUI features for the analysis type
        self.lbl2 = QLabel("Analysis types",self)
        self.lbl2.setFont(fontbold)
        self.lbl2.adjustSize()        
        self.lbl2.move(25,25)
        self.ckbx1 = QCheckBox("Single",self)
        self.ckbx1.adjustSize()
        self.ckbx1.move(25,45)
        self.ckbx1.setToolTip("Remove one node and relpace before the next node is removed")
        self.ckbx1.toggle()
        self.ckbx1.stateChanged.connect(self.ckbxoptionlimited)
        self.ckbx2 = QCheckBox("Sequential",self)
        self.ckbx2.adjustSize()
        self.ckbx2.move(25,65) 
        self.ckbx2.setToolTip("Remove nodes one after each other until none are left")
        self.ckbx2.stateChanged.connect(self.ckbxoptionall)
        self.ckbx3 = QCheckBox("Cascading",self)
        self.ckbx3.adjustSize()
        self.ckbx3.move(25,85)
        self.ckbx3.setToolTip("Remove a node, them all it's neighbours, then all of their neighbours etc,")
        self.ckbx3.stateChanged.connect(self.ckbxoptionall)
        self.Group1 = QButtonGroup(self)
        self.Group1.addButton(self.ckbx1)
        self.Group1.addButton(self.ckbx2)
        self.Group1.addButton(self.ckbx3)
        self.Group1.exclusive()
        #set and create GUI features for the node selection method
        self.lbl3 = QLabel("Node selection method",self)
        self.lbl3.setFont(fontbold)
        self.lbl3.adjustSize()        
        self.lbl3.move(130,25)
        self.ckbx4 = QCheckBox("Random", self)
        self.ckbx4.adjustSize()
        self.ckbx4.move(130,45)
        self.ckbx4.setToolTip("Select the node to remove at random")
        self.ckbx4.toggle()
        self.ckbx5 = QCheckBox("Degree", self)
        self.ckbx5.adjustSize()        
        self.ckbx5.move(130,65)
        self.ckbx5.setToolTip("Select the node with the highest degree")
        self.ckbx6 = QCheckBox("Betweenness", self)
        self.ckbx6.adjustSize()
        self.ckbx6.move(130,85) 
        self.ckbx6.setToolTip(
        "Select the node with the highest betweenness value")
        Group2 = QButtonGroup(self)     
        Group2.addButton(self.ckbx4)
        Group2.addButton(self.ckbx5)
        Group2.addButton(self.ckbx6)
        Group2.exclusive()
        #set when initated as not chackable as single is the defualt option
        self.ckbx5.setEnabled(False)
        self.ckbx6.setEnabled(False)
        #set and create GUI features for the network selection type
        self.lbl1 = QLabel("Network Type", self)
        self.lbl1.setFont(fontbold)
        self.lbl1.adjustSize()
        self.lbl1.move(275, 25)
        
        self.graph = 'GNM' #means this is the default, so if menu option not changed/used, will persume GNM graph
        inputs = ('GNM','Erdos Renyi','Watts Strogatz','Barabasi Albert',
                  'Hierarchical Random','Hierarchical Random +',
                  'Hierarchical Communities','Tree','Database','Lists')
        self.cmbox = QComboBox(self)
        self.cmbox.move(275,40)
        self.cmbox.addItems(inputs)
        self.cmbox.setToolTip("Select the graph type or graph input method")
        self.cmbox.activated[str].connect(self.networkselection)           
        #combo box for second network   
        inputs = ('None','GNM','Erdos Renyi','Watts Strogatz','Barabasi Albert',
                  'Hierarchical Random','Hierarchical Random +',
                  'Hierarchical Communities','Tree','Database','Lists')
        self.cmboxb = QComboBox(self)
        self.cmboxb.move(275,70)
        self.cmboxb.addItems(inputs)
        self.cmboxb.setToolTip("Select the graph type or graph input method")
        self.cmboxb.activated[str].connect(self.networkselectionb)  

        #set and create GUI features for the input text boxes
        self.lbl10 = QLabel("Graph Inputs", self)
        self.lbl10.setFont(fontbold)
        self.lbl10.adjustSize()
        self.lbl10.move(400, 25)
        self.txtparam1 = QLineEdit(self)        
        self.txtparam1.move(400, 40)
        self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM        
        self.txtparam2 = QLineEdit(self)
        self.txtparam2.move(500, 40)
        self.txtparam2.setToolTip(
        'The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtparam3 = QLineEdit(self)
        self.txtparam3.move(600, 40)
        self.txtparam3.setEnabled(False)              
        self.validator = QIntValidator(1,2000,self.txtparam1)       
        self.txtparam1.setValidator(self.validator)
        self.validator = QIntValidator(1,6000,self.txtparam2)       
        self.txtparam2.setValidator(self.validator)
        
        #setb of inputs for dependency and interdependency
        self.txtparam1b = QLineEdit(self)        
        self.txtparam1b.move(400, 72)
        self.txtparam1b.setToolTip('The number of nodes. eg., 34 or 178') #set the start up states for that top of the list, GNM        
        self.txtparam2b = QLineEdit(self)
        self.txtparam2b.move(500, 72)
        self.txtparam2b.setToolTip(
        'The number of edges. eg.,twice the no. of edges, 124 or 389')
        self.txtparam3b = QLineEdit(self)
        self.txtparam3b.move(600, 72)
        self.txtparam3b.setEnabled(False)              
        self.validator = QIntValidator(1,2000,self.txtparam1)       
        self.txtparam1b.setValidator(self.validator)
        self.validator = QIntValidator(1,6000,self.txtparam2)       
        self.txtparam2b.setValidator(self.validator)        

        #set default staes for parameter boxes b
        self.txtparam1b.setDisabled(True)
        self.txtparam2b.setDisabled(True)
        self.txtparam3b.setDisabled(True)
        
        #set and create the extra options features on GUI    
        self.lbl5 = QLabel("Remove subgraphs/isolated nodes", self)
        self.lbl5.setFont(fontbold)
        self.lbl5.adjustSize()
        self.lbl5.move(25,105)
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
        self.ckbxnoisolates.move(235, 120)
        self.ckbxnoisolates.setToolTip("Tick if nodes, one isolated, should not be selected for removal when running resilience analysis")
        self.ckbxisolates.stateChanged.connect(self.limitoptions)
        
        self.ckbxviewnet = QCheckBox("View net failure", self)
        self.ckbxviewnet.adjustSize()
        self.ckbxviewnet.move(275, 100)
        self.ckbxviewnet.setToolTip("View the network failure as nodes are removed")
        #set and create button for the GUI
        self.btndraw = QPushButton('Draw', self)
        self.btndraw.move(275, 150)
        self.btndraw.setToolTip('Draw the network')
        self.btndraw.adjustSize()
        self.built = self.btndraw.clicked.connect(self.drawview) #view the network and set built as true 
        self.btnstart = QPushButton('Start', self)
        self.btnstart.setToolTip('Run the analysis')
        self.btnstart.move(425, 150)
        self.btnstart.adjustSize()
        self.btnstart.clicked.connect(self.startorpause)        
        self.btnstep = QPushButton('Step', self)
        self.btnstep.setToolTip('Run the first step of the analysis')
        self.btnstep.move(350, 150)
        self.btnstep.adjustSize()
        self.btnstep.clicked.connect(self.step_analysis)
        self.btnreset = QPushButton('Reset/Cancel', self)
        self.btnreset.setToolTip('Cancel and/or reset the analysis')
        self.btnreset.move(200, 150)
        self.btnreset.adjustSize()
        self.btnreset.clicked.connect(self.reset)        
        
        self.setGeometry(300,300,715,195)#above; vertical place on screen, hoz place on screen, width of window, height of window
        self.setWindowTitle('Network Tool v2.0') #title of window 
        self.show() #show window
        #finished signal to follow on from the work thread
        self.connect(self.thread, SIGNAL("finished()"), self.updateUi)

    def startorpause(self):
        if self.running == True:
            self.pause = True
        elif self.running == False:
            self.running = True
            self.pause= False            
            self.full_analysis()
            
    def updatecolors(self, coloractive, colorinactive):
        self.coloractive = coloractive
        self.colorinactive = colorinactive
        
    def updatetimedelay(self,timedelay):
        self.timedelay = timedelay
        
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
        self.ckbx5.setEnabled(False)
        self.ckbx6.setEnabled(False)
        self.ckbx5.setChecked(False)
        self.ckbx6.setChecked(False)
        self.ckbx4.setChecked(True)
        QApplication.processEvents() #refresh gui
    def ckbxoptionall(self):
        '''Set all the node selection check boxes as checkable again.'''
        self.ckbx5.setEnabled(True)
        self.ckbx6.setEnabled(True)
    def disableallckbx(self):
        self.ckbx1.setEnabled(False)
        self.ckbx2.setEnabled(False)
        self.ckbx3.setEnabled(False)
        self.ckbx4.setEnabled(False)
        self.ckbx5.setEnabled(False)
        self.ckbx6.setEnabled(False)
        self.ckbxisolates.setEnabled(False)
        self.ckbxnoisolates.setEnabled(False)
        self.ckbxsubgraphs.setEnabled(False)
    def enableallckbx(self):
        self.ckbx1.setEnabled(True)
        self.ckbx2.setEnabled(True)
        self.ckbx3.setEnabled(True)
        self.ckbx4.setEnabled(True)
        if self.ckbx1.isChecked():
            pass
        else:
            self.ckbx5.setEnabled(True)
            self.ckbx6.setEnabled(True)
        self.ckbxisolates.setEnabled(True)
        if self.ckbxisolates.isChecked():
            pass
        else:
            self.ckbxnoisolates.setEnabled(True)
        self.ckbxsubgraphs.setEnabled(True)
    def openfile(self):
         '''Function for opening a text file and adding the lists to the input boxes on the GUI.'''
         #load in a csv, add lists to text boxes, then select lists for the input 
         fname = QFileDialog.getOpenFileName(self, 'Open file')
         text = 'Lists'
         self.networkselection(text)
         text=open(fname).read()
         text1, text2 = text.split('\n')
         self.txtparam1.setText(text1)
         self.txtparam2.setText(text2)
         self.cmbox.setCurrentIndex(9)
        
    def reset(self):
        '''Reset the variables and re-enable any items which have been disabled.'''
        self.G = None
        self.positions = None
        self.cancel = False
        self.timestep = -1
        self.graphvis = None
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
        
    def clear(self):
        '''Clear the three QLinEdit/input text boxes.'''
        self.txtparam1.setText('')
        self.txtparam2.setText('')
        self.txtparam3.setText('')
    def closeall(self):
        '''Closes the other windows if they are open when Exit chosen from 
        File menu.'''
        pl.close('all') #closes the network visualisation window
    def showoptionswindow(self):
        '''Open the extra parameter window.'''
        self.w = OptionsWindow()
        self.w.updatetimedelay(self.timedelay)
    def updateoptions(self):
        return self.timedelay, self.coloractive, self.colorinactive 
    
    def showdbwindow(self):
        '''Open the database connection window.'''
        inputDlg = DbConnect()
        inputDlg.updateparameters(self.dbconnect)
        
    def updatedb(self, dbconnect):
        ''''''
        print 'this is: ',dbconnect
        self.dbconnect = dbconnect
    def getdbparameters(self):
        '''Open the GUI for the user to input the database connection 
        parameters. This needs looking at as works, but not as intended. 
        Could thus do with cleaning up.'''
        self.failed = False        
        dlg = DbConnect()
        dlg.updateparameters(self.dbconnect)
        ####the next four lines do not work properly, but get the data anyhow.
        if dlg.exec_():
            dlg.getval()
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
        self.failed = False
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
                connection = str('PG: host= ' )+self.HOST+str(" dbname = '")+self.DBNAME+str("' user= '")+self.USER+str("' password= '")+self.PASSWORD+str("'")
                print 'connection: ', connection               
                conn = ogr.Open(connection)
                print 'connection open'
                self.G = nx_pgnet.read(conn, 'poewer_line_Edges', 'Power_line_NODES')#load in network from database and create networkx instance
                print 'G = ', self.G                
                return self.G
            except:
                QMessageBox.warning(self, 'Error!', "Could not connect to database and find the data. Please check your inputs and try again. The parameters were: \ndbname: "+self.DBNAME+"\nhost: "+self.HOST+"\nuser: "+self.USER+"\nport: " +self.PORT+"\npassword: "+self.PASSWORD+"\nnetwork: "+self.NETNAME,'&OK')
                self.G = None           
        else:
            self.cancel = True
            self.G = None
            return

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
        '''Called by the finished() signal, thus process the results, handles the visualisations and the completion of the analysis as well as the continument of the full analysis if applicable.'''
        print 'THE THREAD HAS FINSIHED'

        if self.timestep>0:
            forthread = self.thread.update()
            self.graphparameters, self.parameters, self.iterate = forthread
        else:
            self.graphparameters, self.parameters, self.iterate = self.forthread
        i, nodes_removed_A, node_count_removed_A, node_count_removed_B, inter_removed_count, GA, GB, GtempA, GtempB,dlist,removed_nodes,subnodes_A, isolated_nodes_A,node_list,nodes_removed_A,to_nodes, from_nodes,numofcomponents, sizeofcomponents, avpathlengthofcomponents, giantcomponentavpathlength, giantcomponentsize, avnodesincomponents, averagedegree, isolated_nodes_B,subnodes_B,path_length_B,subnodes_count_B,isolated_n_count_removed_B,path_length_A,subnodes_count_A,isolated_n_count_removed_A,B_count_nodes_left,inter_removed_nodes, A_count_nodes_left, dead, deadlist, figureModel, isolated_n_count_A, isolated_n_count_B = self.graphparameters
        self.G = GtempA  
        if self.ckbxviewnet.isChecked():
            self.lbl4.setText('Drawing')
            self.lbl4.adjustSize()
            QApplication.processEvents()
            if self.timestep > -1:
                print 'the time step is: ', self.timestep
                #identify removed ndoes adn set as inactive
                if self.ckbx1.isChecked():
                    for node in self.graphvis:
                        self.graphvis.node[node]['state'] = self.active
                    removednodes = set(self.graphvis.nodes()) - set(self.G.nodes()) #need to convert to sets as lists cannot be subtracted
                    for node in removednodes:
                        self.graphvis.node[node]['state'] = self.inactive
                else:
                    removednodes = set(self.graphvis.nodes()) - set(self.G.nodes()) #need to convert to sets as lists cannot be subtracted
                    for node in removednodes: #set the state to inactive for relavant nodes 
                        self.graphvis.node[node]['state'] = self.inactive 
                self.figureModel, self.timestep = draw(self.graphvis, self.positions, self.figureModel, self.timestep, self.coloractive, self.colorinactive)
                if self.fullanalysis == True:
                    QApplication.processEvents() #refresh gui  
                    time.sleep(self.timedelay)
            else:
                self.reset()
                self.lbl4.setText('Canceled - Now ready')
                self.lbl4.adjustSize()
                
        if self.fullanalysis == True and self.iterate==True and self.cancel==False:
            self.full_analysis()
        if self.iterate==False:
            print 'analysis completed'
            self.lbl4.setText('Analysis completed')
            self.lbl4.adjustSize()
            QApplication.processEvents() #refresh gui
            self.reset() 
            ok = QMessageBox.information(self, 'Information', "Network resileince analysis successfully completed. Do you want to view the metric graphs?" , '&No','&View Graphs')
            if ok == 1: #if the view graph option is clicked
                self.values = res.outputresults(self.graphparameters, self.parameters)     
                pl.close()
                inputdlg = ViewGraphs()
                self.btnstep.setEnabled(True)#allow the button to be pressed again
                self.btndraw.setEnabled(True)
                ###below enables the dialog to stay open but brings an error                
                inputdlg() 
                
    def updatevalueset(self):
        '''Used to transfer the values to the view graphs class. Called on first line oc class.'''        
        return self.values
            
    def drawview(self):
        '''Draws the network without running any anlysis. Initiated by the Draw button and option in the edit menu.'''
        print 'drawing the network'
        if self.G == None:
            param1 = self.txtparam1.text()
            param2 = self.txtparam2.text()
            param3 = self.txtparam3.text()
            self.buildnetwork(param1, param2, param3)
            if self.G == None:
                return
        self.graphvis = self.G.copy()
        for node in self.graphvis.nodes_iter():  
            self.graphvis.node[node]['state'] = self.active
        if self.positions == None:
            selected = self.visselection()
            self.positions = self.getpositions(selected)
        self.timestep = -1
        self.figureModel = None
        self.figureModel, self.timestep = draw(self.graphvis, self.positions, self.figureModel, self.timestep, self.coloractive, self.colorinactive)
            
    def step_analysis(self):
        ''''Perform the resilience analysis through user control for each node removal process.'''
        print 'performing step analysis'
        if self.timestep>1:        
            self.forthread = self.thread.update()
            self.graphparameters, self.parameters, self.iterate = self.forthread
        else:
            pass
        self.btndraw.setEnabled(False)
        self.btnstep.setEnabled(False)
        self.ckbxviewnet.setEnabled(False)
        self.iterate = True        
        self.timestep += 1
        if self.G == None:
            self.lbl4.setText('Intialising')
            self.lbl4.adjustSize()
            QApplication.processEvents()
            
            param1 = self.txtparam1.text()
            param2 = self.txtparam2.text()
            param3 = self.txtparam3.text()
            self.buildnetwork(param1, param2, param3)
            #create copy for visualisation and set active attribute
            self.graphvis=self.G.copy()
            for node in self.graphvis.nodes_iter():  
                self.graphvis.node[node]['state'] = self.active
            self.parameters = self.getanalysistype()
        if self.ckbxviewnet.isChecked() and self.positions==None: 
            selected = self.visselection()
            self.positions = self.getpositions(selected)
        if self.parameters == None: #needed if network is drawn before doing analysis
            self.parameters = self.getanalysistype()
        self.lbl4.setText('Processing')
        self.lbl4.adjustSize()
        QApplication.processEvents()
        if self.timestep == 0:
            self.graphparameters = res.core_analysis(self.G)
            self.forthread = self.graphparameters, self.parameters, self.iterate
            self.updateUi()
        elif self.timestep == 1:            
            self.thread.setup(self.G, self.iterate, self.parameters, self.graphparameters)
        elif self.timestep>1:
            self.forthread = self.graphparameters, self.parameters, self.iterate
            i, nodes_removed_A, node_count_removed_A, node_count_removed_B, inter_removed_count, GA, GB, GtempA, GtempB,dlist,removed_nodes,subnodes_A, isolated_nodes_A,node_list,nodes_removed_A,to_nodes, from_nodes,numofcomponents, sizeofcomponents, avpathlengthofcomponents, giantcomponentavpathlength, giantcomponentsize, avnodesincomponents, averagedegree, isolated_nodes_B,subnodes_B,path_length_B,subnodes_count_B,isolated_n_count_removed_B,path_length_A,subnodes_count_A,isolated_n_count_removed_A,B_count_nodes_left,inter_removed_nodes, A_count_nodes_left, dead, deadlist, figureModel, isolated_n_count_A, isolated_n_count_B = self.graphparameters
            self.G = GA    
            self.thread.setup(self.G, self.iterate, self.parameters, self.graphparameters)
        else:
            print 'major error'
        self.btnstep.setEnabled(True)
        
    def full_analysis(self):
        '''Runs the analysis of the whole network in one go. Called by the Start button and from the edit menu.'''
        print 'performing complete analysis'
        self.btnstart.setText("Pause")
        if self.pause == True:
            self.running = False
            self.lbl4.setText("Paused")
            self.btnstart.setText("Re-Start")
            return

        self.fullanalysis = True
        self.btnstep.setEnabled(False)
        self.btndraw.setEnabled(False)
        self.ckbxviewnet.setEnabled(False)
        self.disableallckbx()
        self.timestep += 1    
        #identify if just single analsysis or dependent anlysis
        if self.dosingle == False:
            print 'either dependent or interdependent analysis'
            #need to check for two graphs and then build them if they don't exist
        elif self.dosingle == True:
            print 'do a single analysis'
            #run as before
            
        if self.G == None:
            self.lbl4.setText('Intialising')
            self.lbl4.adjustSize()
            QApplication.processEvents()
            param1 = self.txtparam1.text()
            param2 = self.txtparam2.text()
            param3 = self.txtparam3.text()
            self.buildnetwork(param1, param2, param3)
            if self.G <> None:
                #create a copy for the vis and adds attribute state
                self.graphvis=self.G.copy()
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['state'] = self.active
                self.parameters = self.getanalysistype()
            if self.G == None:
                self.reset()
                return
        if self.G1 == None and self.dosingle == False:
            param1 = self.txtparam1b.text()
            param2 = self.txtparam2b.text()
            param3 = self.txtparam3b.text()
            self.G1 = self.buildnetwork(param1, param2, param3)
            if self.G1 <> None:
                #create a copies for the vis and adds attribute state
                self.graphvis1=self.G1.copy()
                for node in self.graphvis1.nodes_iter():  
                    self.graphvis1.node[node]['state'] = self.active
                self.parameters = self.getanalysistype()
            if self.G1 == None:
                self.reset()
                return
                
        if self.parameters == None:
            self.parameters = self.getanalysistype()
            
        self.lbl4.setText('Processing')
        self.lbl4.adjustSize()
        QApplication.processEvents()
        if self.ckbxviewnet.isChecked() and self.positions == None:
            #need to think about how to visualise them - think its got to be as part of a single network-therefore will be slower though
            if self.dosingle == True:                
                selected = self.visselection()
                self.positions = self.getpositions(selected)
            elif self.dosingle == False:
                #assign an attribute called 'graph' which will then be numbered one and two
                for node in self.graphvis1.nodes_iter():  
                    self.graphvis1.node[node]['graph'] = 1
                for node in self.graphvis.nodes_iter():  
                    self.graphvis.node[node]['graph'] = 0
                self.graphvis.add_nodes_from(self.graphvis1.nodes())
                print 'number of nodes in graph vis is: ', self.graphvis.number_of_nodes()
                print 'need to sort visulaisation out for more than one network'                
        
        if self.timestep == 0:
            if self.dosingle == True:
                self.graphparameters = res.core_analysis(self.G)
                self.forthread = self.graphparameters, self.parameters, self.iterate
                self.updateUi()
            elif self.dosingle == False:
                print 'need to sort code for dependent/interdependent analysis and capacity for the links'
                
        if self.timestep > 0:
            if self.dosingle == True:            
                self.forthread = self.graphparameters, self.parameters, self.iterate               
                i, nodes_removed_A, node_count_removed_A, node_count_removed_B, inter_removed_count, GA, GB, GtempA, GtempB,dlist,removed_nodes,subnodes_A, isolated_nodes_A,node_list,nodes_removed_A,to_nodes, from_nodes,numofcomponents, sizeofcomponents, avpathlengthofcomponents, giantcomponentavpathlength, giantcomponentsize, avnodesincomponents, averagedegree, isolated_nodes_B,subnodes_B,path_length_B,subnodes_count_B,isolated_n_count_removed_B,path_length_A,subnodes_count_A,isolated_n_count_removed_A,B_count_nodes_left,inter_removed_nodes, A_count_nodes_left, dead, deadlist, figureModel, isolated_n_count_A, isolated_n_count_B = self.graphparameters
                self.G = GA     
                self.thread.setup(self.G, self.iterate, self.parameters, self.graphparameters)
            elif self.dosingle == False:
                print 'need to sort code for analysis of dependent/interdependent analysis'
    
    def visselection(self):
        '''Loads a GUI where the use selects the method of positioning the nodes.'''
        if self.graph == 'Database':
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)', 'Geographic'
        else:
            items = 'Circle', 'Random', 'Spring', 'Shell', 'Spectral','Circle Tree (bfs)', 'Circle Tree (dfs)', 'Tree (bfs)', 'Tree (dfs)'

        method, ok = QInputDialog.getItem(self, 'Input Dialog', 
            'Select visualisation method:', items)
        if ok == False:
            method = False
        return method  

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
        return self.positions
        
    def getanalysistype(self):
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
            QMessageBox.information(self, 'Information', "Successfully ended process.")
            self.nofilename = True   
            self.G = None
            self.reset()
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
            QApplication.processEvents() #refresh gui
            if self.ckbxsubgraphs.isChecked():
                REMOVE_SUBGRAPHS = True
            if self.ckbxisolates.isChecked():
                REMOVE_ISOLATES = True
            if self.ckbxnoisolates.isChecked():
                NO_ISOLATES = True
                
            parameters = SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName
            return parameters   
    def setfilelocation(self):
        '''Set the file location for the output file.'''
        fileName = QFileDialog.getSaveFileName(self, 'Save File', '.txt')  
        return fileName  
    def networkselectionb(self,text):
        self.graphb = text
        self.dosingle = False
        print 'do single is: ', self.dosingle
        if text == 'None':
            self.txtparam1b.setDisabled(True)
            self.txtparam2b.setDisabled(True)
            self.txtparam3b.setDisabled(True)
            self.dosingle = True
        elif text == 'GNM':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(True)
            self.txtparam1b.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2b.setToolTip('The number of edges. eg.,twice the no. of edges, 124 or 389. Min = 1, Max = 6000') 
            self.validator = QIntValidator(1,2000,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,6000,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
        elif text == 'Erods Renyi':
            self.txtparam1b.setDiasbled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(True)
            self.txtparam1b.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2b.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
            self.validator = QIntValidator(1,2000,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.txtparam2b.setInputMask("B.9")
        elif text == 'Barabasi Albert':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(True)
            self.txtparam1b.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2b.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 50')
            self.validator = QIntValidator(1,2000,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,50,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
        elif text == 'Watts Strogatz':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(False)
            self.txtparam1b.setToolTip('The number of nodes. eg.,34 or 178. Min = 1, Max = 2000')
            self.txtparam2b.setToolTip('Number of neighbours connected to a node. eg., 2 or 15. Min = 1, Max = 200')
            self.txtparam3b.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
            self.validator = QIntValidator(1,2000,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,200,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
            self.txtparam3b.setInputMask("B.9")
        elif text =='Hierarchical random':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(False)
            self.txtparam1b.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2b.setToolTip('The number of children from each new node. eg., 2 or 6. Min = 1, Max = 10')
            self.txtparam3b.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.validator = QIntValidator(1,10,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
            self.txtparam3b.setInputMask("B.9")
        elif text == 'Hierarchical random +':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(False)
            self.txtparam1b.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2b.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 10')
            self.txtparam3b.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.validator = QIntValidator(1,10,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
            self.txtparam3b.setInputMask("B.9")
        elif text == 'Hierarchcial communities':
            self.clear()
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(True)
            self.txtparam1b.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 4')
            self.txtparam2b.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
            self.validator = QIntValidator(1,4,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(0,1,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
        elif text == 'Tree':
            self.clear()            
            self.txtparam1b.setDisabled(False)
            self.txtparam2b.setDisabled(False)
            self.txtparam3b.setDisabled(True)
            self.txtparam1b.setToolTip('The number of child nodes per parent. eg., 3 or 5. Min = 1, Max = 50')
            self.txtparam2b.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6. Min = 1, Max = 10')
            self.validator = QIntValidator(1,50,self.txtparam1b)       
            self.txtparam1b.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2b)       
            self.txtparam2b.setValidator(self.validator)
        elif text == 'Database':
            self.clear()
            self.txtparam1b.setEnabled(False)
            self.txtparam2b.setEnabled(False)
            self.txtparam3b.setEnabled(False)
        elif text == 'Lists':   
            self.clear()
            self.txtparam1b.setEnabled(True)
            self.txtparam2b.setEnabled(True)
            self.txtparam3b.setEnabled(False)
            self.txtparam1b.setToolTip('The list if nodes for the network eg., (1,2,3,4)')
            self.txtparam2b.setToolTip('The list of edges for the network eg., ((1,2),(1,4),(1,3),(2,3),(3,4))')
            
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
            self.validator = QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,6000,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
        elif text == 'Erdos Renyi':
            self.clear()
            self.txtparam3.setEnabled(False)
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('Probability of edge creation eg.,0.4 or 0.7')
            self.validator = QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.txtparam2.setInputMask("B.9")
        elif text == 'Watts Strogatz':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg.,34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('Number of neighbours connected to a node. eg., 2 or 15. Min = 1, Max = 200')
            self.txtparam3.setToolTip('Probability of being rewired eg.,0.4 or 0.7')
            self.validator = QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,200,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Barabasi Albert':
            self.clear()
            self.txtparam3.setEnabled(False)
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam1.setToolTip('The number of nodes. eg., 34 or 178. Min = 1, Max = 2000')
            self.txtparam2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 50')
            self.validator = QIntValidator(1,2000,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,50,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
        elif text == 'Hierarchical Random':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2.setToolTip('The number of children from each new node. eg., 2 or 6. Min = 1, Max = 10')
            self.txtparam3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.validator = QIntValidator(1,10,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Hierarchical Random +':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(True)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 10')
            self.txtparam2.setToolTip('The number of edges to attach to a new node. eg., 3 or 6. Min = 1, Max = 10')
            self.txtparam3.setToolTip('The probability of extra connections. eg., 0.3 or 0.7')
            self.validator = QIntValidator(1,10,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
            self.txtparam3.setInputMask("B.9")
        elif text == 'Hierarchical Communities':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(False)
            self.txtparam1.setToolTip('The number of levels. eg., 2 or 4. Min = 1, Max = 4')
            self.txtparam2.setToolTip('The number of type of community, 0 for square, 1 for triangle.')
            self.validator = QIntValidator(1,4,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(0,1,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
        elif text == 'Tree':
            self.clear()
            self.txtparam1.setEnabled(True)
            self.txtparam2.setEnabled(True)
            self.txtparam3.setEnabled(False)
            self.txtparam1.setToolTip('The number of child nodes per parent. eg., 3 or 5. Min = 1, Max = 50')
            self.txtparam2.setToolTip('The number of levels in the tree (excluding the source level). eg., 3 or 6. Min = 1, Max = 10')
            self.validator = QIntValidator(1,50,self.txtparam1)       
            self.txtparam1.setValidator(self.validator)
            self.validator = QIntValidator(1,10,self.txtparam2)       
            self.txtparam2.setValidator(self.validator)
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
            ####open textbox for inputs, then display in list box
            ####could replace txtbox with a edit button, which when clicked opens window            
                        
    #slot to be called when start button is clicekd
    def buildnetwork(self, param1, param2, param3):
        '''Builds the network using the user selected option as well as checking for the correct input values. If graph not built, G=None'''
        print 'building network'

        self.G = None 
        #build network
        if self.graph == 'Watts Strogatz': #ws 
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            if param3 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                return            
            try:        
                param1 = int(param1)
            except:        
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number of connected neighbours, is in an incorrect format.")
                return
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of rewiring, is in an incorrect format.")
                return
            if param2 >= param1:
                QMessageBox.warning(self, 'Error!', "Input parameter 2 needs to be less than input parameter 1.")
                return
            if param3 <0 or param3 >1:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3 is an incorrect value.")
                return
            self.G = nx.watts_strogatz_graph(param1, param2, param3)
            if nx.is_connected(self.G)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase parameter 2 or decrease parameter 3.", '&OK')                  
                #would like to put a retry button on the message box, but not sure how we would know how to restart the analysis after doing this, as can be called from two places
                return #exit sub
        elif self.graph == 'GNM': #gnm
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")             
                return        
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            '''
            maxno = (param1)*(param1/2)
            if maxno < param2:
                QMessageBox.warning(self, 'Warning!', "Warning. This network may have duplicate edges or edges which begin and end at the same node.")
                #sys.exitfunc() 
                return
            else:
            '''
            self.G = nx.gnm_random_graph(param1, param2)
            if nx.is_connected(self.G)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                self.G = None #needs to reset G to none when graph is unconnected                
                self.btnstep.setEnabled(True)#allow the button to be pressed again                            
                return #exit sub
        elif self.graph == 'Barabasi Albert': #ba
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return           
            try:
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            self.G = nx.barabasi_albert_graph(param1, param2)
            if nx.is_connected(self.G)==False:
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.graph == 'Erdos Renyi': #er
            if param1 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                return
            if param2 == '':  
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of nodes, is in an incorrect format.")
                return            
            try:            
                param2 = float(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the nuber of edges, is in an incorrect format.")
                return
            if param2 <0 or param2 >1:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2 is an incorrect value.")
                return
            self.G = nx.erdos_renyi_graph(param1, param2)
            if nx.is_connected(self.G)==False:
                #bring up error message box
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please try again or increase the number of edges.")
                return #exit sub
        elif self.graph == 'Database': #database connection  -currently only allows a single network
            self.getdbnetwork()
            if self.G == None:
                return
        elif self.graph == 'Hierarchical Random': #hr
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            if param3 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                 return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return 
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of new edges, is in an incorrect format.")
                return
            self.G = customnets.hr(param1,param2,param3)
        elif self.graph =='Hierarchical Random +': #ahr
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            if param3 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 3 is blank.")
                 return                        
            try:          
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return 
            try:
                param3 = float(param3)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 3, the probability of new edges, is in an incorrect format.")
                return
            self.G = customnets.ahr(param1,param2,param3)
        elif self.graph == 'Hierarchical Communities': #hc
            #param1 = level
            #param2 = square/tri
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            try:          
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is in an incorrect format.")
                return  
            try:          
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2,the type of sructure, is in an incorrect format.")
                return   
            if param2 >= 2:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2,the type of sructure, is too high. It should be either 0 or 1.")
            
            if param2 == 0:
                if param1 == 0 or param1 >= 6:
                    QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is incorrect. Should be between 1 and 5.")
                else:
                    self.G = customnets.square(param1)
            elif param2 == 1:
                if param1 == 0 or param1 >= 5:
                    QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of levels, is incorrect. Should be between 1 and 4.")
                else:
                    self.G = customnets.tri(param1)
            else:
                print 'There has been an error'
           
        elif self.graph == 'Tree': #trees
            #param 1 is the number of new nodes
            #param 2 is the number of level excluding the source
            if param1 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 1 is blank.")
                 return
            if param2 == '':  
                 QMessageBox.warning(self, 'Error!', "Input for parameter 2 is blank.")
                 return
            try:        
                param1 = int(param1)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 1, the number of child nodes per parent, is in an incorrect format.")
                return  
            try:        
                param2 = int(param2)
            except:
                QMessageBox.warning(self, 'Error!', "Input for parameter 2, the number levels, is in an incorrect format.")
                return  
            self.G=nx.balanced_tree(param1, param2)
        elif self.graph == 'Lists': #lists
            #param1 is a list of nodes  #param2 is a list of egdes
            #need to convert the input strings to lists with integers in the correct format
            if param1 =='' or param2=='':
                QMessageBox.warning(self, 'Error!', "Graph could not be created. Please enter node and edge lists or select a different option.")
                                
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
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The node list does not fit the required format.")
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
                QMessageBox.warning(self, 'Error!', "Graph could not be created. The edge list is not in the correct formart.")            
                return #exit sub
        else: 
            QMessageBox.warning(self, 'Error!', "Error! Please try again.")          
            return #exit sub
        self.param1 = param1 #make these freely accessable
        self.param2 = param2
        self.param3 = param3
        if self.G == None:
            self.cancel = True
            return
        else:
            print 'built network successfully, has ', self.G.number_of_nodes(), ' nodes'
        
        
class Worker(QThread):

    def __init__(self, parent = None):
        print '***the thread is running***'
        QThread.__init__(self, parent)     
        graphparameters = None
        parameters = None
        iterate = True
        self.forthread = graphparameters, parameters, iterate
    def __del__(self):
        self.exiting = True
        self.wait() 
    def setup(self, G, iterate, parameters, graphparameters):
        '''Controls the processes run in the work thread and starts it.'''
        self.G = G
        self.iterate = iterate
        self.parameters = parameters
        self.graphparameters = graphparameters
        self.start() 
    def run(self):
        '''Runs the analysis by calling the function in the resilience module.'''
        # Note: This is never called directly. Always use .start to start the workthread.
        print 'running the analysis'
        self.graphparameters, self.iterate = res.step(self.graphparameters, self.parameters, self.iterate)
        #self.emit(SIGNAL("finished()"),)
        self.forthread = self.graphparameters, self.parameters, self.iterate
    def update(self):
        ''''''
        return self.forthread

def draw(G, positions, figureModel, timestep, coloractive, colorinactive):
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
    drawnet(G, positions, timestep, coloractive, colorinactive)   
    pl.show()  
    figureModel.canvas.manager.window.update()  #gets error here when the window is closed by whatever means  
      
    return figureModel, timestep
      
def drawnet(G, positions, timestep, coloractive, colorinactive):
    '''Draws the network.'''
    inactivenodes=[]
    activenodes=[]
    #inactiveedges=[]
    #activeedges=[]
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
    nx.draw_networkx_nodes(G, positions, node_size= size, node_color = str(coloractive), with_labels=True)
    nx.draw_networkx_edges(G, positions, edge_width=6, edge_color = str(coloractive))
    if timestep <> -1:
        pl.title('iteration = ' + str(timestep))
    timestep+=1

    for node in G.nodes_iter():
        if G.node[node]['state'] == 0: #inactive
            inactivenodes.append(node)
            edgelist = G.edges(node)
            nx.draw_networkx_edges(G, positions, edge_width=6.1, edgelist = edgelist, edge_color = str(colorinactive))
        elif G.node[node]['state']== 1: #active
            activenodes.append(node)
            edgelist = G.edges(node)
            #nx.draw_networkx_edges(G, positions, edgelist = edgelist, edge_width = 7,edge_color = 'r')
            #activeedges.append(G.edges(node))

    #nx.draw(G,positions,node_size=20,alpha=0.5,node_color="blue", with_labels=False) #this is the original method
    #nx.draw(G, positions, nodelist = activenodes, node_color = 'r')#, with_labels=False)
    #nx.draw(G, positions, nodelist = inactivenodes, node_color = 'b')#, with_labels=False)
    #nx.draw_networkx_nodes(G, positions, nodelist = activenodes, node_color = 'g')
    nx.draw_networkx_nodes(G, positions, node_size=size, nodelist = inactivenodes, node_color = str(colorinactive), with_labels=True)   
    #nx.draw_networkx_edges(G, positions, edgelist = inactiveedges, edge_color = 'b')
    #nx.draw_networkx_edges(G, positions, edgelist = activeedges, edge_color = 'r')
    
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
        
        
        
        
        
        
        
        
        
        