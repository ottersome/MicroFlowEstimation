#!/usr/bin/python
import scapy.all as scapy
import time
import os
import numpy as np
import argparse
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

#### Config ####

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--dest_MAC',type=str,required=True)
    args.add_argument('--dest_IP',type=str,required=True)
    args.add_argument('--pps',type=str,required=True)
    args.add_argument('--run_time',type=float,required=True)
    return args.parse_args()


srcMAC = os.popen('ifconfig | grep HWaddr | cut -dH -f2 | cut -d\  -f2').read().strip()
srcIP = os.popen('ifconfig | grep "inet addr" | cut -d: -f2 | cut -d\  -f1 | head -n1').read().strip()
thisHost = os.popen('ifconfig | sed -n \'s/.*\\(h[0-9]*\\)-eth.*/\\1/p\'').read().strip()

logger.info('Using your srcMac {} srcIP {} and host {}'.format(
    srcMAC,srcIP,thisHost))

dataPrefix = "hello "
args = parse_args()

##### Main #####
# TODO maybe used this as arguments and ask parent to  be responsible 
# of avoiding clashes
src_port = np.random.randint(1000,60000,size=1)
dest_port = np.random.randint(1000,60000,size=1)

headers = scapy.Ether(src=srcMAC, dst=args.dest_MAC) / scapy.IP(src=srcIP, dst=args.dest_IP)/scapy.UDP(flags="A", sport=src_port, dport=dest_port)

s = scapy.conf.L2socket()
i = 1
endTime = time.time() + args.run_time
while time.time() <= endTime:
	p = headers / (dataPrefix + str(i))
	i = i+1
	#scapy.sendp(p, verbose=0)
	s.send(p)
	time.sleep(1.0/args.pps)
	#time.sleep(1.0/700)
