"""
Show network condition.

CHANGELOG:
2021-03-01 Incorporated newer iperf3 version that flushes output buffer for realtime monitoring
2021-03-02 Fixed bug in library in mkColor() and reported it on github.
2021-03-08 Used signals and slots and worker class to update the gui from the worker.
2021-03-09 Moved ookla and iperf executables inside the networktool folder so they can be picked up by the packager
           Installed pyinstaller (pip install pyinstalller)
           Installed innosetup (download from web)
           Created scripts for pyinstaller and innosetup
           Created network icon
2021-03-10 Autodetect of iperfserver IP in subnet. Inspired by: https://www.tutorialspoint.com/python_penetration_testing/python_penetration_testing_network_scanner.htm
2021-03-11 Implemented sequential running of upload and download test
2021-03-12 Kill all threads upon exit and ESC key
           Kill all processes upon terminating the workers
2021-03-14 Added numerical metrics: min avg max
2021-03-27 Added changing network diagrams based on interface status
2021-03-29 Splitted code over 3 files
2021-04-01 Changed ping thread into a workerclass
2021-10-11 Linked X axes
           Added log widget and logger
           Upgraded to PyQt6
           Removed pyqtchart brush workaround as my bugreport is now fixed in the release
           Fixed iperfserver autodetect

TODO:
set a background image. use qml markup language for gui? or do a quick and dirty?

PREREQUISITES:
pip install PyQt6 numpy pyqtgraph psutil scapy

PACKAGING:
First package python with pyinstaller
PS R:\project\networkTool> pyinstaller.exe --noconfirm 'networktool 3.spec'
This will create a compiled version in "build" directory

Then run innosetup script by doubleclicking the .iss file
'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' "inno setup script.iss"
This will create a package in "Output" directory

INSTALLATION:
Then install the setupfile as administrator.
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
#from PyQt5 import QtSvg
from PyQt6.QtCore import *
from PyQt6 import QtCore, uic #, QtMultimedia
from numpy import true_divide
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from tests import *
from settings import SettingsDialog
from about import AboutDialog
from time import sleep
#from socket import gethostname
import logging
from logger import QTextEditLogHandler

COMPANY_NAME = "spoorendonk.com"
APPLICATION_NAME = "Network tool"

print('python version', sys.version)
print('pyqtgraph version', pg.__version__)
print('qt version', pg.Qt.VERSION_INFO)

pg.setConfigOptions(antialias=True)

#pg.functions.mkColorOrig = pg.functions.mkColor

# the original mkColor() doesn't support brushes and throws an error when a brush is passed to the legend.
# this just returns a transparent color to get rid of the problem.
# the bug has been solved in a recent version of PyQtChart so this workaround can be removed after a while.
#def mkColorNew(*args):
#    #print('make color')
#    if len(args) == 1 and isinstance(args[0], QtGui.QBrush): # handle brushes
#        return QtGui.QColor('#00000000') # transparent
#    return pg.functions.mkColorOrig(*args) # call the original function

#pg.functions.mkColor = mkColorNew


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        #print('scale: ', scale)

        format = '%H:%M:%S'
        return [datetime.datetime.fromtimestamp(value).strftime(format) for value in values]



class Stats():
    layout = None
    runIn = 6  # [seconds] skip the first seconds

    def __init__(self):
        """numerical stats"""

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # all that margin stuff is an effort to get the text more compact (didn't succeed)

        minLabel = QLabel("min")
        minLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        minLabel.setToolTip('The minimum excludes a run-in period of %d seconds' % self.runIn)
        avgLabel = QLabel("avg")
        avgLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        avgLabel.setStyleSheet('padding :0px; margin: 0px; border: 0px')
        avgLabel.setToolTip('The average excludes a run-in period of %d seconds' % self.runIn)
        maxLabel = QLabel("max")
        maxLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        maxLabel.setToolTip('The maximum excludes a run-in period of %d seconds' % self.runIn)
        curLabel = QLabel("last")
        curLabel.setToolTip('The last measured value')
        curLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(maxLabel, 1, 0)
        self.layout.addWidget(avgLabel, 2, 0)
        self.layout.addWidget(minLabel, 3, 0)
        self.layout.addWidget(curLabel, 4, 0)

        downLabel = QLabel("Down")
        downLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        downLabel.setToolTip('Speed in Mbps')
        self.maxDownLabel = QLabel("-")
        self.maxDownLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.avgDownLabel = QLabel("-")
        self.avgDownLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.avgDownLabel.setStyleSheet('padding: 0px; margin: 0px; border: 0px')
        self.minDownLabel = QLabel("-")
        self.minDownLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.curDownLabel = QLabel("-")
        self.curDownLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(downLabel, 0, 1)
        self.layout.addWidget(self.maxDownLabel, 1, 1)
        self.layout.addWidget(self.avgDownLabel, 2, 1)
        self.layout.addWidget(self.minDownLabel, 3, 1)
        self.layout.addWidget(self.curDownLabel, 4, 1)

        upLabel = QLabel("Up")
        upLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upLabel.setToolTip('Speed in Mbps')
        self.maxUpLabel = QLabel("-")
        self.maxUpLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.maxUpLabel.setStyleSheet('padding: 0px; margin: 0px; border: 0px;')
        self.avgUpLabel = QLabel("-")
        self.avgUpLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.avgUpLabel.setStyleSheet('padding: 0px; margin: 0px; border: 0px;')
        self.minUpLabel = QLabel("-")
        self.minUpLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.curUpLabel = QLabel("-")
        self.curUpLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(upLabel, 0, 2)
        self.layout.addWidget(self.maxUpLabel, 1, 2)
        self.layout.addWidget(self.avgUpLabel, 2, 2)
        self.layout.addWidget(self.minUpLabel, 3, 2)
        self.layout.addWidget(self.curUpLabel, 4, 2)



    def update(self, series):
        if 'down' in series.name.lower():
            self.updateSeries(self.maxDownLabel, self.avgDownLabel, self.minDownLabel, self.curDownLabel, series.value, series.timestamp)
        else:
            self.updateSeries(self.maxUpLabel, self.avgUpLabel, self.minUpLabel, self.curUpLabel, series.value, series.timestamp)

    def clear(self):
        for widget in (self.maxDownLabel, self.avgDownLabel, self.minDownLabel, self.curDownLabel, self.maxUpLabel, self.avgUpLabel, self.minUpLabel, self.curUpLabel):
            widget.setText('-')

    def updateSeries(self, labelMax, labelAvg, labelMin, labelCur, speed, time):
        """
        Max calculation:
        The tests tend to have a runin period that needs to be removed.
        Therefore, after each NaN we ommit the first x seconds.
        """

        max = np.nan
        min = np.nan
        avgSum = 0
        avgCount = 0
        avg = 0
        lastNanTime = np.nan
        for i in range(len(speed)-1):
            if np.isnan(speed[i]):
                lastNanTime = time[i]
            elif (np.isnan(lastNanTime) or time[i]>lastNanTime+self.runIn) and not np.isnan(speed[i+1]):
                if np.isnan(max) or speed[i]>max:
                    max = speed[i]
                if np.isnan(min) or speed[i]<min:
                    min = speed[i]
                avgSum += speed[i]
                avgCount += 1
        
        # finally calculate the average and update the supplied labels.
        if avgCount > 0:
            avg = avgSum / avgCount

            labelMax.setText("%d" % max)
            labelAvg.setText("%d" % avg)
            labelMin.setText("%d" % min)

        if len(speed) > 0:
            if not np.isnan(speed[-1]):
                cur = speed[-1]
                labelCur.setText("%d" % cur)
            else:
                labelCur.setText('-')


class MainWindow(QMainWindow):
    stop = pyqtSignal()

    def __init__(self, *args, **kwargs):
        #global app
        super(MainWindow, self).__init__(*args, **kwargs)

        self.show()

        self.dataStore = DataStore()

        self.threadpool = QThreadPool()
        self.curves = {}

        self.settings = QSettings(COMPANY_NAME, APPLICATION_NAME)
        print(self.settings.fileName())
        self.settingsDialog = SettingsDialog(self, self.settings)
        self.aboutDialog = AboutDialog(self)

        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.setWindowIcon(QtGui.QIcon('networktool.ico'))
        self.resize(self.settings.value("size", QSize(1024, 768)))
        self.move(self.settings.value("pos", QPoint(200, 200)))

        # move it to the center of the screen.
        qtRectangle = self.frameGeometry()
        centerPoint = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        

        wid = QWidget(self)  # You can't set a QLayout directly on the QMainWindow. You need to create a QWidget and set it as the central widget on the QMainWindow and assign the QLayout to that.
        self.setCentralWidget(wid)
        layout = QGridLayout()
        wid.setLayout(layout)

        menus = self.setupMenus() # setup the menus in row 0 of the layout
        self.setupBrushes()
        charts = self.setupCharts()
        hl1, vl = self.setupNetworkStats()

        handler = QTextEditLogHandler()
        # You can format what is printed to text box
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        handler.widget.setFixedHeight(250)

        

        layout_computerInfo = self.setupComputerInfo()

        # row 0
        layout.addWidget(menus, 0, 0, 1, 3)
        # row 1
        layout.addLayout(layout_computerInfo, 1, 0)
        layout.addLayout(hl1, 1, 1)
        layout.addLayout(vl, 1, 1)
        layout.addWidget(handler.widget, 1, 2)
        # row 2
        layout.addWidget(charts, 2, 0, 1, 3)

        layout.setRowStretch(2,1)

        self.statusBar()
        #self.statusBar().setStyleSheet("color: #a0a0a0")
        self.statusBar().showMessage('Select a test from the menu')

        self.show()
        self.setWindowTitle('Realtime bandwidth test')

        # start monitoring some stuff in the background, such as connection state
        worker = BackgroundPoller()
        worker.signals.activeInterface.connect(self.updateBackground)
        worker.signals.ssid.connect(self.updateSSID)
        #self.stop.connect(worker.stop)
        QCoreApplication.instance().aboutToQuit.connect(worker.stop)
        self.threadpool.start(worker)

        self.autoRangeTimer  = QtCore.QTimer(self)
        self.autoRangeTimer.setInterval(50)          # Throw event timeout with an interval in ms
        self.autoRangeTimer.timeout.connect(self.autoRange2) # each time timer counts a second, call self.blink
        self.stop.connect(self.autoRangeTimer.stop) # stop the autoranging of the charts when pressing ESC

    def setupCharts(self):
        # the linking of the xaxes in combination with autoranging gave very flickery graphics.
        # also the scaling 'auto' changed to manual for only one chart
        # It's resolved by disabling the autoranging and calling a setXrange() periodically.

        self.min = -1 # minimum x axis value
        self.max = -1 # maximum x axis value

        pg.setConfigOption('background', '#202020')
        pg.setConfigOption('foreground', '#a0a0a0')

        charts=pg.GraphicsLayoutWidget()
        charts.setAntialiasing(True)
        # Simplest approach -- update data in the array such that plot appears to scroll
        self.p1 = charts.addPlot(title='Latency', labels={'left': 'roundtrip time [ms]', 'bottom': 'wallclock time'}, axisItems={'bottom': TimeAxisItem(orientation='bottom')}, name='Latency')
        charts.nextRow()  # next chart on new row
        self.p2 = charts.addPlot(title='Bandwidth', labels={'left': 'bandwidth [Mbps]', 'bottom': 'wallclock time'}, axisItems={'bottom': TimeAxisItem(orientation='bottom')}, name='Bandwidth')

        # I don't know if this needs to be linked both ways
        self.p1.setXLink(self.p2)
        #self.p2.setXLink(self.p1)
 

        self.p1.addLegend()
        self.p1.showGrid(x=True, y=True, alpha = 0.3)

        # overload the setRange() in order to fix only ymin to 0
        # inspiration: https://groups.google.com/g/pyqtgraph/c/TxIj3mc49HEr
        def setRange1(rect=None, xRange=None, yRange=None, *args, **kwds):
            if not kwds.get('disableAutoRange', True):
                if yRange is not None:
                    yRange[0] = 0
            pg.ViewBox.setRange(vb1, rect, xRange, yRange, *args, **kwds)

        vb1 = self.p1.vb
        vb1.setRange=setRange1
        vb1.setMouseEnabled(x=True, y=False)  # only allow zoom on time axis

        

        
        self.p2.addLegend()
        self.p2.showGrid(x=True, y=True, alpha = 0.3)

        

        
        def setRange2(rect=None, xRange=None, yRange=None, *args, **kwds):
            if not kwds.get('disableAutoRange', True):
                if yRange is not None:
                    yRange[0] = 0
            pg.ViewBox.setRange(vb2, rect, xRange, yRange, *args, **kwds)

        vb2 = self.p2.vb
        vb2.setRange=setRange2
        vb2.setMouseEnabled(x=True, y=False) # only allow zoom on time axis

        #vb1.linkView(pg.ViewBox.XAxis, vb2)
        self.p1.vb.enableAutoRange(pg.ViewBox.XAxis, False) # only allow autorange on y axis
        self.p2.vb.enableAutoRange(pg.ViewBox.XAxis, False)
        return charts

    def setupBrushes(self):
        #make a nice gradient below the curve
        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#00000001'))
        grad.setColorAt(0.10, pg.mkColor('#00ff0050')) # green
        grad.setColorAt(0.20, pg.mkColor('#ffff0050')) # yellow
        grad.setColorAt(0.40, pg.mkColor('#ffff0070')) # yellow
        grad.setColorAt(0.70, pg.mkColor('#ff000080')) # red
        self.pingBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#00ff0001'))
        grad.setColorAt(0.9, pg.mkColor('#00ff0050')) # green
        self.greenBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#a0ffa001'))
        grad.setColorAt(0.9, pg.mkColor('#a0ffa050')) # light green
        self.lightGreenBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#0000ff01'))
        grad.setColorAt(0.9, pg.mkColor('#2020ff90')) # blue
        self.blueBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#8080ff01'))
        grad.setColorAt(0.9, pg.mkColor('#8080ff90')) # light blue
        self.lightBlueBrush = QtGui.QBrush(grad)

    def setupMenus(self):
        quitAct = QAction('&Quit', self)
        quitAct.setShortcut('Ctrl+Q')
        quitAct.setStatusTip('Quit the application')
        quitAct.triggered.connect(QCoreApplication.instance().quit)

        pingAct = QAction('Ping latency test', self)
        pingAct.setShortcut('Ctrl+P')
        pingAct.triggered.connect(self.startPings)

        ooklaAct = QAction('Ookla internet bandwidth test - alternating', self)
        ooklaAct.setShortcut('Ctrl+O')
        ooklaAct.triggered.connect(self.startOokla)

        iperfBAct = QAction('Iperf3 LAN bandwidth test - bidirectional', self)
        iperfBAct.setShortcut('Ctrl+I')
        iperfBAct.triggered.connect(self.startIperfBidirectional)

        iperfUAct = QAction('Iperf3 LAN bandwidth test - upload', self)
        iperfUAct.setShortcut('Ctrl+U')
        iperfUAct.triggered.connect(self.startIperfUpload)

        iperfDAct = QAction('Iperf3 LAN bandwidth test - download', self)
        iperfDAct.setShortcut('Ctrl+D')
        iperfDAct.triggered.connect(self.startIperfDown)

        iperfAAct = QAction('Iperf3 LAN bandwidth test - alternating', self)
        iperfAAct.setShortcut('Ctrl+A')
        iperfAAct.triggered.connect(self.startIperfAlternating)

        stopAct= QAction('Stop all tests', self)
        stopAct.setShortcut('ESC')
        stopAct.triggered.connect(self.stop.emit)

        clearAct = QAction('Clear output', self)
        clearAct.setShortcut('Ctrl+R')
        clearAct.triggered.connect(self.clear)

        settingsAct = QAction('Settings', self)
        settingsAct.triggered.connect(self.settingsDialog.exec)
        
        exportAct = QAction('Export output', self)
        exportAct.setShortcut('Ctrl+E')
        exportAct.triggered.connect(self.export)

        aboutAct = QAction('About', self)
        aboutAct.triggered.connect(self.aboutDialog.exec)

        devAct = QAction('Development test', self)
        devAct.setShortcut('Ctrl+T')
        devAct.triggered.connect(self.dev)

        # create menu
        menubar = QMenuBar()
        
        actionFile = menubar.addMenu("Application")
        #actionFile.addSeparator()
        actionFile.addAction(quitAct)
        actionFile.addAction(stopAct)
        actionFile.addAction(clearAct)
        actionFile.addAction(settingsAct)
        actionFile.addAction(exportAct)

        actionTest = menubar.addMenu("Test")
        actionTest.addAction(ooklaAct)
        actionTest.addAction(pingAct)
        actionTest.addAction(iperfBAct)
        actionTest.addAction(iperfUAct)
        actionTest.addAction(iperfDAct)
        actionTest.addAction(iperfAAct)

        #menubar.addMenu("View")
        actionHelp = menubar.addMenu("Help")
        #actionHelp.addAction(helpAct)
        actionHelp.addAction(aboutAct)
        actionHelp.addAction(devAct)
        return menubar

    def setupComputerInfo(self):
        # define interesting info about the computer and network interface
        self.lblDate = QLabel("Date: " + datetime.date.today().strftime('%Y-%m-%d'))
        self.lblComputerName = QLabel("Computer name: " + socket.gethostname() + " [" + get_own_ip()+"]")
        self.lblConnection = QLabel("Connection")  # gets updated in the background
        self.lblSSID = QLabel("SSID: " + getSSID())  # gets updated in the background
        
        vlayout = QVBoxLayout()
        vlayout.addStretch(0)
        vlayout.addWidget(self.lblDate)
        vlayout.addWidget(self.lblConnection)
        vlayout.addWidget(self.lblComputerName)
        vlayout.addWidget(self.lblSSID)
        vlayout.addStretch(0)
        return vlayout

    def setupNetworkStats(self):
        #
        # hl1
        # vl
        #   hl2

        #self.stats = []
        self.internetStats=Stats()
        self.lanStats=Stats()

        # load a bunch of images that show the connection state graphically
        self.wiredImg        = QPixmap('resources/networktool - wired.png')
        self.wifiImg         = QPixmap('resources/networktool - wifi.png')
        self.lifiImg         = QPixmap('resources/networktool - lifi.png')
        self.disconnectedImg = QPixmap('resources/networktool - disconnected.png')

        self.networkLabel = QLabel(self)
        self.networkLabel.setPixmap(self.wiredImg)
        self.networkLabel.setScaledContents(True)
        self.networkLabel.setFixedHeight(250)
        self.networkLabel.setFixedWidth(600)

         # show a horizontally centered image of the network
        hl1 = QHBoxLayout()
        hl1.addStretch()
        hl1.addWidget(self.networkLabel)
        hl1.addStretch()


        # show two tables with networkspeeds with a fixed distance so that it nicely
        # overlays on the graphic.
        hl2 = QHBoxLayout()
        hl2.addStretch(1)
        hl2.addLayout(self.lanStats.layout, 0)
        hl2.addSpacing(100)
        hl2.addLayout(self.internetStats.layout, 0)
        hl2.addStretch(1)
       
        # position the tables vertically
        vl = QVBoxLayout()
        vl.addSpacing(100)
        vl.addLayout(hl2)
        vl.addSpacing(12)

        return hl1, vl

    def showError(self, err):
        print("ERROR", err)
        self.error_dialog = QMessageBox()
        self.error_dialog.setWindowTitle('Error')
        self.error_dialog.setText(err)
        self.error_dialog.setIcon(QMessageBox.Icon.Critical)
        self.error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        x = self.error_dialog.exec()

    # event : QCloseEvent
    def closeEvent(self, event):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        event.accept()
        print('Closing main window. Settings are stored.')


    def showStatus(self, status):
        self.statusBar().showMessage(status)
        logging.debug(status)

    def updateSSID(self, ssid):
        lbl = 'SSID: WiFi not connected'
        if ssid != '':
            lbl = 'SSID: ' + ssid
        self.lblSSID.setText(lbl)


    def updateBackground(self, state):
        """Update the background image, such that it shows the active state"""
        description = getInterface(state).Description
        self.lblConnection.setText('Interface: %s - %s' % (state, description))

        state = state.lower()
        print(">%s<" % state)

        if 'ax88179' in description.lower():  # USB Ethernet, this is assumed to be lifi. Bit lame, should look at other strings.
            self.networkLabel.setPixmap(self.lifiImg)
        elif state == "disconnected":
            self.networkLabel.setPixmap(self.disconnectedImg)
        elif state == "wi-fi" or state == "wifi":
            self.networkLabel.setPixmap(self.wifiImg)
        else:
            self.networkLabel.setPixmap(self.wiredImg)

        self.lblDate.setText("Date: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    def startPings(self):
        self.lastPingWarning = 0

        # order is important here. The first one is at the back.
        self.startPing('ping1', 'loss1', self.settings.value('ping_host_1'))
        #self.startPing('ping2', 'loss2', self.settings.value('ping_host_2'))
        self.startPing('pingFirstHop', 'lossFirstHop', getFirstHop())


    def startPing(self, name, lossName, host):
        self.autoRangeTimer.start()
        if not name in self.curves.keys():
            if name == 'pingFirstHop':
                self.curves[name] = self.p1.plot(pen=pg.mkPen(color='y', width=2), fillLevel=0, brush=self.pingBrush,
                                                 name=name+' '+host)
            else:
                self.curves[name] = self.p1.plot(pen=pg.mkPen(color='w', width=2), fillLevel=0, brush=self.pingBrush,
                                                 name=name + ' ' + host)
        #else:
        #    self.curves[name].setData(name=name + ' ' + host) # this does not work (bug in pyqtgraph) https://github.com/pyqtgraph/pyqtgraph/issues/1000
        logging.debug('Starting ping for '+name)
        worker = PingWorker(self.dataStore.data[name], self.dataStore.data[lossName], host)
        worker.signals.error.connect(self.showError)
        worker.signals.update.connect(self.updatePing)
        worker.signals.status.connect(self.showStatus)
        self.stop.connect(worker.stop)
        QCoreApplication.instance().aboutToQuit.connect(worker.stop)
        self.threadpool.start(worker)

    def autoRange(self, timestamps):
        if len(timestamps)>0:
            if self.min == -1:
                self.min = timestamps[0]
            else:
                self.min = min(self.min, timestamps[0])

            if self.max == -1:
                self.max = timestamps[-1]
            else:
                self.max = max(self.max, timestamps[-1])

    def autoRange2(self):
        if self.min > 0 and self.max > 0:
            self.p1.vb.setXRange(self.min, timestamp())
            #self.p2.vb.setXRange(self.min, self.max) # the axes are linked so we only need to set the range on one of them




    def updatePing(self, series):
        if series.name in self.curves.keys():
            self.curves[series.name].setData(series.timestamp, series.value, connect=np.array(series.connect))
            self.autoRange(series.timestamp)

        if len(series) > 0:
            # if latency > 200ms
            ms = series.value[-1]  # get last value
            if ms > 100:
                print('SLOW')
                # if sound effect is at least 1 minute ago
                if timestamp() - self.lastPingWarning > 60:
                    self.lastPingWarning = timestamp()
                    # If you're using Qt Multimedia to play sounds in your application you could switch over to the Python library playsound instead. (for pyqt6)
                    # This is across-platform single-function library which will play sounds for you.
                    # play sound
                    url = QtCore.QUrl.fromLocalFile(os.path.join('resources', 'slowdown.wav'))
                    #content = QtMultimedia.QMediaContent(url)
                    #player = QtMultimedia.QMediaPlayer()
                    #player.setMedia(content)
                    #player.setVolume(50)
                    #player.play()
                    #sleep(2)  # that is nasty but seems required. We should play in a separate thread.

    def dev(self):
        #self.curves['pingFirstHop'].setPos(timestamp(), 0)
        logging.debug('damn, a bug')
        logging.info('something to remember')
        logging.warning('that\'s not right')
        logging.error('foobar')

    def startOokla(self):
        self.autoRangeTimer.start()
        if 'ooklaDown' not in self.curves.keys():
            self.curves['ooklaDown'] = self.p2.plot(pen=pg.mkPen(color='#9090ff', width=2), fillLevel=0, brush=self.lightBlueBrush, name='internet download')
        if 'ooklaUp' not in self.curves.keys():
            self.curves['ooklaUp'] = self.p2.plot(pen=pg.mkPen(color='#2020ff', width=2), fillLevel=0, brush=self.blueBrush, name='internet upload')

        worker = OoklaWorker(self.dataStore.data['ooklaDown'], self.dataStore.data['ooklaUp'])
        worker.signals.error.connect(self.showError)
        worker.signals.update.connect(self.updateOokla)
        worker.signals.status.connect(self.showStatus)
        self.stop.connect(worker.stop)
        QCoreApplication.instance().aboutToQuit.connect(worker.stop)
        self.threadpool.start(worker)


    def updateOokla(self, series):
        
        if series.name in self.curves.keys():
            self.curves[series.name].setData(series.timestamp, series.value, connect=np.array(series.connect))
            #logging.debug('update %s' % series.name)
            self.autoRange(series.timestamp)
        self.internetStats.update(series)



    def startIperf(self, direction):
        self.autoRangeTimer.start()
        if 'iperfDown' not in self.curves.keys() and direction in 'dba':
            self.curves['iperfDown'] = self.p2.plot(pen=pg.mkPen(color='#a0ffa0', width=2), fillLevel=0, brush=self.lightGreenBrush, name='LAN download')
        
        if 'iperfUp' not in self.curves.keys() and direction in 'uba':
            self.curves['iperfUp'] = self.p2.plot(pen=pg.mkPen(color='#00ff00', width=2), fillLevel=0, brush=self.greenBrush, name='LAN upload')

        worker = IperfWorker(direction, self.dataStore.data['iperfDown'], self.dataStore.data['iperfUp'])
        worker.signals.error.connect(self.showError)
        worker.signals.update.connect(self.updateIperf)
        worker.signals.status.connect(self.showStatus)
        self.stop.connect(worker.stop)
        QCoreApplication.instance().aboutToQuit.connect(worker.stop)
        self.threadpool.start(worker)

    def startIperfUpload(self):
        self.startIperf('u')

    def startIperfDown(self):
        self.startIperf('d')

    def startIperfBidirectional(self):
        self.startIperf('b')

    def startIperfAlternating(self):
        self.startIperf('a')

    def updateIperf(self, series):
        print('update %s' % series.name)
        if series.name in self.curves.keys():
            self.curves[series.name].setData(series.timestamp, series.value, connect=np.array(series.connect))
        self.lanStats.update(series)

    def clear(self):
        """Reset all data series to length 0 and clear the charts"""
        for name, series in self.dataStore.data.items():
            series.clear()

        self.min = -1
        self.max = -1

        self.updateOokla(self.dataStore.data['ooklaDown'])
        self.updateOokla(self.dataStore.data['ooklaUp'])

        self.updateIperf(self.dataStore.data['iperfDown'])
        self.updateIperf(self.dataStore.data['iperfUp'])

        self.updatePing(self.dataStore.data['pingFirstHop'])
        self.updatePing(self.dataStore.data['ping1'])
        #self.updatePing(self.dataStore.date['ping2'])

        self.lanStats.clear()
        self.internetStats.clear()
        self.showStatus('Data cleared')

    def export(self):
        self.dataStore.export()




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    # Uncomment below for terminal log messages
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # You can control the logging level
    logging.getLogger().setLevel(logging.DEBUG)  

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()



    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())
