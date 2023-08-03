from scapy import sessions
from scapy.all import *
from time import time
import matplotlib.pyplot as plt
import argparse
import re
import logging

file_logger = logging.getLogger(__name__)
fh = logging.FileHandler('./parsing.log')
file_logger.addHandler(fh)
file_logger.setLevel(logging.DEBUG)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_file',type=str,required=True)

    return parser.parse_args()

def get_tot_len_flow(packetList: PacketList) -> int: 
    tot_size: int = 0
    for p in packetList:
        tot_size += p.getlayer('UDP').len
    return tot_size


def get_length_statistics(sesh:sessions)-> dict[str,int]:
    sesh_lengths = pcap_flow.sessions()
    session_lengths = {}
    # Initialize
    file_logger.debug('Below are all the keys we have')
    file_logger.debug(str(sessions.keys()))
    for k in sessions.keys(): session_lengths[k] = 0
    for k,packetlist in sessions.items():
        if 'UDP' not in k: continue
        session_lengths[k] += get_tot_len_flow(packetlist)
    return session_lengths



########## Configuration ##########
logger=logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.ERROR)
args = get_args()

# Load To Memory
t0 = time()
logger.info(f'Loading the file {args.pcap_file}')
pcap_flow =rdpcap(args.pcap_file)
t1 = time()
logger.debug('It took {} seconds to load the pcap file'.format(t1-t0))
logger.info('Getting Sessions')
sessions = pcap_flow.sessions()
num_sessions = len(sessions)
logger.info('Getting Session Lengths')
lengths = get_length_statistics(sessions)
lengths = dict(sorted(lengths.items(), key= lambda item: item[1],reverse=True))
logger.info(f'We have a final amount of {len(lengths.keys())} flows')
## Plot The Info


fig, axs = plt.subplots(1,2)
#axs[0].bar(range(num_sessions),lengths.values(),tick_label=lengths.keys)
axs[0].bar(range(num_sessions),lengths.values())
axs[0].set_title('Size of Flows')

axs[1].hist(lengths.values(),bins=15)
axs[1].set_title('Flow Length Distributions')

plt.show()

