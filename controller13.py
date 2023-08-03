# -*- coding: utf-8 -*-

"""
Ryu Tutorial Controller

This controller allows OpenFlow datapaths to act as Ethernet Hubs. Using the
tutorial you should convert this to a layer 2 learning switch.

See the README for more...
"""

from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.lib.mac import haddr_to_bin
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib.dpid import dpid_to_str
from ryu import cfg
import pprint
import inspect

pp = pprint.PrettyPrinter(indent=4)

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mac_to_port['s0'] = {}
        self.config = cfg.CONF
        self.config.register_opts([
            cfg.StrOpt('collector_ip',default="10.0.0.200",help='IP for collector'),
            cfg.StrOpt('collector_mac',default="00:00:00:00:01:A4",help='MAC for collector'),
            cfg.IntOpt('collector_port',default=6600,help='Port for collector'),
            cfg.FloatOpt('sample_probability',default=1,help='NetFlow-like probability of sampling'),
            ])
        # TODO: hard code the mac address of collector

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        '''
        Handshake: Features Request Response Handler

        Installs a low level (0) flow table modification that pushes packets to
        the controller. This acts as a rule for flow-table misses.
        '''
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.logger.info("Handshake taken place with {}".format(dpid_to_str(datapath.id)))
        # THIS IS CRITICAL TO OBTAINE "PacketIn"  Events
        self.__add_flow(datapath, match, actions, ofproto.OFP_DEFAULT_PRIORITY-1)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        '''
        Packet In Event Handler

        Takes packets provided by the OpenFlow packet in event structure and
        floods them to all ports. This is the core functionality of the Ethernet
        Hub.
        '''
        msg = ev.msg
        datapath = msg.datapath

        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = msg.datapath.id
        pkt = packet.Packet(msg.data)
        #pp.pprint(dir(msg.match))
        #for attribute in inspect.getmembers(msg.match):
        #    print(attribute)
        in_port = msg.match.get('in_port')
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        eth = pkt.get_protocol(ethernet.ethernet)
        dst = eth.dst
        src = eth.src

        #ipv4
        ip_deets = pkt.get_protocol(ipv4.ipv4)# This returns null it seems. Not yet reaching IPV4 perhaps?
        print("Ip Details ",ip_deets)
        #ip_dst = ip_deets.dst
        #ip_src = ip_deets.src

        #self.logger.info("packet in %s-->%s through port %s", ip_src, ip_dst, msg.in_port)
        self.logger.info("packet in %s-->%s through port %s", src, dst, in_port)

        # This is how we learn our ports (very simple):
        self.mac_to_port.setdefault(dpid,{})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
            self.logger.debug('We FLOODIN')

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        # Add Flow To Collector
        self.logger.info('Sampling packets to : '+str(self.config['collector_port']))
        ## SAMPLING (🚧 Under Construction)
        actions.append(datapath.ofproto_parser.OFPActionOutput(self.config['collector_port']))
        #  actions += datapath.ofproto_parser.NXActionSample(
        #          probability=self.config['sample_probability'],
        #          )
        ## Add Flow for Precise Match
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(
                    in_port=in_port, eth_dst=dst, eth_src=src
                    )
            self.__add_flow(datapath, match, actions, ofproto.OFP_DEFAULT_PRIORITY+1)
        ## Broadcast it since we don't know where to send it for now
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=msg.buffer_id,
                                  in_port=in_port,
                                  actions=actions,
                                  data=data)

        self.logger.info("Sending packet out")
        datapath.send_msg(out)
        return

    def __add_flow(self, datapath, match, actions, priority):
        '''
        Install Flow Table Modification

        Takes a set of OpenFlow Actions and a OpenFlow Packet Match and creates
        the corresponding Flow-Mod. This is then installed to a given datapath
        at a given priority.
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst)
        self.logger.info("Flow-Mod written to {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)

