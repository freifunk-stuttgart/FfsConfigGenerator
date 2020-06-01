#!/usr/bin/python
from string import Template
from netaddr import *
import argparse
import os
import json

ffrlEndpoints = {}

ffrlEndpoints["bb-a-ak-ber"] =  "185.66.195.0"
ffrlEndpoints["bb-b-ak-ber"] = "185.66.195.1"
ffrlEndpoints["bb-a-ix-dus"] = "185.66.193.0"
ffrlEndpoints["bb-b-ix-dus"] = "185.66.193.1"
ffrlEndpoints["bb-a-fra2-fra"] = "185.66.194.0"
ffrlEndpoints["bb-b-fra2-fra"] = "185.66.194.1"


def getGwList(config):
    result = []
    for gw in config["gws"].keys():
        s = gw.split(",")
        result.append("gw%02dn%02d"%(int(s[0]),int(s[1])))
    return result

def genBirdBgpMain(gw,instance,config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    natv4 = config['gws']["%i,%i"%(gw,instance)]["ffrl_ipv4"]
    with open("bird_bgp_main.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    return tmpl.substitute(NAT_V4=natv4)

def genBirdBgpPeers(gw,instance,config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    with open("bird_bgp_peers.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        #i = interfaces[interface]
        
        data += tmpl.substitute(IFACE=ep.replace("-","_"),
                                TUN_LOCAL_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])+1),
                                TUN_REMOTE_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])))
    
    return data

def genCollectd(gw,instance,config):
    with open("collectd.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    hostname = "gw%02in%02i"%(gw,instance)
    data = tmpl.substitute(HOSTNAME=hostname)
    md("etc/collectd")
    with open("etc/collectd/collectd.conf","w") as fp:
        fp.write(data)
    
def genFfrl(gw, instance,config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return
    with open("ffrl.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        #i = interfaces[ep]
        localv4 = config['gws']["%i,%i"%(gw,instance)]["externalipv4"]
        natv4 = config['gws']["%i,%i"%(gw,instance)]["ffrl_ipv4"]
        data += tmpl.substitute(IFACE=ep,
                                TUN_LOCAL_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])+1),
                                TUN_REMOTE_V4=config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep],
                                TUN_LOCAL_V6=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv6"][ep])+1),
                                GRE_REMOTE=ffrlEndpoints[ep],
                                GRE_LOCAL=localv4,
                                NAT_V4=natv4)
    
    with open("etc/network/interfaces.d/ffrl","w") as fp:
        fp.write(data)

def gen_ffsbb(gw, instance, config):
    with open("tinc.conf.tpl","r") as fp:
        tmpl = Template(fp.read())

    md("etc/tinc")
    md("etc/tinc/ffsbb")
    inst = tmpl.substitute(interface="eth0",gw="gw%02dn%02d"%(gw,instance))
    with open("etc/tinc/ffsbb/tinc.conf","w") as fp:
        fp.write(inst)
    
    with open("network-ffsbb.tpl","r") as fp:
        tmpl = Template(fp.read())
    
    md("etc/network")
    md("etc/network/interfaces.d")

    if instance == 0:
        idv4 = gw
    else:
        idv4 = gw*10+instance
    idv6 = instance+gw*100 
    
    inst = tmpl.substitute(idv4=idv4,idv6=idv6)
    with open("etc/network/interfaces.d/ffsbb","w") as fp:
        fp.write(inst)

def genNetwork(segments, gw, config, nobridge):
    if nobridge == True:
        templatefile="ffs-gw-no-bridge.tpl"
    else:
        templatefile="ffs-gw.tpl"
    with open(templatefile,"r") as fp:
        tmpl = Template(fp.read())
    md("etc/network")
    md("etc/network/interfaces.d")
    for seg in segments:
        if seg == "00":
            continue
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4netmask=ip.netmask
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
        inst = tmpl.substitute(gw="%02i"%(gw),seg=seg,ipv4=ipv4,ipv4net=ip,ipv4netmask=ipv4netmask,ipv6=ipv6,ipv6net=ipv6net,instance="%02i"%(instance))
        with open("etc/network/interfaces.d/ffs-seg%s"%(seg), "w") as fp:
            fp.write(inst)
        #ip = IPNetwork(str(ip.broadcast+1)+"/18")


def genRadvd(segments, gw,config):
    with open("radvd.conf.tpl") as fp:
        tpl = Template(fp.read())
    fp = open("etc/radvd.conf","w")
    data = ""
    segments_sorted = sorted(segments)
    for seg in segments_sorted:
        if seg == "00":
            continue
        netroutes = "    route fd21:b4dc:4b00::/40 { };"
        ipv6net = IPNetwork(config["segments"][seg]["ipv6network"])
        if instance == 0:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw))
        else:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw*100+instance))

        inst = tpl.substitute(gw="%02i"%(gw),seg=seg,ipv6=ipv6,ipv6net=ipv6net,netroutes=netroutes)
        data += inst
        data +="\n"

    with open("etc/radvd.conf","w") as fp:
        fp.write(data)

def genBindOptions(segments,gw,config):
    with open("named.conf.options.tpl","r") as fp:
        tpl = Template(fp.read())

    md("etc/bind")
    ipv4ips = ""
    ipv6ips = ""
    if "legacyipv4" in config["gws"]["%s,%s"%(gw,instance)]:
        ipv4ips = "%s; "%(config["gws"]["%s,%s"%(gw,instance)]["legacyipv4"])
    if "legacyipv6" in config["gws"]["%s,%s"%(gw,instance)]:
        ipv6ips = "%s; "%(config["gws"]["%s,%s"%(gw,instance)]["legacyipv6"])
    for seg in segments:
        if seg == "00":
            continue
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4gw = str(ip.network+gw)
        ipv4ips += "%s; "%(ipv4gw)
        ipv6ips += "fd21:b4dc:4b%s::a38:%s; "%(seg,gw)
    inst = tpl.substitute(ipv4addr=ipv4ips,ipv6addr=ipv6ips)
    with open("etc/bind/named.conf.options","w") as fp:
        fp.write(inst)

def genBindLocal(segments,gw,config):
    with open("named.conf.local.tpl","r") as fp:
        tpl = Template(fp.read())

    ipv4net = ""
    ipv6net = ""
    for seg in segments:
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv6 = IPNetwork(config["segments"][seg]["ipv6network"])
        ipv4net += "    %s;\n"%(str(ip))
        ipv6net += "    %s;\n"%(str(ipv6))
    inst = tpl.substitute(ipv4net=ipv4net,ipv6net=ipv6net)
    with open("etc/bind/named.conf.local","w") as fp:
        fp.write(inst)

def genFastdConfig(segments,gw,config):
    with open("fastd.conf.tpl","r") as fp:
        tpl = Template(fp.read())

    externalipv4 = None
    externalipv6 = None
    if "externalipv4" in config["gws"]["%s,%s"%(gw,instance)]:
        externalipv4 = config["gws"]["%s,%s"%(gw,instance)]["externalipv4"]
    if "externalipv6" in config["gws"]["%s,%s"%(gw,instance)]:
        externalipv6 = config["gws"]["%s,%s"%(gw,instance)]["externalipv6"]

    if not os.path.exists("etc/fastd"):
        os.mkdir("etc/fastd")

    for conf in (("vpn",10200,1340,"peers"),("bb",9040,1340,"bb")):
        (scope,portBase,mtu,group) = conf
        for seg in segments: #alternative MTU
            if seg == "00":
                if scope=="vpn":
                    port = portBase-3
                else:
                    continue
            else:
                port = int(seg)+portBase 
            bindv4 = ""
            if not externalipv4 == None:
                bindv4 = "bind 0.0.0.0:%i;"%(port)
            bindv6 = ""
            if not externalipv6 == None:
                bindv6 = "bind [::]:%i;"%(port)
            inst = tpl.substitute(seg=seg,bindv4=bindv4,bindv6=bindv6,group=group,scope=scope,mtu=mtu)
            if not os.path.exists("etc/fastd/%s%s"%(scope,seg)):
                os.mkdir("etc/fastd/%s%s"%(scope,seg))
            with open("etc/fastd/%s%s/fastd.conf"%(scope,seg),"w") as fp:
                fp.write(inst)
    
def genBirdConfig(segments,gw,instance,config):

    if instance == 0:
        router_id = "10.191.255.%s"%(gw)
    else:
        router_id = "10.191.255.%s"%((gw*10)+instance)

    with open("bird.conf.tpl","r") as fp:
        tlp = Template(fp.read())
    data = ""
    md("etc/bird")

    inst = tlp.substitute(router_id=router_id)
    data += inst
    data += genBirdBgpMain(gw,instance,config)
    data += genBirdBgpPeers(gw,instance,config)
    
    dataFfrl = genBirdBgpMain(gw,instance,config)
    dataFfrl+=genBirdBgpPeers(gw,instance,config)
    
    with open("etc/bird/ffrl.conf","w") as fp:
        fp.write(dataFfrl)
    
    with open("etc/bird/bird.conf","w") as fp:
        fp.write(data)

    with open("bird6.conf.tpl","r") as fp:
        tlp = Template(fp.read())
    
    inst = tlp.substitute(router_id=router_id)

    with open("etc/bird/bird6.conf","w") as fp:
        fp.write(inst)

def md(d):
    if not os.path.exists(d):
        os.mkdir(d)

parser = argparse.ArgumentParser(description='Generate Configuration for Freifunk Gateway')
parser.add_argument('--gwnum', dest='GWNUM', action='store', required=True,help='Config will be generated for this gateway')
parser.add_argument('--instance', dest='INSTANCE', action='store', required=True,help='Config will be generated for this instance of a gateway')
parser.add_argument('--no-bridge', dest='NOBRIDGE', action='store_true', required=False,help='Create network without bridges, direct batman only')
args = parser.parse_args()


gw=int(args.GWNUM)
instance=int(args.INSTANCE)
md("etc")
with open("config.json","r") as fp:
    config = json.load(fp)

segments = config["segments"].keys()
gen_ffsbb(gw,instance,config)
genNetwork(segments,gw,config,args.NOBRIDGE)
genRadvd(segments,gw,config)
genBindOptions(segments,gw,config)
genBindLocal(segments,gw,config)
genFastdConfig(segments,gw,config)
genBirdConfig(segments,gw,instance,config)
genFfrl(gw,instance,config)
genBirdBgpPeers(gw,instance,config)
genCollectd(gw,instance,config)
