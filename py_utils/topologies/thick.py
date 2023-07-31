from mininet.topo import Topo

class ThiccShallow(Topo):
    def __init__(self, num_flows):
        Topo.__init__(self)

        # Single Switch
        self.s1 = self.addSwitch('s1')
        
        # Start Hosts
        self.hi = [None]*num_flows
        for i in range(num_flows):
            self.hi[i] = self.addHost('h'+str(i))
            self.addLink(self.hi[i],self.s1 )

        self.end_host = self.addHost('end_host')
        self.addLink(self.s1,self.end_host)

class RoundTopology(Topo):
    def __init__(self, num_hosts, collector_port):
        Topo.__init__(self)

        # Single Switch
        self.switch = self.addSwitch('s0')

        # Collector
        self.collector = self.addHost('hc')
        self.addPort(self.switch,self.collector, )
        self.addLink(self.switch, self.collector,port1=collector_port, port2=0)
        
        # Start Hosts
        self.hi = [None]*num_hosts
        for i in range(num_hosts):
            self.hi[i] = self.addHost('h'+str(i))
            self.addLink(self.hi[i],self.switch )


topos = {'ThiccShallow': (lambda :  ThiccShallow())
         }
