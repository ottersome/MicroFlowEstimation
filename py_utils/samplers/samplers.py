from scapy.all import PacketList, Packet
import logging

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.FileHandler('./logs/sampler.log'))
_logger.setLevel(logging.DEBUG)

r"""
" This will will only take packets that woudl've been observed under a sampling regime
" Time given will be in nanon seconds(1e9)
"""
def sample_packets(packets:PacketList, offtime:float,ontime:float)-> PacketList:
    # Assume they are already ordered
    currPacketList = PacketList([])
    on_p_off_time = ontime+ offtime
    for packet in packets:
        #  _logger.debug('Packet time {}, remainder {}.'.format(packet.time, packet.time % on_p_off_time))
        if packet.time % on_p_off_time <= ontime:
            currPacketList.append(packet)
    return currPacketList

# TODO()
r"""
" Quick as in QuickSort. 
    Will use Quick Sort to find the limit of samples.
"""
def quick_sampler(packets:PacketList, offtime:float,ontime:float):
    pass

