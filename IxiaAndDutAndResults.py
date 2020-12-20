#!/usr/bin/python
# -*- coding: utf-8 -*-
#For python3: pip install jsonrpclib-pelix
#For python2: pip install jsonrpclib
from jsonrpclib import Server
from pprint import pprint
import jinja2
import os
import netaddr
import json

def report(op):
    op = op
    TEMPLATE = """{{ showversion2 }}
    <html>
        <head>
            <meta charset="utf-8">
                <style>
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        font-size: 13px;
        line-height: 19px;
        overflow: auto;
        padding: 6px 10px;
        border-radius: 3px;
    }
    code {
        white-space: pre;
    }
                </style>
        </head>

        <body>
            {% if h1 %}
            <h1>{{ h1 }}</h1>
            {% endif %}

            {% for x in op %}
            <pre>
            <code>
{{ x }}
            </code>
            </pre>
            {% endfor %}
        </body>
    </html>
    """


    j2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    template = j2_env.from_string(TEMPLATE)

    with open("showversion.html", 'w') as fh:
        htmlContent = template.render(op = op)
        #print(htmlContent)
        fh.write(htmlContent)

def configureIxia():
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
    #assert(ipv4.Address.Pattern.startswith('Inc:') is True)         # this is an example that assert statements can be used too.
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
    return ixnetwork

def startIxiaTraffic(ixnetwork):
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

    TrafficItemStatistics = session_assistant.StatViewAssistant('Traffic Item Statistics')
    FlowStatistics = session_assistant.StatViewAssistant('Flow Statistics')

    return TrafficItemStatistics, FlowStatistics
    #print(session_assistant.Session)
    #port_map.Disconnect()
    #session_assistant.Session.remove()

def main():
    ixnetwork = configureIxia()
    op = []
    switch = Server("http://admin:@nfc302/command-api")

    resp = switch.runCmds(1,["show version"],"text")
    op.append("nfc302: " + resp[0]['output'])

    #Configure switch
    commands = [
    "configure",
    "interface Ethernet3/41/1",
    "ip address 1.0.0.1/24",
    "interface Ethernet3/42/1",
    "ip address 2.0.0.1/24",
    "router bgp 65514",
    "neighbor ixia-v4 peer group",
    "neighbor ixia-v4 remote-as 101",
    "neighbor ixia-v4 maximum-routes 0",
    "neighbor 1.0.0.2 peer group ixia-v4",
    "neighbor 1.0.0.3 peer group ixia-v4",
    "neighbor 1.0.0.4 peer group ixia-v4",
    "neighbor 1.0.0.5 peer group ixia-v4",
    ]
    resp = switch.runCmds(1,commands,"text")
    op.append("nfc302: \n" + resp[0]['output'])

    time.sleep(10)

    resp = switch.runCmds(1,["show ip bgp summary | grep Estab"],"text")
    op.append("nfc302: " + resp[0]['output'])
    assert "1.0.0.2" in resp[0]['output']

    resp = switch.runCmds(1,["show ip bgp"],"text")
    op.append("nfc302: " + resp[0]['output'])

    TrafficItemStatistics, FlowStatistics = startIxiaTraffic(ixnetwork)

    op.append(TrafficItemStatistics)
    op.append(FlowStatistics)

    #pprint(op)
    report(op)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
