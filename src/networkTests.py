"""
the logic of network tests is defined here
- ping
- ookla
- iperf

"""

import subprocess
import json
from PyQt6.QtCore import *
import numpy as np
from util import *
import logging
#import dateutil.parser  #pip install python-dateutil

#serverIp = 'ping.online.net'
serverIp = 'lens.l.google.com'

# download iperf3.9 from https://files.budman.pw/iperf3.9_64.zip this version has the requried flushing of output buffer

#iperfServer = '192.168.1.112'
iperfServer = 'autodetect'  # autodetect will search for it

#iperfDir = os.getenv('USERPROFILE') + r'\Downloads\iperf3.9_64'
iperfDir = 'iperf'
iperfCmd = [iperfDir+r'\iperf3.exe', '-c', iperfServer, '-p', '%d' % iperfPort, '--omit', '1', '-i', '0.5', '--forceflush'] # forceflush makes sure that the output is realtime. -i is the reporting interval in seconds.
#pingCmd_old = ['ping', serverIp, '-w', '3000', '-t']


ooklaDir = r'.\ookla'
ooklaCmd = [ooklaDir+r'\speedtest.exe', '--accept-license', '--accept-gdpr', '-f', 'jsonl' ] # licence acceptance is required as the executable will not run ohterwise.



class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    """
    finished = pyqtSignal()
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    update = pyqtSignal(Series)
    error = pyqtSignal(str)  # ends up in error popup
    status = pyqtSignal(str)  # ends up on statusbar


class PingWorker(QRunnable):
    """

    """

    def __init__(self, series, lossSeries, host, pingSize):
        super(PingWorker, self).__init__()

        self.signals = WorkerSignals()
        self.running = False
        self.series = series
        self.lossSeries = lossSeries
        self.host = host
        self.pingSize = pingSize

    def stop(self):
        print('STOP requested')
        self.running = False

    @pyqtSlot()
    def run(self):
        threading.current_thread().name = "ping"  # makes it easy to locate the thread in the debugger
        self.running = True

        pingCmd = ['ping', '-l', self.pingSize, '-w', '3000', '-n', '5', self.host ]  # report a packetloss every 5 seconds
        self.series.append(np.nan, 0)
        self.series.append(0, 1)
        while self.running:
            logging.debug("calling %s in folder '%s' " % (pingCmd, iperfDir))
            try:
                process = subprocess.Popen(pingCmd, stdout=subprocess.PIPE, cwd=iperfDir, shell=True)
            except Exception as e:
                logging.error(f"Failed to start ping process: {e}")
                self.signals.error.emit(f"Failed to start ping process: {e}")
                break
            while process.poll() is None and self.running:
                output = process.stdout.readline()
                if output:
                    output = output.strip().decode('utf-8').replace('<', '=')
                    print(output)
                    elements = output.split(' ')
                    if "time=" in output:
                        for element in elements:  # sometimes additional elements are present so search for it.
                            if element[:5] == 'time=':
                                ms = int(element.split('=')[1].replace('ms', ''))
                                print(self.series.name + ' RTT %dms' % ms)

                                self.series.append(ms)
                                self.signals.update.emit(self.series)
                                break  # we found the right element
                    if "loss" in output:
                        loss = float(elements[10][1:-1])
                        print(self.series.name + ' %d%% loss' % loss)
                        self.lossSeries.append(loss)
                    if "could not find host" in output:
                        self.signals.error.emit('Ping: Could not find host '+self.host)
                        return

        self.series.append(0, 1)
        self.series.append(np.nan, 0)
        
        #killAll('ping.exe')  # kill it or it will keep running otherwise
        #process.terminate() 
        os.kill(process.pid, 9)

        print('returning ping')
        self.signals.status.emit('ping done')


class OoklaWorker(QRunnable):
    """
Performs an Ookla bandwidth test.
    """
    def __init__(self, seriesDown, seriesUp):
        super(OoklaWorker, self).__init__()

        self.seriesDown = seriesDown
        self.seriesUp = seriesUp
        self.signals = WorkerSignals()
        self.running = False

    def stop(self):
        print('STOP requested')
        self.running = False

    @pyqtSlot()
    def run(self):
        threading.current_thread().name = "ookla" # makes it easy to locate the thread in the debugger
        self.running = True
        count = 30 # stop after so many because we don't want to be banned from ookla

        for r in range(count):
            if self.running == False:
                break
            logging.debug('calling %s in %s' % (ooklaCmd, ooklaDir))
            self.signals.status.emit('calling %s' % ' '.join(ooklaCmd))
            # shell must be true otherwise when running from PyInstaller directory, Python will spin up a command window. (Yes it's counterintuitive)
            process = subprocess.Popen(ooklaCmd, stdout=subprocess.PIPE, shell=True) 
            cd = 1 # create a gap when starting and ending a bandwith test
            cu = 1
            state = 'start'

            while process.poll() is None and self.running:
                #print('.', end='')
                output = process.stdout.readline()
                if output:
                    output_obj = json.loads(output.strip().decode('utf-8'))
                    print(output_obj)

                    if 'type' in output_obj:
                        if output_obj['type'] == 'download' and output_obj['download']['elapsed'] > 200:
                            if state == 'start':
                                self.seriesDown.append(np.nan, 0)
                                self.seriesDown.append(0, 1)
                            state = 'down'
                            down = output_obj['download']['bandwidth']*8/1e6
                            self.seriesDown.append(down, cd)
                            self.signals.update.emit(self.seriesDown)
                            
                            cd = 1
                        if output_obj['type']=='upload' and output_obj['upload']['elapsed']>200:
                            if state == 'down':
                                # close the down series
                                self.seriesDown.append(0, 1)
                                self.seriesDown.append(np.nan, 0)
                                self.signals.update.emit(self.seriesDown)

                                self.seriesUp.append(np.nan, 0)
                                self.seriesUp.append(0, 1)
                            state = 'up'
                            up = output_obj['upload']['bandwidth']*8/1e6

                            self.seriesUp.append(up, cu)
                            self.signals.update.emit(self.seriesUp)
                            cu = 1

            if state == 'down':  # only happens when stopping the run
                self.seriesDown.append(0, 1)        # close the series
                self.seriesDown.append(np.nan, 0)   # and add a nan to start a gap
                self.signals.update.emit(self.seriesDown)
            if state == 'up':
                self.seriesUp.append(0, 1)
                self.seriesUp.append(np.nan, 0)
                self.signals.update.emit(self.seriesUp)

            #rc = process.poll()

            process.terminate()  # kill it or it will keep running otherwise
            #os.kill(process.pid, 9) # PermissionError: [WinError 5] Access is denied

            print('returning ookla')

            #print(len(ooklaUp), len(ooklaUpTime), len(ooklaUpConnect))
            #return rc
            self.signals.status.emit('ookla done')


class BackgroundPollerSignals(QObject):
    activeInterface = pyqtSignal(str)
    ssid = pyqtSignal(str)


class BackgroundPoller(QRunnable):
    """Monitors some stuff in the background"""

    def __init__(self):
        super(BackgroundPoller, self).__init__()
        self.signals = BackgroundPollerSignals()

    def stop(self):
        logging.debug('BackgroundPoller: STOP requested')
        self.running = False

    @pyqtSlot()
    def run(self):
        threading.current_thread().name = "BackgroundPoller"  # makes it easy to locate the thread in the debugger
        self.running = True

        self.activeInterface = 'disconnected'
        self.ssid = None
        
        while self.running:
            interface = getActiveInterface()
            if self.activeInterface != interface:
                self.activeInterface = interface
                print('emmitting', self.activeInterface)
                self.signals.activeInterface.emit(self.activeInterface)

            ssid = getSSID()
            if self.ssid != ssid:
                self.ssid = ssid
                self.signals.ssid.emit(self.ssid)
            time.sleep(2)


class IperfWorker(QRunnable):
    """
        Capture performance statistics by connecting to an iperf server
    """

    def __init__(self, direction, seriesDown, seriesUp):
        super(IperfWorker, self).__init__()
        self.direction = direction
        self.seriesDown = seriesDown
        self.seriesUp = seriesUp
        self.signals = WorkerSignals()
        self.running = False
        


    def stop(self):
        print('STOP requested')
        self.running = False


    @pyqtSlot()
    def run(self):
        threading.current_thread().name = "iperf"  # makes it easy to locate the thread in the debugger
        self.running = True

        if iperfServer == 'autodetect':
            found_servers, msg = findIperfServers()
            if len(found_servers) == 0:
                self.signals.error.emit(msg)
                return
            iperfCmd[2] = found_servers[0]
            self.signals.status.emit('selected iperf server %s' % found_servers[0])

        count = 1
        if self.direction == 'a':
            count = 30

        for r in range(count):
            if self.running == False:
                break

            # build a commandline
            totalCmd = iperfCmd.copy()
            if self.direction == 'b':
                totalCmd.append('--bidir')

            if self.direction == 'd' or (r % 2 == 0 and self.direction == 'a'):
                totalCmd.append('--reverse')

            if self.direction in 'udb':
                totalCmd.append('-t')
                totalCmd.append('600')
            else:
                totalCmd.append('-t')
                totalCmd.append('20')

            logging.debug('calling %s in %s' % (' '.join(totalCmd), iperfDir))
            # shell must be true otherwise when running from PyInstaller directory, Python will spin up a command window. (Yes it's counterintuitive)
            process = subprocess.Popen(totalCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            while process.poll() is None and self.running:
                print('.', end='')
                output = process.stdout.readline()
                if output:
                    output = output.decode('utf-8').strip()
                    print('>', output, '<')

                    if 'Mbits' in output and output[:5] == '[  5]' and (self.direction in 'bd' or (self.direction =='a' and r%2==0)):
                        if len(self.seriesDown) == 0 or timestamp()-self.seriesDown.timestamp[-1] > 5:  # when starting a new burst
                            self.seriesDown.append(np.nan, 0)
                            self.seriesDown.append(0, 1)
                        state = 'down'

                        down=float(output.split('Mbits')[0].strip().split(' ')[-1])  # fetch the last word before 'Mbits'
                        self.seriesDown.append(down, 1)

                    if 'Mbits' in output and ((output[:5] == '[  7]' and self.direction == 'b')
                                           or (output[:5] == '[  5]' and (self.direction == 'u' or (self.direction =='a' and r%2==1)))):
                        if len(self.seriesUp) == 0 or timestamp()-self.seriesUp.timestamp[-1] > 5:
                            self.seriesUp.append(np.nan, 0)
                            self.seriesUp.append(0, 1)
                        state = 'up'

                        up = float(output.split('Mbits')[0].strip().split(' ')[-1])  # fetch the last word before 'Mbits'

                        self.seriesUp.append(up, 1)

                    self.signals.update.emit(self.seriesDown)
                    self.signals.update.emit(self.seriesUp)

            if self.direction in 'bd' or (self.direction =='a' and r%2==0):
                self.seriesDown.append(0, 1)
                self.seriesDown.append(np.nan, 0)

            if self.direction in 'bu' or (self.direction =='a' and r%2==1):
                self.seriesUp.append(0, 1)
                self.seriesUp.append(np.nan, 0)

            self.signals.update.emit(self.seriesDown)
            self.signals.update.emit(self.seriesUp)

            #process.terminate()  # kill it or it will keep running otherwise
            if process.pid:
                os.kill(process.pid, 9)

            rc = process.poll()
            print('returning iperf', rc)

            if self.running:  # if we intend to stop anyway then reading errors is not interesting
                err = process.stderr.read1()  # non-blocking read
                if err:
                    err = err.decode('utf-8').strip()
                    print('>>', err, '<<')
                    #error_dialog = QErrorMessage() # can only raise this in gui thread. Have to use signals/slots
                    self.signals.error.emit(err)
                    err = ''

            self.signals.status.emit('iperf done')
            
