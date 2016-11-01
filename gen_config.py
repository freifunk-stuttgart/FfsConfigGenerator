#!/usr/bin/python
from string import Template
from netaddr import *
import argparse
import os
import json

def genTinc(gw, instance, config):
    fp = open("tinc.conf.tpl","rb")
    tmpl = Template(fp.read())
    fp.close()
    md("etc/tinc")
    md("etc/tinc/ffsbb")
    gws = ["gw01n00","gw01n01","gw05n01","gw05n02","gw05n03","gw05n04","gw08n00","gw08n01","gw08n02","gw08n03","gw08n04","gw09"]
    connects = ""
    for g in gws:
        connects += "ConnectTo = %s\n"%(g)
    inst = tmpl.substitute(interface="eth0",connects=connects,gw="gw%02dn%02d"%(gw,instance))
    fp = open("etc/tinc/ffsbb/tinc.conf","wb")
    fp.write(inst)
    fp.close()




def genNetwork(segments, gw,config):
    fp = open("ffs-gw.tpl","rb")
    tmpl = Template(fp.read())
    fp.close()
    md("etc/network")
    md("etc/network/interfaces.d")
    for seg in segments:
        if seg == "00":
            continue
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv6net = IPNetwork(config["segments"][seg]["ipv6network"])
        if instance == 0:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw))
        else:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw*100+instance))
        if seg == "00":
            ipv4 = config["gws"]["%s"%(gw)]["legacyipv4"]
        else:
            if instance == 0:
		ipv4 = str(ip.network+gw)
            else:
		ipv4 = str(ip.network+gw*10+instance)
        inst = tmpl.substitute(gw="%02i"%(gw),seg=seg,ipv4=ipv4,ipv4net=ip,ipv6=ipv6,ipv6net=ipv6net,instance="%02i"%(instance))
        fp = open("etc/network/interfaces.d/ffs-seg%s"%(seg), "wb")
        fp.write(inst)
        fp.close()
        ip = IPNetwork(str(ip.broadcast+1)+"/18")


def genRadvd(segments, gw,config):
    fp = open("radvd.conf.tpl")
    tpl = Template(fp.read())
    fp.close()
    fp = open("etc/radvd.conf","wb")
    hostroutes = "    route fd21:b4dc:4b00::/64\n    {\n    };\n"
    for seg in segments:
        netroutes = ""
        for netroute in segments:
            if netroute != seg:
                ipv6net = IPNetwork(config["segments"][netroute]["ipv6network"])
                netroutes += "    route %s\n    {\n    };\n\n"%(ipv6net) 
        ipv6net = IPNetwork(config["segments"][seg]["ipv6network"])
        if instance == 0:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw))
        else:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw*100+instance))

        inst = tpl.substitute(gw="%02i"%(gw),seg=seg,ipv6=ipv6,ipv6net=ipv6net,hostroutes=hostroutes,netroutes=netroutes)
        fp.write(inst)
    fp.close()

def genDhcp(segments, gw,config):
    fp = open("dhcpd.conf.tpl")
    tpl = Template(fp.read())
    fp.close()
    fp = open("dhcpd.conf.head")
    head = fp.read()
    fp.close()
    md("etc/dhcp")

    fp = open("etc/dhcp/dhcpd.conf","wb")
    fp.write(head)

    for seg in segments:
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4net = str(ip.network)
        if seg == "00":
            ipv4gw = config["gws"]["%s"%(gw)]["legacyipv4"]
            ipv4start = config["gws"]["%s"%(gw)]["ipv4start"]
            ipv4end = config["gws"]["%s"%(gw)]["ipv4end"]
        else:
            ipv4gw = str(ip.network+gw)

            dhcp_ipnet = IPNetwork("%s/21"%(ip.network))
            for  i in range(1,gw):
                dhcp_ipnet = dhcp_ipnet.next()
        
            ipv4start = str(dhcp_ipnet.network+257)
            ipv4end = str(dhcp_ipnet.broadcast-1)
        
        inst = tpl.substitute(ipv4start=ipv4start,ipv4end=ipv4end,ipv4net=ipv4net,ipv4gw=ipv4gw)
        fp.write(inst)
        ip = ip.next()
    fp.close()

def genBindOptions(segments,gw,config):
    fp = open("named.conf.options.tpl","rb")
    tpl = Template(fp.read())
    fp.close()
    md("etc/bind")
    fp = open("etc/bind/named.conf.options","wb")
    ipv4ips = "%s; "%(config["gws"]["%s"%(gw)]["instance"]["%s"%(instance)]["legacyipv4"])
    ipv6ips = "%s; "%(config["gws"]["%s"%(gw)]["instance"]["%s"%(instance)]["legacyipv6"])
    for seg in segments:
        if seg == "00":
            continue
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4gw = str(ip.network+gw)
        ipv4ips += "%s; "%(ipv4gw)
        ipv6ips += "fd21:b4dc:4b%s::a38:%s; "%(seg,gw)
    inst = tpl.substitute(ipv4addr=ipv4ips,ipv6addr=ipv6ips)
    fp.write(inst)
    fp.close()

def genBindLocal(segments,gw,config):
    fp = open("named.conf.local.tpl","rb")
    tpl = Template(fp.read())
    fp.close()
    fp = open("etc/bind/named.conf.local","wb")
    ipv4net = ""
    ipv6net = ""
    for seg in segments:
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv6 = IPNetwork(config["segments"][seg]["ipv6network"])
        ipv4net += "    %s;\n"%(str(ip))
        ipv6net += "    %s;\n"%(str(ipv6))
    inst = tpl.substitute(ipv4net=ipv4net,ipv6net=ipv6net)
    fp.write(inst)
    fp.close()

def genFastdConfig(segments,gw,config):
    fp = open("fastd.conf.tpl","rb")
    tpl = Template(fp.read())
    fp.close()
    externalipv4 = config["gws"]["%s"%(gw)]["instance"]["%s"%(instance)]["externalipv4"]
    externalipv6 = config["gws"]["%s"%(gw)]["instance"]["%s"%(instance)]["externalipv6"]

    if not os.path.exists("etc/fastd"):
        os.mkdir("etc/fastd")
    for seg in segments:
        if seg == "00":
            port = 10037
        else:
            port = int(seg)+10040
        inst = tpl.substitute(port=port,seg=seg,externalipv4=externalipv4,externalipv6=externalipv6)
        if not os.path.exists("etc/fastd/vpn%s"%(seg)):
            os.mkdir("etc/fastd/vpn%s"%(seg))
        fp=open("etc/fastd/vpn%s/fastd.conf"%(seg),"wb")
        fp.write(inst)
        fp.close()

def genBirdConfig(segments,gw,config):
    fp = open("bird.conf.tpl","rb")
    tlp = Template(fp.read())
    fp.close()
    router_id = "10.191.255.%s"%(gw+(instance*10))    
    if not os.path.exists("etc/bird"):
        os.mkdir("etc/bird")
    inst = tlp.substitute(router_id=router_id)
    fp = open("etc/bird/bird.conf","wb")
    fp.write(inst)

    fp.close()
    fp = open("bird6.conf.tpl","rb")
    tlp = Template(fp.read())
    fp.close()
    router_id = "10.191.255.%s"%(gw+(instance*10))    
    if not os.path.exists("etc/bird"):
        os.mkdir("etc/bird")
    inst = tlp.substitute(router_id=router_id)
    fp = open("etc/bird/bird6.conf","wb")
    fp.write(inst)
    fp.close()


    
def md(d):
    if not os.path.exists(d):
        os.mkdir(d)

parser = argparse.ArgumentParser(description='Generate Configuration for Freifunk Gateway')
parser.add_argument('--gwnum', dest='GWNUM', action='store', required=True,help='Config will be generated for this gateway')
parser.add_argument('--instance', dest='INSTANCE', action='store', required=True,help='Config will be generated for this instance of a gateway')
args = parser.parse_args()


segments = ["00", "01","02","03","04"]
gw=int(args.GWNUM)
instance=int(args.INSTANCE)
md("etc")
fp = open("config.json","rb")
config = json.load(fp)
fp.close()
genTinc(gw,instance,config)
genNetwork(segments,gw,config)
genRadvd(segments,gw,config)
#genDhcp(segments,gw,config)
genBindOptions(segments,gw,config)
genBindLocal(segments,gw,config)
genFastdConfig(segments,gw,config)
genBirdConfig(segments,gw,config)


