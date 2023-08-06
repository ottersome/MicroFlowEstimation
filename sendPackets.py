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
    args.add_argument('--pps',type=float,required=True)
    args.add_argument('--run_time',type=float,required=True)
    return args.parse_args()


srcMAC   = os.popen("ip a | sed -n -E '/eth/,$p' | grep -oE '([0-F]{2}:){5}[0-F]{2}' | awk 'NR==1'").read().strip()
srcIP    = os.popen("ip a | sed -n -E '/eth/,$p' | grep -oE '(192|10)\.([0-9]{1,3}\.){2}[0-9]{1,3}' | awk 'NR==1'").read().strip()
iface = os.popen("ip a | grep -oE 'h[0-9]+-eth0' | awk 'NR==1'").read().strip()
thisHost = os.popen('hostname').read().strip()

logger.info('Using your srcMac {} srcIP {} and host {}'.format(
    srcMAC,srcIP,thisHost))

dataPrefix = "hello "
args = parse_args()

##### Main #####
# TODO maybe used this as arguments and ask parent to  be responsible 
# of avoiding clashes
src_port = np.random.randint(1000,60000,size=1).item()
dest_port = np.random.randint(1000,60000,size=1).item()

headers = scapy.Ether(src=srcMAC,dst=args.dest_MAC) /\
           scapy.IP(src=srcIP,dst=args.dest_IP)/\
           scapy.UDP(sport=src_port,dport=dest_port)

#  s = scapy.conf.L2socket()
i = 1
endTime = time.time() + args.run_time
while time.time() <= endTime:
    p = headers / scapy.Raw(dataPrefix + str(i))
    i = i+1
    scapy.sendp(p, verbose=2, iface=iface)
    #  s.send(p)
    time.sleep(1.0/args.pps)
    print('Sent')
	#time.sleep(1.0/700)
