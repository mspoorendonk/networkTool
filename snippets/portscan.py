import socket
import time
import threading

from queue import Queue

iperfServers = []
q = Queue()
print_lock = threading.Lock()

def get_own_ip():
    """
    Get the own IP, even without internet connection.
    From https://stackoverflow.com/a/1267524
    """
    return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])


def portscan(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    subnet = '192.168.1.'
    ip = '%s%d' % (subnet, host)
      
    with print_lock:
        #print(ip)
        pass
    try:
        #with s.connect((ip, port)) as con:
        con = s.connect((ip, port))
        with print_lock:
            print(ip, 'is open')
            iperfServers.append(ip)
        if conn is not None:
            con.close()
    except socket.timeout:
        with print_lock:
           #print(ip, 'is closed')
           pass

    except Exception as ex:
        with print_lock:
           print(ip, 'ERROR in portscan', ex)
    #   pass

def worker():
   while not q.empty():
      host = q.get()
      portscan(host, 5201)
      q.task_done()

def findIperfServers():
    socket.setdefaulttimeout(0.25)
    

    iperfServers = []
    net = get_own_ip()
    net1= net.split('.')
    a = '.'
    subnet = net1[0] + a + net1[1] + a + net1[2] + a 



    # fill the queue with work
    for host in range(1, 254):
        q.put(host)
          
    # spin up a bunch of threads that take work from the queue
    for x in range(100):
        t = threading.Thread(target = worker)
        t.daemon = True
        t.start()
    
    q.join()



startTime = time.time()
findIperfServers()
print(iperfServers)
print('Time taken:', time.time() - startTime)
