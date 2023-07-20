from mininet.topo import Topo

class ThickTopo(Topo):
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

topos = {'ThickTopo': (lambda :  ThickTopo())
         }
