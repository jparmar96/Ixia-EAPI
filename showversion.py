#!/usr/bin/python
# -*- coding: utf-8 -*-
#For python3: pip install jsonrpclib-pelix
#For python2: pip install jsonrpclib
from jsonrpclib import Server
from pprint import pprint
import os
import json


resp = switch.runCmds(1,["show interfaces status connected"],"json")
pprint(resp)

for interface in resp[0]['interfaceStatuses'].keys():
    #print(interface)
    if interface == "Management1":
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["configure", "interface "+ interface, "description eapi-configured"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["configure", "interface "+ interface, "no description"],"json")
        pprint(resp)
        resp = switch.runCmds(1,["show interfaces " + interface + " description"],"json")
        pprint(resp)
