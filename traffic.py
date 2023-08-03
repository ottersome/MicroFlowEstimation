import logging
from mininet.node import Host, Node
from typing import List

logger = logging.getLogger(__name__)

def traffic_simulation(simulation_time: int,hosts: List[Host]):
    num_hosts = len(hosts)
    for i in range(num_hosts):
        send_str =""
        for j in range(num_hosts):
            # TODO figur out what N shoudl be 
            amp = " & disown " if i != num_hosts else ""
            send_str = f'timeout {simulation_time}s sourcesonoff -n 1 --transmitter-udp'+\
                             ' --destination '+str(hosts[j].IP()) +\
                             ' --don-alpha ' + "0.9" +\
                             ' --doff-alpha ' + "0.9" + amp
            hosts[i].cmd(send_str)
            logging.debug(f'for simuulation_time {simulation_time} and host_ip {hosts[i].IP()}')
            logging.debug('h'+str(i)+':'+send_str)
