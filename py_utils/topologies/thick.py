from mininet.topo import Topo

class ThiccShallow(Topo):
    def __init__(self, num_flows):
        Topo.__init__(self)

        # Single Switch
        self.s1 = self.addSwitch('s1',use_v6=False)
        
        # Start Hosts
        self.hi = [None]*num_flows
        for i in range(num_flows):
            self.hi[i] = self.addHost('h'+str(i), use_v6=False)
            self.addLink(self.hi[i],self.s1 )

        self.end_host = self.addHost('end_host',use_v6=False)
        self.addLink(self.s1,self.end_host)

class RoundTopology(Topo):
    def __init__(self, num_hosts):
        Topo.__init__(self)

        # Single Switch
        self.switch = self.addSwitch('s0',use_v6=False)

        # Collector
        self.collector = self.addHost('hc',use_v6=False)
        self.addLink(self.switch, self.collector)
        
        # Start Hosts
        self.hi = [None]*num_hosts
        for i in range(num_hosts):
            self.hi[i] = self.addHost('h'+str(i), use_v6=False)
            self.addLink(self.hi[i],self.switch )


topos = {'ThiccShallow': (lambda :  ThiccShallow())
         }
