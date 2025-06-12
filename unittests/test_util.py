from src.util import *
import re
import numpy as np


def test_mapNetworkStateToTone():
    # Test case 1: networkState is at minState
    assert mapNetworkStateToTone(0, 0, 100, 200, 1000) == 200
    # Test case 2: networkState is at maxState
    assert mapNetworkStateToTone(100, 0, 100, 200, 1000) == 1000
    # Test case 3: networkState is in the middle
    assert mapNetworkStateToTone(50, 0, 100, 200, 1000) == 600
    # Test case 4: networkState is below minState (should clamp to minFreq)
    assert mapNetworkStateToTone(-10, 0, 100, 200, 1000) == 200
    # Test case 5: networkState is above maxState (should clamp to maxFreq)
    assert mapNetworkStateToTone(110, 0, 100, 200, 1000) == 1000
    # Test case 6: minState and maxState are the same
    assert mapNetworkStateToTone(50, 50, 50, 200, 1000) == 1000 # maxFreq
    # Test case 7: NaN input
    assert mapNetworkStateToTone(np.nan, 0, 100, 200, 1000) == 0 # Expecting 0 for NaN
    # Test case 8: Reverse mapping (e.g. latency where lower is better)
    # If mapNetworkStateToTone is intended for latency (lower value = higher freq)
    # then the parameters minState and maxState should be swapped by the caller
    # or the function should have a 'reverse' flag.
    # Assuming current logic: higher networkState = higher frequency
    # For latency, if we want high freq for low latency:
    # mapNetworkStateToTone(latency, max_latency, min_latency)
    assert mapNetworkStateToTone(10, 100, 0, 200, 1000) == 920.0 # (10-100)/(0-100) * (1000-200) + 200


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
    iperfServers, msg = findIperfServers()
    print(iperfServers)
    print(msg)
    assert len(iperfServers)>=0


def test_listProcesses():
    procs=listProcesses()
    print(procs)
    assert len(procs)>1, 'no processes returned'


def test_getSSID():
    ssid = getSSID()
    print('ssid: ' + ssid)
    assert (ssid == '' or (len(ssid) > 4 and len(ssid) < 30)), "SSID doesn't appear to be short string"


def test_get_interface():
    interface=getInterface()
    print(interface.PhysicalAdapter)
    assert interface.PhysicalAdapter, 'empty result'
