# Introduction

This is a repository to test a few algorithms to detect 
best sampling rate on a network for decision making.
This is part of my graduate research thesis. 
As the testbench I will use OpenFlow, Mininet.
References to software, tutorials, guides and paper I used will (not exhaustively)
be listed below.




# Description

Project is based in mininet + openVSwitch + Ryu Controller. 
Mininet is in charge of simulating the namespaces, openVSwitch receives rules for 
forwarding flows, Ryu Controller handles the communication between the logic layer and the
forwarding layer. This is to say, the controller will observe the (possible multiple)
switches in the network and will communicate with them new rules according to whatever
criteria our logic sets.

## More Specifically


(This might be incorrect as I change the topology and its surrounding environment quite
frequently)

Topology is circular see (./py\_utils/topologies/thick.py).
When a hosts sends a packet to controller it will immediately bind its mac address to its
r
ingress port. That way we can form a static map of where the mac addresses come from. 
With a map in place the controller can communicate with the switches the rules to set in
terms of ethernet/mac addresses. 
Additionally, every rule will have appended to it a sub-rule to send statistics to
collector at a specified rate. 

(Comment: I am not sure yet whether to make the collector be the same as the controller)

# 🏃How to Run

## Traffic Generation

1. Export path to your OpenVSwitch executables:
   
   ```
   export PATH=$PATH:/path/to/your/openvswitch/executables
   ```
2. Run openVSwitch
   
   ```
   sudo ovs-ctl start
   ```
   You can see [this](https://docs.openvswitch.org/en/stable/intro/install/general/)
   page to understand how to run it. 

3. Run our ryu application: `ryu-manager controller13.py`

   You can install ryu via `pip install ryu`
4. Make sure your config is correct. See `./controller_params.conf`
5. Run the `traffic_generation.py` python script to generate your traffic.
6. 💫Retrieve your generated traffic.

## For Sampling:

1. Run `./pcap_sampler.py` with arguments denoting where the traffic capture file is

# TODOS

- [x] Create Basic Topologies
- [x] Setup Ryu Controller
    - [x] Request Features
    - [x] Learn Topology
    - [x] Forward to Collector
- [x] Setup Traffic
    - [ ] Setup simple Scapy Traffic (skip for now)
    - [x] Setup Self-Similar Traffic
    - [ ] Confirm Self-Similar Statistics
- [ ] Implement Time Sampling
- [ ] Create a `dpctl.c` modification to allow for sampling in the time domain.

# Dependencies

1. [openVSwitch]
1. [ryu]
1. [mininet]
1. [sourcesonoff]
1. [wireshark]
1. [scapy]

# References:

- [OpenFlow Software Switch(BOFUSS)](https://github.com/CPqD/ofsoftswitch13/tree/master)
  1. [Netbee](https://github.com/netgroup-polito/netbee.git)
- [Mininet Simulator](http://mininet.org/)
- [Self-Similar Traffic]()
- [Nixira Extension Netflow Sample in Ryu](https://ryu.readthedocs.io/en/latest/nicira_ext_ref.html#ryu.ofproto.ofproto_v1_3_parser.NXActionSample)
- [HyperLogLog Algorithm](https://en.wikipedia.org/wiki/HyperLogLog)

