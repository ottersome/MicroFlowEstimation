from py_utils.topologies.thick import RoundTopology
from math import sqrt
from datetime import date
from mininet.net import Mininet
from typing import List
from mininet.node import (
     OVSSwitch,
     RemoteController,
     )
from mininet.cli import CLI
from time import time
import os
import argparse
import logging
from traffic import traffic_simulation, traffic_simulation_w_rates
import threading
import configparser
import pwd

## Some Configs
def parseargs():
    args = argparse.ArgumentParser()
    args.add_argument('-v',action='store_true',default=False)
    return args.parse_args()

args = parseargs()
logging_level =  logging.DEBUG if args.v else logging.INFO

global_config = configparser.ConfigParser()
with open('./controller_params.conf') as f:
    global_config.read_file(f)
config = global_config['DEFAULT']
log_file = None if config['log_file'] == "" else config['log_file']
gen_logger = logging.getLogger(__name__)
#  fh = logging.StreamHandler()
#  gen_logger.addHandler(fh)
gen_logger.setLevel(logging_level)

logging.info('**⚙️ Your Configs **')
for k,v in dict(config).items():
    gen_logger.info('{}:{}'.format(k,v))
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

## Build Network
net.build()
net.start()
t2 = time()
gen_logger.info('⏲️ Time to Start is {}'.format(t2-t1))

## Obtain references to hosts inside the entwork
hosts = [net.getNodeByName('h'+str(i)) for i in range(num_hosts)]
switch = net.getNodeByName('s0')
collector = net.getNodeByName('hc')

collector.setIP(config['collector_ip'])
collector.setMAC(config['collector_mac'])

dump_file_name = config['dumppcap_file'].format(date.today())
gen_logger.info(f'📝 Writing log file to: {dump_file_name}')
collector.sendCmd(f"runuser -l {dir_owner} -c "\
        f"'dumpcap -a duration:{config.getint('traffic_sim_time') +3}"\
        f" -i hc-eth0 -w {cur_dir}/{dump_file_name}'")

gen_logger.info('First Host MAC: {}'.format(hosts[0].MAC()))
gen_logger.info('Collector MAC: {}'.format(collector.MAC()))
gen_logger.info('Switch MAC: {}'.format(switch.MAC()))

## Emulate Traffic in Threads
traffic_sim_threads = threading.Thread(
        target=traffic_simulation_w_rates,
        args=(config.getint('traffic_sim_time'),hosts,12,4)
        )
traffic_sim_threads.start()

# Estimate Utility Function.
#  CLI( net ) # Useful foenor debugging
traffic_sim_threads.join()
gen_logger.info(f'🛑 Waiting for {config.getint("traffic_sim_time")}'\
        f' seconds while data is being collected in {cur_dir}/{dump_file_name}. Output of `dumpcap`:')
while collector.waiting:
    gen_logger.info(collector.monitor())
t3 = time()
net.stop()
t4 = time()
gen_logger.info('⏲️a Time to tear down is {}'.format(t4-t3))
