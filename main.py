from py_utils.topologies.thick import RoundTopology
from py_utils.controllers.POX import POX
from math import sqrt
from datetime import date
from mininet.net import Mininet
from typing import List
from mininet.node import (
     OVSSwitch,
     OVSController,
     RemoteController,
     Controller,
     UserSwitch,
     Host,
     Node)
from mininet.cli import CLI
from time import time
import os
import logging
from traffic import traffic_simulation
import threading
import configparser
import pwd

## Some Configs
global_config = configparser.ConfigParser()
with open('./controller_params.conf') as f:
    global_config.read_file(f)
config = global_config['DEFAULT']
log_file = None if config['log_file'] == "" else config['log_file']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.info('**⚙️ Your Configs **')
for k,v in dict(config).items():
    logger.info('{}:{}'.format(k,v))
logging.info('*******************\n')
dir_owner = pwd.getpwuid(os.stat('./').st_uid)[0]
cur_dir = os.getcwd()
logging.info(f'Will use dumpcap as user 🧑{dir_owner}')
logging.info(f'Will work under dir 📁{cur_dir}')


## This is for Ryu Remote Controller
c0 = RemoteController('c0',ip='127.0.0.1',port=6653, protocols="OpenFlow13")

t1 = time()

## Start topology and mininet
num_hosts = int(sqrt(config.getint("flows"))) 
topo = RoundTopology(num_hosts,collector_port=config.getint('collector_port'))
net = Mininet(topo=topo,
              switch=OVSSwitch,
              build=False,
              #  controller=Controller,
              controller=c0,
              autoSetMacs=True,
              )

# Start CLI
net.build()
net.start()
t2 = time()
logger.info('⏲️ Time to Start is {}'.format(t2-t1))

# Emulate Traffic

hosts = [net.getNodeByName('h'+str(i)) for i in range(num_hosts)]
switch = net.getNodeByName('s0')
#  print(switch)
collector = net.getNodeByName('hc')

collector.setIP(config['collector_ip'])
collector.setMAC(config['collector_mac'])

dump_file_name = config['dumppcap_file'].format(date.today())
logger.info(f'📝 Writing log file to: {dump_file_name}')
colelcting_time = config.getint('traffic_sim_time') + 10
collector.cmd(f"runuser -l {dir_owner} -c 'dumpcap -i hc-eth0 -w {cur_dir}/{dump_file_name} &'")
#hosts[0].cmd('sudo wireshark -i h0-eth0 -k &')

logger.info('First Host MAC: {}'.format(hosts[0].MAC()))
logger.info('Collector MAC: {}'.format(collector.MAC()))
logger.info('Switch MAC: {}'.format(switch.MAC()))

#  collector.cmd("ovs-vsctl set bridge s0 protocols=OpenFlow13")
#  hosts[3].cmd("wireshark -i h3-eth0 -k &")


flood_thread = threading.Thread(
        target=traffic_simulation,
        args=(config.getint('traffic_sim_time'),hosts)
        )
flood_thread.start()

# Estimate Utility Function.
CLI( net )
flood_thread.join()
t3 = time()
net.stop()
t4 = time()
logger.info('⏲️a Time to tear down is {}'.format(t4-t3))
