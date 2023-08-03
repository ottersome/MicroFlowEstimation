from scapy import sessions
from scapy.all import  PacketList, rdpcap,wrpcap
from time import time
from typing import List
from py_utils.samplers.samplers import sample_packets
import matplotlib.pyplot as plt
import argparse
import re
import logging



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_file',type=str,required=True)
    parser.add_argument('--sampled_packets',type=str,required=True)

    return parser.parse_args()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    fh = logging.FileHandler('./logs/pcap_sampler.log')
    logger.addHandler(fh)
    args = get_args()
    logger.info(f'📂 Opening {args.pcap_file}')

    ## Read File in One Go
    scapy_cap = rdpcap(args.pcap_file)
    logging.info('Filtering out non-UDP packets.')
    
    ## Obtain only UDP Packets
    #udp_packets = PacketList([ packet for packet in scapy_cap if packet.haslayer('UDP')])
    udp_packets = scapy_cap
    
    ## Sample Packets
    sampled_packets = sample_packets(udp_packets, 2,1)
    logging.info(f'🗃️ Saving sampled packets to {args.sampled_packets}')
    wrpcap(args.sampled_packets,sampled_packets)

    ## Do Inference on the Samplers
