#!/usr/bin/env python3
from string import Template
from netaddr import *
import argparse
import os
import json

def md(d):
    if not os.path.exists(d):
        os.mkdir(d)


def genDhcp(segments, dhcp, config, flavour, output):
    with open(f"{flavour}.conf.tpl") as fp:
        segment_template = Template(fp.read())
    with open(f"{flavour}.pool.conf.tpl") as fp:
        pool_template = Template(fp.read())
    with open(f"{flavour}.conf.head") as fp:
        data = fp.read()

    segments = list(segments)
    segments.sort()
    for seg in segments:
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4net = str(ip.network)
        dhcp_prefixlen = ip.prefixlen + 2

        ipv4gw = str(ip.network + 1)
        netmask = ip.netmask
        prefixlen = ip.prefixlen
        dhcp_ipnet = list(ip.subnet(dhcp_prefixlen))[dhcp]

        ipv4start = str(IPAddress(dhcp_ipnet.first))
        ipv4end = str(IPAddress(dhcp_ipnet.last - 1))

        if seg in segments_with_pools:
            poolconfig = pool_template.substitute(ipv4start=ipv4start, ipv4end=ipv4end)
        else:
            poolconfig = ""

        inst = segment_template.substitute(segment=seg, ipv4net=ipv4net, ipv4gw=ipv4gw,
                              netmask=netmask, prefixlen=prefixlen, poolconfig=poolconfig)

        data += inst

    with open(f"{output}", "w") as fp:
        fp.write(data)


parser = argparse.ArgumentParser(description='Generate Configuration for Freifunk DHCP Server')
parser.add_argument('--dhcp', dest='DHCP', action='store', required=True,
                    help='Config will be generated for this DHCP-Server')

def two_digits_leading_zero(string):
    """
    Given a string, normalize it such that it always start with leading zero
    """
    number = int(string, 10)
    return "{:02d}".format(number)

parser.add_argument('--segment', dest='segments', action='append', required=False, type=two_digits_leading_zero, default=[], help='Only generate pools for these segments (default all, can be specified multiple times). Segments not given here will be generated, but will have an empty pool.')
args = parser.parse_args()

dhcp = int(args.DHCP)

with open("config.json", "r") as fp:
    config = json.load(fp)

segments = config["segments"].keys()
if len(args.segments) > 0:
    segments_with_pools = args.segments
else:
    segments_with_pools = config["segments"].keys()

md("etc")
md("etc/dhcp")
md("etc/kea")
genDhcp(segments, dhcp, config, "dhcpd", "etc/dhcp/dhcp.conf")
genDhcp(segments, dhcp, config, "kea", "etc/kea/subnet4.conf")
