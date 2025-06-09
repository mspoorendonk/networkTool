"""
helper functions

pip install scapy
"""

import psutil
import socket
import time
import datetime
import threading
from queue import Queue
import os
import csv
import subprocess
import scapy.all
import logging

import ctypes.wintypes  # for "My Documents" folder


iperfPort = 5201
iperfServers = []
q = Queue()
print_lock = threading.Lock()  # this makes sure that messages are printed as a whole to the screen and not halfway interrupted by different thread.





def getInterface(id=''):
    """instance of Win32_NetworkAdapter
{
	AdapterType = "Ethernet 802.3";
	AdapterTypeId = 0;
	Availability = 3;
	Caption = "[00000012] ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_NetworkAdapter";
	Description = "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter";
	DeviceID = "12";
	GUID = "{F7438BBD-9594-4898-9306-3488D7CAB1B9}";
	Index = 12;
	Installed = TRUE;
	InterfaceIndex = 26;
	MACAddress = "00:0E:C6:00:38:82";
	Manufacturer = "ASIX";
	MaxNumberControlled = 0;
	Name = "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter #2";
	NetConnectionID = "Ethernet 3";
	NetConnectionStatus = 2;
	NetEnabled = TRUE;
	PhysicalAdapter = TRUE;
	PNPDeviceID = "USB\\VID_0B95&PID_1790\\00000000000009";
	PowerManagementSupported = FALSE;
	ProductName = "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter";
	ServiceName = "AX88179";
	Speed = "1000000000";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "WATT";
	TimeOfLastReset = "20210611194729.706688+120";
};"""
    import wmi

    c = wmi.WMI()
    qry = "select * from Win32_NetworkAdapter where NetEnabled=True and NetConnectionStatus=2"
    if id != '':
        qry += " and NetConnectionID = '%s'" % id
    #for o in c.query(qry):
    #    print(o)
    #lst = [o.Name for o in c.query(qry)]
    #print(lst)
    return c.query(qry)[0]

def getMyDocuments():
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value

def timestamp():
    # a bit of hassle here to provide subsecond timestamps. returns float.
    dt = datetime.datetime.now()
    return time.mktime(dt.timetuple()) + dt.microsecond/1000000.0


def get_own_ip():
    """
    Get the own IP, even without internet connection.
    From https://stackoverflow.com/a/1267524
    """
    return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])


def portscan(ip, port, found_servers):
    with print_lock:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            with print_lock:
                logging.debug('found iperf server %s' % ip)
                found_servers.append(ip)
    except socket.timeout:
        with print_lock:
            pass
    except Exception as ex:
        with print_lock:
            print(ip, 'ERROR in portscan', ex)



def worker(q, found_servers):
    while not q.empty():
        ip = q.get()
        portscan(ip, iperfPort, found_servers)
        q.task_done()


def findIperfServers():
    """ Scan the subnet to find servers that have port 5201 open. Completes in about 0.5 seconds."""
    logging.debug('finding iperf servers')
    socket.setdefaulttimeout(0.2)

    found_servers = []
    net = get_own_ip()
    net1= net.split('.')
    subnet = net1[0] + '.' + net1[1] + '.' + net1[2] + '.'

    # fill the queue with work
    q = Queue()
    for host in range(1, 254):
        if host != int(net1[3]): # skip own ip
            q.put('%s%d' % (subnet, host))

    # spin up a bunch of threads that take work from the queue
    for x in range(255):
        t = threading.Thread(target=worker, args=(q, found_servers))
        t.daemon = True
        t.start()
    q.join()
    msg = 'OK'
    if len(found_servers) == 0:
        msg = "Didn't find any iperf servers in subnet %s*. Start one on an other machine by choosing 'start iperf server' from the Windows Start menu." % subnet
    logging.debug('found %d iperf servers' % len(found_servers))
    return found_servers, msg


def killAll(killName):
    print('listing processes')
    ls = []
    for p in psutil.process_iter():
        try:
            name = p.name()
            cmdline = p.cmdline()
            exe = p.exe()
            pid = p.pid
            if killName == name:
                print('Killing %s' % name)
                os.kill(pid, 9)
            #ls.append((name, cmdline, exe, pid))
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except psutil.NoSuchProcess:
            continue
    #print(ls)

def listProcesses():
    print('listing processes')
    ls = []
    for p in psutil.process_iter():
        try:
            name = p.name()
            cmdline = p.cmdline()
            exe = p.exe()
            pid = p.pid
            print(name)
            #ls.append((name, exe, pid))
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except psutil.NoSuchProcess:
            continue
    #print(ls) 

def getSSID():
    #print('lookingup ssid')
    connected_ssid = ''

    try:
        current_network = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], shell=True)\
            .decode('utf-8').split('\n')  # shell=True prevents a command window from popping up on windows. (yes it's counterintuitive)
        ssid_line = [x for x in current_network if 'SSID' in x and 'BSSID' not in x]
        if ssid_line:
            ssid_list = ssid_line[0].split(':')
            connected_ssid = ssid_list[1].strip()
    except Exception:
        pass
    #print('ssid: ' + connected_ssid)
    return connected_ssid

def getActiveInterface():
    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    available_networks = []
    for intface, addr_list in addresses.items():
        if any(getattr(addr, 'address').startswith("127.0.0.1") for addr in addr_list):
            continue
        elif intface in stats and getattr(stats[intface], "isup"):
            available_networks.append(intface)

    #print(available_networks)
    if len(available_networks)>0:
        return available_networks[0]
    else:
        return 'disconnected'

def getFirstHop():
    """Return the first hop. Found by tracerouting to www.google.com"""
    host = ''
    cmd = 'tracert -h 1 www.google.com'
    # todo: this probably doesn't work for posix systems.
    # todo: add error handling

    with os.popen(cmd) as process:
        output = process.read()
    #print('>>' + output + '<<')

    for line in output.splitlines():
        #print('>'+line[0:4]+'<')
        if line[0:4] == '  1 ':
            elements = line.strip().split(' ', )
            #print(elements)
            host = elements[-1].strip('[]')  # only when a host name is resolved then the ip has [] around it
    return host



class Series():
    """A timeseries class that holds the measured values"""
    def __init__(self, name):
        self.name = name
        self.value = []
        self.timestamp = []
        self.connect = []

        self.comment = []
        self.commentTimestamp = []

    def append(self, value, connect=1):
        """Append a new value to the time series.
        
        Args:
            value: The measurement value to append
            connect: Should the dots be connected with a line (1=connected, 0=disconnected).
        """
        self.timestamp.append(timestamp())
        self.value.append(value)
        self.connect.append(connect)

    def appendComment(self, comment):
        self.commentTimestamp.append(timestamp())
        self.comment.append(comment)

    def clear(self):
        del self.value[:]
        del self.timestamp[:]
        del self.connect[:]
        del self.comment[:]
        del self.commentTimestamp[:]

    def writeCsv(self):
        #exportFolder = os.path.expanduser('~/Networktool')
        exportFolder = os.path.join(getMyDocuments(), 'Networktool')

        if not os.path.exists(exportFolder):
            os.makedirs(exportFolder)

        fileName = os.path.join(exportFolder, self.name+'.csv')
        logging.info('exporting to ' + fileName)

        try:
            with open(fileName, mode='w', newline='') as csv_file:  # setting newline to '' disables newline translation so that all csvs are equal on all platforms
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                #writer.writeheader()
                writer.writerow(['timestamp', 'value', 'connect'])  # header
                for i in range(len(self.timestamp)):
                    time_string = time.ctime(self.timestamp[i])
                    writer.writerow([time_string, self.value[i], self.connect[i]])
        except IOError:
            logging.error('Failed to open %s for export' % fileName)

    def __len__(self):
        return len(self.timestamp)

class DataStore():
    """
    Holds the recorded data and allows saving, loading and exporting.
    """

    def __init__(self):
        self.data = {}
        self.createSeries('iperfUp')
        self.createSeries('iperfDown')
        self.createSeries('ooklaUp')
        self.createSeries('ooklaDown')
        self.createSeries('pingFirstHop')
        self.createSeries('ping1')
        self.createSeries('ping2')
        self.createSeries('lossFirstHop')
        self.createSeries('loss1')
        self.createSeries('loss2')


    def createSeries(self, name):
        self.data[name] = Series(name)

    def export(self):
        for name, series in self.data.items():
            series.writeCsv()

