from math import comb
from scapy import sessions
from scapy.all import  PacketList, rdpcap,wrpcap
from time import time
from typing import List
from py_utils.samplers.samplers import sample_packets
import numpy as np
import matplotlib.pyplot as plt
import argparse
from tqdm import tqdm
import re
import hyperloglog
import logging

logger = logging.getLogger(__name__)
fh = logging.FileHandler('./logs/pcap_sampler.log')
logger.addHandler(logging.StreamHandler())
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_file',type=str,required=True)
    #parser.add_argument('--sampled_packets',type=str,required=True)
    parser.add_argument('--low_samp_bound_exp',type=float,default=-24,required=False)
    parser.add_argument('--up_samp_bound_exp',type=float,default=48,required=False)
    parser.add_argument('--on_time',type=float,default=0.000000000001,required=False)
    #parser.add_argument('--storage_units',type=str,required=True)

    return parser.parse_args()

#TODO: Imporve with quicksort algoritm
# NOT FINISHED
def stateful_sample_estimate(packets: PacketList,
                    offtime:float,
                    mem_units:int=40,
                    offset:float = 1.0#Time offset from which to peek
                    ) -> int:
    """Will only sample within a window of time
    Will make last seen packet as its *state*
    """
    hll = hyperloglog.HyperLogLog(0.01)
    init_time = packets[0].time + offset
    next_sample_time = init_time+offtime
    cnt = 0
    for i in range(len(packets)):
        if packet.time < init_time: continue
        if packet[i].time < next_sample_time and packet[i+1].time > next_sample_time:
            hll.add(str(packet))
            next_sample_time += offtime
            cnt += 1

        if cnt >= mem_units: 
            break

    return len(hll)

def sample_estimate(packets:PacketList,
                    offtime:float,
                    ontime:float,
                    mem_units=40,
                    time_budget=3) -> int: 
    """ Will iterate over packages until it finds mem_units that fit withing the sampling time
    packets: filtered packet list
    offtime: "frequency". Time between on states
    ontime: Duration of on state
    mem_units: Limit on samples collected
    """
    # Assume they are already ordered
    hll= hyperloglog.HyperLogLog(0.01)
    on_p_off_time = ontime + offtime
    keys = []
    avg_gap_size = 0.0
    cnt = 0
    for packet in packets:
        if packet.time % on_p_off_time <= ontime :
            hll.add(str(packet))
            cnt +=1
            if cnt >= mem_units: break

    logger.debug(f'Average Gap : {avg_gap_size}')
    logger.debug(f'For offtime {offtime} we get {len(keys)} different flows')
    return len(hll)

if __name__ == '__main__':
    args = get_args()
    logger.info(f'📂 Opening {args.pcap_file}')

    ## Read File in One Go
    scapy_cap = rdpcap(args.pcap_file)
    logger.info('Filtering out non-UDP packets.')

    ## Obtain only UDP Packets
    udp_packets = PacketList([])
    list_keys = []
    for packet in scapy_cap:
        if "UDP 10.0.0" in str(packet):# and "Raw" not in str(packet):
            udp_packets.append(packet)
            if str(packet) not in list_keys:
                list_keys.append(str(packet))
    logger.info('☑️ Baseline amount of flows: {}'.format(len(list_keys)))
    correct_amount_flows = len(list_keys)


    ## Create an Array of Tests
    t0  = time()
    logger.info('Sampling across base 2 bounds: {}-{}'.format(
        args.low_samp_bound_exp,args.up_samp_bound_exp
        ))
    rates = np.logspace(
            args.low_samp_bound_exp,
            args.up_samp_bound_exp,1000,base=2)
    # TODO parallelize this ?
    estimates = {}
    ### Run Tests
    for rate in tqdm(rates):
        estimates[rate] = sample_estimate(udp_packets,1/rate,args.on_time)
    t1=time()
    logger.info('⏱  Sampling took {} seconds.'.format(t1-t0))

    logger.info('These are your estimates:{}'.format(estimates))
    l1_diffs = np.abs(np.array(list(estimates.values())) - correct_amount_flows)
    logger.info(f'Keys length {len(estimates.keys())} and l1_difs {len(l1_diffs)}')

    ## Plot results
    fig, ax = plt.subplots()
    ax.scatter(rates, l1_diffs,s=0.5)
    ax.set_xscale('log',basex=2)
    ax.set_xlabel('Sampling Rate')
    ax.set_ylabel('L1 from Correct Value')
    ax.set_title('Performance based on Sampling Rate')

    plt.show()

