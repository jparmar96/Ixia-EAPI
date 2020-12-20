#!/usr/bin/python
"""This script demonstrates how to get started with ixnetwork_restpy scripting.

"""
from pprint import pprint
from ixnetwork_restpy import SessionAssistant
import time

# create a test tool session
session_assistant = SessionAssistant(IpAddress='127.0.0.1',
                                     UserName='admin', Password='admin',
                                     LogLevel=SessionAssistant.LOGLEVEL_INFO,
                                     ClearConfig=True)
ixnetwork = session_assistant.Ixnetwork

#print(session_assistant.Session)

# create tx and rx port resources
port_map = session_assistant.PortMapAssistant()
port_map.Map('172.24.68.5', 5, 17, Name='Tx')
port_map.Map('172.24.68.5', 5, 18, Name='Rx')

port_map.Connect(ForceOwnership=True, HostReadyTimeout=20, LinkUpTimeout=60)
#print(port_map)

#Need to map Tx and Rx to vport1 and vport2
vport1 = ixnetwork.Vport.find(Name='^Tx')
vport2 = ixnetwork.Vport.find(Name='^Rx')

#Topology
topology1 = ixnetwork.Topology.add(Name='Topo1', Ports=vport1)
deviceGroup1 = topology1.DeviceGroup.add(Name='DG1' , Multiplier=4)

topology2 = ixnetwork.Topology.add(Name='Topo2', Ports=vport2)
deviceGroup2 = topology2.DeviceGroup.add(Name='DG2' , Multiplier=4)

#Add vports to topology, add ethernet and ipv4
ipv4 = deviceGroup1.Ethernet.add().Ipv4.add() #adding ethernet & ipv4 protocol
ipv4_2 = deviceGroup2.Ethernet.add().Ipv4.add() 
#ipv4 = ixnetwork.Topology.add(Ports=vport1).DeviceGroup.add(Multiplier=4).Ethernet.add().Ipv4.add() #adding ethernet & ipv4 protocol
#ipv4_2 = ixnetwork.Topology.add(Ports=vport2).DeviceGroup.add(Multiplier=4).Ethernet.add().Ipv4.add() 


#Add ip address, prefix, gateway
ipv4.Address.Increment(start_value='1.0.0.2', step_value='0.0.0.1')#set increment multivalue
#ipv4.info(ipv4.Address)#this is for logging at info level
#assert(ipv4.Address.Pattern.startswith('Inc:') is True)         # this is an example that assert statements can be used too.
ipv4.Prefix.Single('24')
ipv4.GatewayIp.Single('1.0.0.1')

#Configuring BGP and Network Groups
#ixnetwork.info('Configuring BgpIpv4Peer 1')
bgp1 = ipv4.BgpIpv4Peer.add(Name='Bgp1')
bgp1.DutIp.Increment(start_value='1.0.0.1', step_value='0.0.0.0')
bgp1.Type.Single('external')
bgp1.LocalAs2Bytes.Increment(start_value=101, step_value=0)

#ixnetwork.info('Configuring Network Group 1')
networkGroup1 = deviceGroup1.NetworkGroup.add(Name='BGP-Routes1', Multiplier='1')
ipv4PrefixPool = networkGroup1.Ipv4PrefixPools.add(NumberOfAddresses='10')
ipv4PrefixPool.NetworkAddress.Increment(start_value='10.10.0.1', step_value='0.0.0.1')
ipv4PrefixPool.PrefixLength.Single(32)


ipv4_2.Address.Increment(start_value='2.0.0.2', step_value='0.0.0.1')#set increment multivalue
ipv4_2.Prefix.Single('24')
ipv4_2.GatewayIp.Single('2.0.0.1')


#Start Topology
#topologies = ixnetwork.Topology.find().Start()
ixnetwork.StartAllProtocols(Arg1='sync')

#Create traffic item
traffic_item=ixnetwork.Traffic.TrafficItem.add(Name='Ipv4 traffic item sample', BiDirectional=True, TrafficType='ipv4', TrafficItemType='l2L3')
#Add endpoints to traffic
endpoint_Set= traffic_item.EndpointSet.add(Sources=topology1, Destinations=topology2)
#Configure traffic properties
traffic_config = traffic_item.ConfigElement.find()
traffic_config.FrameRate.update(Type='percentLineRate', Rate='50')
traffic_config.TransmissionControl.update(Type='continuous')
traffic_item.Tracking.find()[0].TrackBy = ['flowGroup0']
traffic_item.Generate()#Generates traffic item

time.sleep(20)
trafficItem = ixnetwork.Traffic.TrafficItem.find()
if trafficItem.Errors or trafficItem.Warnings:
    print("Errors in traffic item")
    print(trafficItem.Errors)
    print(trafficItem.Warnings)
    
traffic_item.Generate()

ixnetwork.Traffic.Apply()
ixnetwork.Traffic.StartStatelessTrafficBlocking()

time.sleep(10)

flowStatistics = session_assistant.StatViewAssistant('Flow Statistics')
ixnetwork.info('{}\n'.format(flowStatistics))
for rowNumber,flowStat in enumerate(flowStatistics.Rows):
    ixnetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))

ixnetwork.Traffic.StopStatelessTrafficBlocking()

#print(session_assistant.Session)
#port_map.Disconnect()
#session_assistant.Session.remove()
