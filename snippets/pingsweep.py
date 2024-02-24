import os
import platform
import socket
from multiprocessing import Process, Queue
import time
import argparse
from datetime import datetime
#net = input("Enter the Network Address: ")


def get_own_ip():
    """
    Get the own IP, even without internet connection.
    From https://stackoverflow.com/a/1267524
    """
    return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

net = get_own_ip()
net1= net.split('.')
a = '.'

net2 = net1[0] + a + net1[1] + a + net1[2] + a
#st1 = int(input("Enter the Starting Number: "))
#en1 = int(input("Enter the Last Number: "))
#en1 = en1 + 1

st1 = 1
en1 = 255

own_ip = net
print("Got own ip: " + str(own_ip))
ip_split = own_ip.split('.')
subnet = ip_split[:-1]
subnetstr = '.'.join(subnet)
print('subnet', subnetstr)
oper = platform.system()

if (oper == "Windows"):
   ping1 = "ping -n 1 "
elif (oper == "Linux"):
   ping1 = "ping -c 1 "
else :
   ping1 = "ping -c 1 "
t1 = datetime.now()
print ("Scanning in Progress:")

for ip in range(st1,en1):
   addr = net2 + str(ip)
   print(addr)
   comm = ping1 + addr
   response = os.popen(comm)
   
   for line in response.readlines():
      if(line.count("TTL")):
         break
      if (line.count("TTL")):
         print (addr, "--> Live")
         
t2 = datetime.now()
total = t2 - t1
print ("Scanning completed in: ",total)