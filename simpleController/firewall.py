from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''
import csv


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  

''' Add your global variables here ... '''
policyList = []
firstLine = True
with open(policyFile,'rb') as policies:

    csv_entries = csv.reader(policies, delimiter=',')
    for row in csv_entries:
        if firstLine:
            firstLine = False
            continue
        log.debug('raw data from csv file: %s ', row )
        policyList.append(row[1:])
    for rule in policyList:
        log.debug("rules: %s ", rule)

class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):    
        ''' Add your logic here ... '''
        for rule in policyList:
            match = of.ofp_match()
            log.debug( "rule[0]: %s" , rule[0] )
            match.dl_src = EthAddr(rule[0])
            match.dl_dst = EthAddr(rule[1])
            msg = of.ofp_flow_mod()
            msg.match = match
            # Empty action list means DROP
            # msg.action = 
            event.connection.send(msg)

    
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)