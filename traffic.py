import logging
from mininet.node import Host, Node
from typing import List
import numpy as np

traffic_logger = logging.getLogger(__name__)
traffic_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./logs/traffic.log')
fh.setLevel(logging.DEBUG)
traffic_logger.addHandler(fh)
traffic_logger.propagate = False

def traffic_simulation(simulation_time: int,hosts: List[Host]):
    num_hosts = len(hosts)
    for i in range(num_hosts):
        send_str =""
        weibull_k = int(np.random.normal(20, 4, 1))
        for j in range(num_hosts):
            if i==j:continue
            # TODO figur out what N shoudl be 
            amp = " & disown " if i != num_hosts else ""
            send_str = 'sourcesonoff -n --transmitter-udp'+\
                             ' --destination '+str(hosts[j].IP()) +\
                             ' --stop-after '+str(int(simulation_time*1e9)) +\
                             ' --don-max 100' +\
                             ' --don-k '+str(weibull_k) +\
                             ' --don-type=Weibull' +\
                             ' --don-lambda=1'+amp
                             #' --doff-alpha ' + str(don_doff_alpha) + amp
            hosts[i].cmd(send_str)
            traffic_logger.debug(f'for simuulation_time {simulation_time} and host_ip {hosts[i].IP()}')
            traffic_logger.debug('h'+str(i)+':'+send_str)

def traffic_simulation_w_rates(simulation_time: int,hosts: List[Host], mean: float, var: float):
    """Simulate traffic with fixed, deterministic rates. 
    Simple, fixed-rate and fixed-size packets will be sent by scapy at rate chosen 
    at random from Gaussian Distribution.  
    """
    num_hosts = len(hosts)
    for i in range(num_hosts):
        send_str =""
        #  weibull_k = int(np.random.normal( 20, 4,1))
        rate = np.random.normal(mean,var,1).item()
        for j in range(num_hosts):
            if i==j:continue
            # TODO figur out what N shoudl be 
            amp = " & disown " if i != num_hosts else ""
            send_str = 'sudo python ./sendPackets.py'\
                    f' --dest_IP {hosts[j].IP()}'\
                    f' --dest_MAC {hosts[j].MAC()}'\
                    f' --pps {rate}'\
                    f' --run_time {simulation_time}' + amp
            hosts[i].cmd(send_str)
            traffic_logger.debug('h'+str(i)+':'+send_str)
