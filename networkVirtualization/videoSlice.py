from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class VideoSlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda:defaultdict(lambda:None))
        
        '''
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        '''

        self.portmap = {('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:03'), 80): 2, #'00-00-00-00-00-03'
		   ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:04'), 80): 2, #'00-00-00-00-00-03'
           ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:03'), 80): 2, #'00-00-00-00-00-03'
           ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:04'), 80): 2, #'00-00-00-00-00-03'
           ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:03'), 22): 1, #'00-00-00-00-00-03'           
		   ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:04'), 22): 1, #'00-00-00-00-00-03'
           ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:03'), 22): 1, #'00-00-00-00-00-03'
           ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:04'), 22): 1, #'00-00-00-00-00-03'           
           
           ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:03'), 80): 2, #'00-00-00-00-00-04'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:04'), 80): 2, #'00-00-00-00-00-04'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:03'), 80): 2, #'00-00-00-00-00-04'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:04'), 80): 2, #'00-00-00-00-00-04'

           ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:01'), 80): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:01'), 80): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:02'), 80): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:02'), 80): 1, #'00-00-00-00-00-01'

           ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:01'), 80): 2, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:01'), 80): 2, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:02'), 80): 2, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:02'), 80): 2, #'00-00-00-00-00-01'
           ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:01'), 22): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:01'), 22): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:02'), 22): 1, #'00-00-00-00-00-01'
		   ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:02'), 22): 1} #'00-00-00-00-00-01'

    def _handle_LinkEvent (self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)

        log.debug ("link %s[%d] <-> %s[%d]",
                   sw1, l.port1,
                   sw2, l.port2)

        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2


    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        tcpp = event.parsed.find('tcp')

        def install_fwdrule(event,packet,outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port = outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)

            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug("Got unicast packet for %s at %s (input port %d):",
                          packet.dst, dpid_to_str(event.dpid), event.port)

                try:
                    if event.parsed.find('arp') or event.parsed.find('icmp'):
                        #log.debug("ARP packet type has no transport ports, flooding.")
                        install_fwdrule(event,packet,of.OFPP_FLOOD)
                    elif event.parsed.find('tcp'):
                        if tcpp.dstport == 80:
                            outport = self.portmap[(this_dpid, EthAddr(packet.src),EthAddr(packet.dst), tcpp.dstport)]
                            install_fwdrule(event, packet, outport)
                        elif tcpp.srcport == 80:
                            outport = self.portmap[(this_dpid, EthAddr(packet.src),EthAddr(packet.dst), tcpp.srcport)]
                            install_fwdrule(event, packet, outport)
                        elif tcpp.dstport == 22:
                            outport = self.portmap[(this_dpid, EthAddr(packet.src),EthAddr(packet.dst), tcpp.dstport)]
                            install_fwdrule(event, packet, outport)                            
                        elif tcpp.srcport == 22:
                            outport = self.portmap[(this_dpid, EthAddr(packet.src),EthAddr(packet.dst), tcpp.srcport)]
                            install_fwdrule(event, packet, outport)                            
                            
                            
                        log.debug("Sw: %s adding rule Src: %s Dst: %s Dport: %s out port: %d", this_dpid, packet.src, packet.dst, tcpp.dstport, outport)
                
                except KeyError:
                    log.debug("TCP packet type has no transport ports, flooding.")
                    install_fwdrule(event,packet,of.OFPP_FLOOD)
                except AttributeError:
                    log.debug("Generic packet type has no transport ports, flooding.")

                    # flood and install the flow table entry for the flood
                    install_fwdrule(event,packet,of.OFPP_FLOOD)

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        forward()


    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
        

def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Video Slicing module
    '''
    core.registerNew(VideoSlice)