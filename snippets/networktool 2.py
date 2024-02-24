"""
Show network condition.

CHANGELOG:
2021-03-01: Incorporated newer iperf3 version that flushes output buffer for realtime monitoring
2021-03-02: Fixed bug in library in mkColor() and reported it on github.
"""
#import initExample ## Add path to library (just for examples; you do not need this)
import sys
import pyqtgraph as pg
pg.setConfigOptions(antialias=True)
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import *
import numpy as np
from contextlib import suppress

#from datetime import datetime
import subprocess
import json
import socket
import os
import datetime
import dateutil.parser  #pip install python-dateutil
import time

import threading

print('python version', sys.version)
print('pyqtgraph version', pg.__version__)
print('qt version', pg.Qt.VERSION_INFO)

#thisIp = socket.gethostbyname(socket.getfqdn())
thisName = socket.gethostname()
#serverIp = '192.168.1.112'
#serverIp = '169.254.147.208'
#serverIp = 'ping.online.net'
serverIp = 'www.ellipz.io'

# download iperf3.9 from https://files.budman.pw/iperf3.9_64.zip
#iperfServer = '192.168.1.127'
iperfServer = '192.168.1.112'
iperfPort = '5201'
iperfDir = os.getenv('USERPROFILE') + r'\Downloads\iperf3.9_64'
iperfCmd = [iperfDir+r'\iperf3.exe', '-c', iperfServer, '-p', iperfPort, '-t', '600', '--omit', '1', '-i', '1', '--forceflush', '--bidir']
pingCmd = ['ping', serverIp, '-w', '3000', '-t']
ooklaCmd = ['speedtest.exe', '-f', 'jsonl' ]
ooklaDir = r'.'




pingMs = []
pingTime = []

ooklaDown = []
ooklaDownConnect = []
ooklaDownTime = []

ooklaUp = []
ooklaUpConnect = []
ooklaUpTime = []

iperfDown = []
iperfDownConnect = []
iperfDownTime = []

iperfUp = []
iperfUpConnect = []
iperfUpTime = []


# the original mkColor() doesn't support brushes and throws an error when a brush is passed to the legend.
# this just returns a transparent color to get rid of the problem.
def mkColorNew(*args):
    #print('make color')
    if len(args) == 1 and isinstance(args[0], QtGui.QBrush): # handle brushes
        return QtGui.QColor('#00000000') # transparent
    return pg.functions.mkColorOrig(*args) # call the original function

pg.functions.mkColorOrig = pg.functions.mkColor
pg.functions.mkColor = mkColorNew

def timestamp():
    # a bit of hassle here to provide subsecond timestamps
    dt = datetime.datetime.now()
    return time.mktime(dt.timetuple()) + dt.microsecond/1000000.0


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        #print('scale: ', scale)

        format = '%H:%M:%S'
        return [datetime.datetime.fromtimestamp(value).strftime(format) for value in values]

def startPing():
    t=threading.Thread(target=ping, daemon=True)
    t.start()

def ping():
    print('calling %s in %s' % (pingCmd, iperfDir))
    process = subprocess.Popen(pingCmd, stdout=subprocess.PIPE, cwd=iperfDir, shell=False)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            output = output.strip().decode('utf-8')
            print(output)
            elements = output.split(' ')
            if "time=" in output:
                ms = int(elements[4].split('=')[1].replace('ms',''))
                print(ms)
                updatePing(ms)
            #.split('=')[1]
            

    rc = process.poll()
    return rc

def updatePing(ms):
    global pingMs, pingTime, ptr1, curve1
    #pingMs[:-1] = pingMs[1:]  # shift data in the array one sample left
    pingMs.append(ms)
    pingTime.append(timestamp())
    
    #pingTime[:-1] = pingTime[1:]                        # (see also: np.roll)
    #pingMs[-1] = ms
    #pingTime[-1] = timestamp()
    curve1.setData(pingTime, pingMs)

def startOokla():
    t=threading.Thread(target=ookla, daemon=True)
    t.start()


def ookla():
    global ooklaDown, ooklaUp, ooklaTime, curve2, curve3
    print('calling %s in %s' % (ooklaCmd, ooklaDir))
    process = subprocess.Popen(ooklaCmd, stdout=subprocess.PIPE, cwd=ooklaDir, shell=False)
    cd = 1 # create a gap when starting and ending a bandwith test
    cu = 1
    state = 'start'





    while process.poll() == None:
        #print('.', end='')
        output = process.stdout.readline()
        if output:
            output_obj = json.loads(output.strip().decode('utf-8'))
            print(output_obj)
            #if 'timestamp' in output_obj and output_obj['type']=='download':

            if 'type' in output_obj:
                if output_obj['type']=='download' and output_obj['download']['elapsed']>200:
                    if state == 'start':
                        ooklaDown.append(np.nan)
                        ooklaDownTime.append(timestamp())
                        ooklaDownConnect.append(0)
                        ooklaDown.append(0)
                        ooklaDownTime.append(timestamp())
                        ooklaDownConnect.append(1)
                    state = 'down'
                    down = output_obj['download']['bandwidth']*8/1e6
                    ts = dateutil.parser.isoparse(output_obj['timestamp']).timestamp()
                    #if (ts - ooklaDownTime[-1]).total_sconds < 0.1:
                    #    ts = ooklaDownTime[-1]
                    #print(ts)
                    ooklaDown.append(down)
                    ooklaDownTime.append(timestamp())
                    #if cd == 0 and len(ooklaDownConnect)>0:
                    #    ooklaDownConnect[-1]=0
                    ooklaDownConnect.append(cd)
                    #ooklaDownTime.append(ts)
                    
                    cd = 1
                if output_obj['type']=='upload' and output_obj['upload']['elapsed']>200:
                    if state == 'down':
                        ooklaDown.append(0)
                        ooklaDownTime.append(timestamp())
                        ooklaDownConnect.append(1)
                        ooklaDown.append(np.nan)
                        ooklaDownTime.append(timestamp())
                        ooklaDownConnect.append(0)

                        ooklaUp.append(np.nan)
                        ooklaUpTime.append(timestamp())
                        ooklaUpConnect.append(0)
                        ooklaUp.append(0)
                        ooklaUpTime.append(timestamp())
                        ooklaUpConnect.append(1)
                    state = 'up'
                    up = output_obj['upload']['bandwidth']*8/1e6
                    ts = dateutil.parser.isoparse(output_obj['timestamp']).timestamp()
                    ooklaUp.append(up)
                    ooklaUpTime.append(timestamp())
                    #if cu == 0 and len(ooklaUpConnect)>0:
                    #    ooklaUpConnect[-1]=0
                    ooklaUpConnect.append(cu)
                    #ooklaUpTime.append(ts)
                    
                    cu = 1

                curve2.setData(ooklaDownTime, ooklaDown, connect=np.array(ooklaDownConnect))
                #curve2.setData(ooklaDownTime, ooklaDown, connect='finite')
                curve3.setData(ooklaUpTime, ooklaUp, connect=np.array(ooklaUpConnect))   
                #curve3.setData(ooklaUpTime, ooklaUp, connect='finite') 



    ooklaUp.append(0)
    ooklaUpTime.append(timestamp())
    ooklaUpConnect.append(1)
    ooklaUp.append(np.nan)
    ooklaUpTime.append(timestamp())
    ooklaUpConnect.append(0)
    curve2.setData(ooklaDownTime, ooklaDown, connect=np.array(ooklaDownConnect))
    #curve2.setData(ooklaDownTime, ooklaDown, connect='finite')
    curve3.setData(ooklaUpTime, ooklaUp, connect=np.array(ooklaUpConnect))   
    #curve3.setData(ooklaUpTime, ooklaUp, connect='finite') 

    rc = process.poll()
    print('returning ookla')

    #print(len(ooklaUp), len(ooklaUpTime), len(ooklaUpConnect))
    return rc

def startIperf():
    t=threading.Thread(target=iperf, daemon=True)
    t.start()


def iperf():
    global iperfDown, iperfUp, iperfTime, curve4, curve5
    print('calling %s in %s' % (' '.join(iperfCmd), iperfDir))
    process = subprocess.Popen(iperfCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=iperfDir, shell=False)



    while process.poll() == None:
        print('.', end='')
        output = process.stdout.readline()
        if output:
            output=output.decode('utf-8').strip()
            print('>', output, '<')

            if output[:5] == '[  5]' and 'Mbits' in output:
                if len(iperfDownTime)==0 or timestamp()-iperfDownTime[-1]>5:
                    iperfDown.append(np.nan)
                    iperfDownTime.append(timestamp())
                    iperfDownConnect.append(0)
                    iperfDown.append(0)
                    iperfDownTime.append(timestamp())
                    iperfDownConnect.append(1)
                state = 'down'

                down=float(output.split('Mbits')[0].strip().split(' ')[-1]) # fetch the last word before 'Mbits'

                iperfDown.append(down)
                iperfDownTime.append(timestamp())

                iperfDownConnect.append(1)

            if output[:5] == '[  7]' and 'Mbits' in output:
                if len(iperfUpTime)==0 or timestamp()-iperfUpTime[-1]>5:
                    iperfUp.append(np.nan)
                    iperfUpTime.append(timestamp())
                    iperfUpConnect.append(0)
                    iperfUp.append(0)
                    iperfUpTime.append(timestamp())
                    iperfUpConnect.append(1)
                state = 'up'

                up=float(output.split('Mbits')[0].strip().split(' ')[-1]) # fetch the last word before 'Mbits'

                iperfUp.append(up)
                iperfUpTime.append(timestamp())

                iperfUpConnect.append(1)

        
            curve4.setData(iperfDownTime, iperfDown, connect=np.array(iperfDownConnect))
            #curve4.setData(iperfDownTime, iperfDown, connect='finite')
            curve5.setData(iperfUpTime, iperfUp, connect=np.array(iperfUpConnect))   
            #curve5.setData(iperfUpTime, iperfUp, connect='finite') 

    iperfDown.append(0)
    iperfDownTime.append(timestamp())
    iperfDownConnect.append(1)
    iperfDown.append(np.nan)
    iperfDownTime.append(timestamp())
    iperfDownConnect.append(0)

    iperfUp.append(0)
    iperfUpTime.append(timestamp())
    iperfUpConnect.append(1)
    iperfUp.append(np.nan)
    iperfUpTime.append(timestamp())
    iperfUpConnect.append(0)

    curve4.setData(iperfDownTime, iperfDown, connect=np.array(iperfDownConnect))
    #curve4.setData(iperfDownTime, iperfDown, connect='finite')
    curve5.setData(iperfUpTime, iperfUp, connect=np.array(iperfUpConnect))   
    #curve5.setData(iperfUpTime, iperfUp, connect='finite') 

    rc = process.poll()
    print('returning iperf', rc)

    err = process.stderr.read()
    if err:
        err=err.decode('utf-8').strip()
        print('>>', err, '<<')
        #error_dialog = QErrorMessage() # can only raise this in gui thread. Have to use signals/slots
        #error_dialog.showMessage(err)
        err = ''

    print(len(iperfUp), len(iperfUpTime), len(iperfUpConnect))
    print(len(iperfDown), len(iperfDownTime), len(iperfDownConnect))
    return rc
    
class Window(QWidget):
    def __init__(self):
        global curve1, curve2, curve3, curve4, curve5
        QWidget.__init__(self)
        self.setGeometry(900, 600, 1700, 700)
        layout = QGridLayout()
        self.setLayout(layout)

        quitAct = QAction('&Quit', self)
        quitAct.setShortcut('Ctrl+Q')
        quitAct.setStatusTip('Quit the application')
        quitAct.triggered.connect(qApp.quit)

        pingAct = QAction('Ping latency test', self)
        pingAct.setShortcut('Ctrl+P')
        pingAct.triggered.connect(startPing)

        ooklaAct = QAction('Ookla internet bandwidth test', self)
        ooklaAct.setShortcut('Ctrl+O')
        ooklaAct.triggered.connect(startOokla)

        iperfAct = QAction('iperf3 LAN bandwidth test', self)
        iperfAct.setShortcut('Ctrl+I')
        iperfAct.triggered.connect(startIperf)

        # create menu
        menubar = QMenuBar()
        layout.addWidget(menubar, 0, 0)
        actionFile = menubar.addMenu("File")
        #actionFile.addSeparator()
        actionFile.addAction(quitAct)

        actionTest = menubar.addMenu("Test")
        actionTest.addAction(ooklaAct)
        actionTest.addAction(pingAct)
        actionTest.addAction(iperfAct)
        #menubar.addMenu("View")
        #menubar.addMenu("Help")

        # add textbox
        tbox = QPlainTextEdit()
        layout.addWidget(tbox, 1, 0)

        pg.setConfigOption('background', '#202020')
        pg.setConfigOption('foreground', '#a0a0a0')

        #make a nice gradient below the curve
        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#00000001'))
        grad.setColorAt(0.10, pg.mkColor('#00ff0050')) # green
        grad.setColorAt(0.20, pg.mkColor('#ffff0090')) # yellow
        grad.setColorAt(0.40, pg.mkColor('#ffff0090')) # yellow
        grad.setColorAt(0.70, pg.mkColor('#ff000090')) # red
        pingBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#00ff0001'))
        grad.setColorAt(0.9, pg.mkColor('#00ff0050')) # green
        greenBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#a0ffa001'))
        grad.setColorAt(0.9, pg.mkColor('#a0ffa050')) # light green
        lightGreenBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#0000ff01'))
        grad.setColorAt(0.9, pg.mkColor('#2020ff90')) # blue
        blueBrush = QtGui.QBrush(grad)

        grad = QtGui.QLinearGradient(0, 0, 0, 100)
        grad.setColorAt(0, pg.mkColor('#8080ff01'))
        grad.setColorAt(0.9, pg.mkColor('#8080ff90')) # light blue
        lightBlueBrush = QtGui.QBrush(grad)

        charts=pg.GraphicsLayoutWidget()
        charts.setAntialiasing(True)
        # 1) Simplest approach -- update data in the array such that plot appears to scroll
        #    In these examples, the array size is fixed.
        p1 = charts.addPlot(title='ping', labels={'left': 'roundtrip time [ms]', 'bottom': 'wallclock time'}, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        p1.showGrid(x=True, y=True, alpha = 0.3)

        # overload the setRange() in order to fix only ymin to 0
        # inspiration: https://groups.google.com/g/pyqtgraph/c/TxIj3mc49HE
        def setRange1(rect=None, xRange=None, yRange=None, *args, **kwds):
            if not kwds.get('disableAutoRange', True):
                if yRange is not None:
                    yRange[0] = 0
            pg.ViewBox.setRange(vb1, rect, xRange, yRange, *args, **kwds)

        vb1 = p1.vb
        vb1.setRange=setRange1
        vb1.setMouseEnabled(x=True, y=False) # only allow zoom on time axis
        
        #p1.setYRange(0, 100, padding=0)
        #p1.setXRange(0, 300, padding=0)
        #p1.setXRange(timestamp(), timestamp() + 100)
        p2 = charts.addPlot(title='Bandwidth', labels={'left': 'bandwidth [Mbps]', 'bottom': 'wallclock time'}, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        p2.addLegend()
        p2.showGrid(x=True, y=True, alpha = 0.3)
        
        def setRange2(rect=None, xRange=None, yRange=None, *args, **kwds):
            if not kwds.get('disableAutoRange', True):
                if yRange is not None:
                    yRange[0] = 0
            pg.ViewBox.setRange(vb2, rect, xRange, yRange, *args, **kwds)

        vb2 = p2.vb
        vb2.setRange=setRange2
        vb2.setMouseEnabled(x=True, y=False) # only allow zoom on time axis

    
        curve1 = p1.plot(pen=pg.mkPen(color='w', width=2), fillLevel=0, brush=pingBrush, name='ping')
        curve2 = p2.plot(pen=pg.mkPen(color='#9090ff', width=2), fillLevel=0, brush=lightBlueBrush, name='internet download')
        curve3 = p2.plot(pen=pg.mkPen(color='#2020ff', width=2), fillLevel=0, brush=blueBrush, name='internet upload')
        curve4 = p2.plot(pen=pg.mkPen(color='#a0ffa0', width=2), fillLevel=0, brush=lightGreenBrush, name='LAN download')
        curve5 = p2.plot(pen=pg.mkPen(color='#00ff00', width=2), fillLevel=0, brush=greenBrush, name='LAN upload')
        

        layout.addWidget(charts, 2, 0)

app = QApplication(sys.argv)
app.setStyle('Fusion')

win = Window()
win.show()
win.setWindowTitle('Realtime bandwidth test')










## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()