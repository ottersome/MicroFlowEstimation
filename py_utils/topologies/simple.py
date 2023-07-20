from mininet.topo import Topo

class SimpleTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Start Switch
        switch = self.addSwitch('switch')
        
        # Start Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        self.addLink(switch,h1)
        self.addLink(switch,h2)
        self.addLink(switch,h3)

class DiamondTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Start Switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Start Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        self.addLink(h1,s1)
        self.addLink(h1,s2)
        self.addLink(s1,h2)
        self.addLink(s2,h2)

class SimpleMicroflowEstTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Single Switch
        s1 = self.addSwitch('s1')
        
        # Start Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h1')

        end_host = self.addHost('end_host')


        self.addLink(h1,s1)
        self.addLink(h2,s1)
        self.addLink(h3,s1)

        self.addLink(s1,end_host)

topos = {'diamond': (lambda :  DiamondTopology()),
         'SimpleMicroflowEstTopo': (lambda: SimpleMicroflowEstTopo())
         }
