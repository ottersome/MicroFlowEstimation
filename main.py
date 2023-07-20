from py_utils.topologies.thick import ThickTopo
from py_utils.controllers.POX import POX
from mininet.net import Mininet
from mininet.node import (
     OVSSwitch,
     OVSController,
     RemoteController,
     Controller,
     UserSwitch,
     Node)
from mininet.cli import CLI
from time import time
from typing import List
import argparse
import threading

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument("--flows",default=10,type=int)
    return args.parse_args()

args = parse_args()
print(f'Running with {args.flows} flows')

t1 = time()
# Start topology and mininet
topo = ThickTopo(args.flows)
net = Mininet(topo=topo,
              switch=OVSSwitch,
              build=False,
              autoSetMacs=True,
              )
flooding_time = 1

# Load our Traffic Flow
# c0 = Controler('c0',port=6633)
# net.addController(c)

# Load our Pythonic Controller.
# (Not sure what this looks like  yet)
def ddos_flood_true_ddos(hosts:List[Node],victims_ip):
    for host in hosts:
        #host.cmd('timeout '+str(flooding_time)+'s hping3 --flood '+victims_ip)
        host.sendCmd('timeout '+str(flooding_time)+'s hping3 --flood '+victims_ip)

def ddos_flood_spoofed_ddos(host,victims_ip):
    for host in hosts:
        host.cmd('timeout '+str(flooding_time)+'s hping3 --flood -a '+host.ip+' '+victims_ip)

# Start CLI 
net.build()
net.start()
t2 = time()
print('Time to Start is ',t2-t1)

# Emulate Traffic 
print('End host is :',topo.end_host)
hosts = [net.getNodeByName('h'+str(i)) for i in range(args.flows)]
end_host = net.getNodeByName('end_host')

# Open Wireshark 
end_host.sendCmd('sudo wireshark -i end_host-eth0 -k &')

#flood_thread = threading.Thread(target=ddos_flood_true_ddos,args=(hosts,end_host.IP()))
#flood_thread.start()

# Estimate Utility Function.
CLI( net )
flood_thread.join()
t3 = time()
net.stop()
t4 = time()
print('Time to tear down is ',t4-t3)
