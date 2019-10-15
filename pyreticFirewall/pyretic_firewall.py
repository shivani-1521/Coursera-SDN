from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.modules.mac_learner import mac_learner
import os

# insert the name of the module and policy you want to import
# from pyretic.examples.mac_learner import <mac_learner>

policy_file = "%s/pyretic/pyretic/examples/firewall-policies.csv" % os.environ[ 'HOME' ]

def main():
    # Copy the code you used to read firewall-policies.csv from the Pox Firewall assignment
    policyFileContent = open(policy_file)
    # skip first line
    policyFileContent.readline()

    # start with a policy that doesn't match any packets
    not_allowed = none

    while True:
        line = policyFileContent.readline()
        if not line:
            break
        print line
        # info[1] == mac_0, info[2] == mac_1
        info = line.split(',')
        info[2].strip('\n')

        # and add traffic that isn't allowed
        not_allowed = union( [not_allowed, match(dstmac=EthAddr(info[2])) >>
            match(srcmac=EthAddr(info[1]))] )
        not_allowed = union( [not_allowed, match(dstmac=EthAddr(info[1])) >>
            match(srcmac=EthAddr(info[2]))] )

    # express allowed traffic in terms of not_allowed - hint use '~'
    allowed = ~not_allowed

    # and only send allowed traffic to the mac learning (act_like_switch) logic
    return allowed >> mac_learner()
