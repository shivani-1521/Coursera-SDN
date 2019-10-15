from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
	
        Topo.__init__(self, **opts)
        
	agCount = 1
	edgeCount = 1
	hostCount = 1
	coreSwitch = self.addSwitch('c1')
	for z in range(fanout):
		switch = self.addSwitch('a%s' % agCount)
		agCount += 1
		self.addLink(switch, coreSwitch, **linkopts1);
		for y in range(fanout):
			eSwitch = self.addSwitch('e%s'%edgeCount)
			edgeCount += 1
			self.addLink(eSwitch, switch, **linkopts2);
			for x in range(fanout):
				host = self.addHost('h%s'%hostCount)
				hostCount += 1
				self.addLink(host,eSwitch, **linkopts3); 
        
                    
topos = { 'custom': ( lambda: CustomTopo({'bw':10,'delay':'1ms'},{'bw':8,'delay':'2ms'},{'bw':4,'delay':'4ms'},fanout=2) ) }

def simpleTest():
   "Create and test a simple network"
   ctopo = CustomTopo({'bw':10,'delay':'1ms'},{'bw':8,'delay':'2ms'},{'bw':4,'delay':'4ms'},fanout=2)
   net = Mininet(ctopo)
   net.start()
   print "Dump all host connections"
   dumpNodeConnections(net.hosts)
   print "Test the network connection"
   net.pingAll()
   net.stop()

if __name__ == '__main__':
  
   setLogLevel('info')
   simpleTest()