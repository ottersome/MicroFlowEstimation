from py_utils.topologies.thick import RoundTopology
from py_utils.controllers.POX import POX
from math import sqrt
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
from numpy import random
import logging
import argparse
import threading

logging.basicConfig(level=logging.DEBUG,filename="./log")

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument("--flows",default=10000,type=int)
    return args.parse_args()

args = parse_args()
print(f'Running with {args.flows} flows')

t1 = time()
# Start topology and mininet
num_hosts = int(sqrt(args.flows))
topo = RoundTopology(num_hosts)
net = Mininet(topo=topo,
              switch=OVSSwitch,
              build=False,
              autoSetMacs=True,
              )

capturing_time = 1
# As Per Our own experiments we have seen rates of 1e7
# So Cohens Rates *should* be okay
uniform_lower = 100
uniform_upper = 10000

# Load our Traffic Flow
# c0 = Controler('c0',port=6633)
# net.addController(c)

# Load our Pythonic Controller.
# (Not sure what this looks like  yet)
# TODO: figure out generation of DON  and DOFF Params
    # for now uniform
def traffic_simulation(*hosts):
    hosts = list(hosts)
    num_hosts = len(hosts)
    for i in range(num_hosts):
        send_str =""
        for j in range(num_hosts):
            # TODO figur out what N shoudl be 
            amp = " && " if j !=num_hosts-1 else ""
            send_str += 'sudo sourcesonoff -n 1000 --transmitter-udp'+\
                             ' --destination '+str(hosts[j].IP()) +\
                             ' --don-alpha ' + "0.9" +\
                             ' --doff-alpha ' + "0.9" + amp
        logging.debug(send_str)
        hosts[i].sendCmd(send_str)
        hosts[i].monitor()


# TODO remove when it becomes irrelevant
#def ddos_flood_spoofed_ddos(host,victims_ip):
#    for host in hosts:
#        host.cmd('timeout '+str(flooding_time)+'s hping3 --flood -a '+host.ip+' '+victims_ip)

# Start CLI 
net.build()
net.start()
t2 = time()
print('Time to Start is ',t2-t1)

# Emulate Traffic 
hosts = [net.getNodeByName('h'+str(i)) for i in range(num_hosts)]
switch = net.getNodeByName('s0')
collector = net.getNodeByName('hc')

# Open Wireshark on first Host we can find
switch.sendCmd('sudo ovs-ctl start')
hosts[3].sendCmd('sudo wireshark -i h3-eth0 -k &')
hosts[3].monitor()
#collector.sendCmd('sudo wireshark -i hc-eth0 -k &')
#collector.monitor()

flood_thread = threading.Thread(target=traffic_simulation,args=(hosts))
flood_thread.start()

# Estimate Utility Function.
CLI( net )
flood_thread.join()
t3 = time()
net.stop()
t4 = time()
print('Time to tear down is ',t4-t3)
