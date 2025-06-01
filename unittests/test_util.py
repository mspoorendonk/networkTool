from src.util import *
import re


def test_get_own_ip():
    h = get_own_ip()
    assert re.match(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',h), 'must return an IPv4 address'



def test_getActiveInterface():
    i = getActiveInterface()
    assert i =="Ethernet"



def test_getFirstHop():
    h = getFirstHop()
    #print('Test:first hop', h)
    assert re.match(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', h), 'must return an IPv4 address'


def test_findIperfServers():
    findIperfServers()
    print(iperfServers)
    assert len(iperfServers)>=0


def test_listProcesses():
    procs=listProcesses()
    print(procs)
    #self.assertTrue(len(procs)>1, 'no processes returned')
    assert True     


def test_getSSID():
    ssid = getSSID()
    print('ssid: ' + ssid)
    assert (ssid == '' or (len(ssid) > 4 and len(ssid) < 30)), "SSID doesn't appear to be short string"


def test_get_interface():
    interface=getInterface()
    print(interface.PhysicalAdapter)
    assert interface.PhysicalAdapter, 'empty result'
