#!/usr/bin/env python
from string import Template
from netaddr import *
import argparse
import os
import json


def md(d):
    if not os.path.exists(d):
        os.mkdir(d)


def genDhcp(segments, dhcp, config):
    with open("dhcpd.conf.tpl") as fp:
        tpl = Template(fp.read())
    with open("dhcpd.conf.head") as fp:
        data = fp.read()

    md("etc")
    md("etc/dhcp")
    segments = list(segments)
    segments.sort()
    for seg in segments:
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4net = str(ip.network)
        dhcp_prefixlen = ip.prefixlen + 2

        ipv4gw = str(ip.network + 1)
        netmask = ip.netmask
        dhcp_ipnet = list(ip.subnet(dhcp_prefixlen))[dhcp]

        ipv4start = str(IPAddress(dhcp_ipnet.first))
        ipv4end = str(IPAddress(dhcp_ipnet.last - 1))

        inst = tpl.substitute(segment=seg, ipv4start=ipv4start, ipv4end=ipv4end, ipv4net=ipv4net, ipv4gw=ipv4gw,
                              netmask=netmask)

        data += inst

    with open("etc/dhcp/dhcpd.conf", "w") as fp:
        fp.write(data)


parser = argparse.ArgumentParser(description='Generate Configuration for Freifunk DHCP Server')
parser.add_argument('--dhcp', dest='DHCP', action='store', required=True,
                    help='Config will be generated for this gateway')
args = parser.parse_args()

dhcp = int(args.DHCP)

with open("config.json", "r") as fp:
    config = json.load(fp)
segments = config["segments"].keys()

genDhcp(segments, dhcp, config)
