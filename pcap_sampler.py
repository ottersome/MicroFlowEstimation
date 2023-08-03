from scapy import sessions
from scapy.all import  PacketList, rdpcap,wrpcap
from time import time
from typing import List
from py_utils.samplers.samplers import sample_packets
import matplotlib.pyplot as plt
import argparse
import re
import hyperloglog
import logging


hll = hyperloglog.HyperLogLog(0.01)
def hll_impl(txt)-> int:
    hll.add(txt)
    return len(hll)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_file',type=str,required=True)
    parser.add_argument('--sampled_packets',type=str,required=True)
    #parser.add_argument('--storage_units',type=str,required=True)

    return parser.parse_args()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler('./logs/pcap_sampler.log')
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    args = get_args()
    logger.info(f'📂 Opening {args.pcap_file}')

    ## Read File in One Go
    scapy_cap = rdpcap(args.pcap_file)
    logging.info('Filtering out non-UDP packets.')

    ## Obtain only UDP Packets
    udp_packets = PacketList([])
    list_keys = []
    for packet in scapy_cap:
        if "UDP 10.0.0" in str(packet) and "Raw" not in str(packet):
            udp_packets.append(packet)
            if str(packet) not in list_keys:
                list_keys.append(str(packet))
    logger.info('Final keys with length {}:\n{}'.format(len(list_keys),list_keys))

    ## Sample Packets
    sampled_packets = sample_packets(udp_packets, 2,1)
    logging.info(f'🗃️ Saving sampled packets to {args.sampled_packets}')
    wrpcap(args.sampled_packets,sampled_packets)

    ## Do Inference on the Samplers
