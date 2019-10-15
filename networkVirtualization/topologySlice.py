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


class TopologySlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Slicing Module")
        
        
    """This event will be raised each time a switch will connect to the controller"""
    def _handle_ConnectionUp(self, event):
        
        # Use dpid to differentiate between switches (datapath-id)
        # Each switch has its own flow table. As we'll see in this 
        # example we need to write different rules in different tables.
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
        
        """ Add your logic here """
        if dpid == '00-00-00-00-00-01':
            fm = of.ofp_flow_mod()
            fm.match.in_port = 1
            fm.actions.append(of.ofp_action_output(port=3))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 2
            fm.actions.append(of.ofp_action_output(port=4))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 3
            fm.actions.append(of.ofp_action_output(port=1))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 4
            fm.actions.append(of.ofp_action_output(port=2))
            event.connection.send(fm)
                             
        elif dpid == '00-00-00-00-00-02' or dpid == '00-00-00-00-00-03':
            fm = of.ofp_flow_mod()
            fm.match.in_port = 1
            fm.actions.append(of.ofp_action_output(port=2))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 2
            fm.actions.append(of.ofp_action_output(port=1))
            event.connection.send(fm)
                             
        elif dpid == '00-00-00-00-00-04':
            fm = of.ofp_flow_mod()
            fm.match.in_port = 1
            fm.actions.append(of.ofp_action_output(port=3))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 2
            fm.actions.append(of.ofp_action_output(port=4))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 3
            fm.actions.append(of.ofp_action_output(port=1))
            event.connection.send(fm)
                             
            fm = of.ofp_flow_mod()
            fm.match.in_port = 4
            fm.actions.append(of.ofp_action_output(port=2))
            event.connection.send(fm)
                             

def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Topology Slicing module
    '''
    core.registerNew(TopologySlice)