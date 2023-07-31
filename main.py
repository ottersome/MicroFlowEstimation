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
import configparser

global_config = configparser.ConfigParser()
with open('./controller_params.conf') as f:
    global_config.read_file(f)

config = global_config['DEFAULT']
print('Working with config: ',dict(config))

c0 = RemoteController('c0',ip='127.0.0.1',port=6653, protocols="OpenFlow13")

logging.basicConfig(level=logging.DEBUG,filename="./log")
print(f'Running with {config["flows"]} flows')

t1 = time()
# Start topology and mininet
num_hosts = int(sqrt(config.getint("flows"))) 
topo = RoundTopology(num_hosts,collector_port=config.getint('collector_port'))
net = Mininet(topo=topo,
              switch=OVSSwitch,
              build=False,
              #  controller=Controller,
              controller=c0,
              autoSetMacs=True,
              )
# As Per Our own experiments we have seen rates of 1e7
# So Cohens Rates *should* be okay
uniform_lower = 100
uniform_upper = 10000


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
            amp = " & disown "
            send_str = f'sudo timeout {config["traffic_sim_time"]} sourcesonoff -n 1 --transmitter-udp'+\
                             ' --destination '+str(hosts[j].IP()) +\
                             ' --don-alpha ' + "0.9" +\
                             ' --doff-alpha ' + "0.9" + amp
            hosts[i].cmd(send_str+amp)
            logging.debug('h'+str(i)+':'+send_str+amp)
        #if i != 0:
        #hosts[i].monitor()


# Start CLI 
net.build()
net.start()
t2 = time()
print('Time to Start is ',t2-t1)

# Emulate Traffic 
hosts = [net.getNodeByName('h'+str(i)) for i in range(num_hosts)]
switch = net.getNodeByName('s0')
print(switch)
collector = net.getNodeByName('hc')

collector.setIP(config['collector_ip'])
collector.setMAC(config['collector_mac'])

collector.cmd('sudo wireshark -i hc-eth0 -k &')
#hosts[0].cmd('sudo wireshark -i h0-eth0 -k &')

print('First Host MAC: {}'.format(hosts[0].MAC()))
print('Collector MAC: ',collector.MAC())
print('Switch MAC: ',switch.MAC())

#  collector.cmd("ovs-vsctl set bridge s0 protocols=OpenFlow13")
#  hosts[3].cmd("wireshark -i h3-eth0 -k &")

flood_thread = threading.Thread(target=traffic_simulation,args=(hosts))
flood_thread.start()

# Estimate Utility Function.
CLI( net )
flood_thread.join()
t3 = time()
net.stop()
t4 = time()
print('Time to tear down is ',t4-t3)
