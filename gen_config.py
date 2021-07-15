#!/usr/bin/env python3

import argparse
import json


from gen_config_bird import *
from gen_config_utils import *
from gen_config_fastd import *
from gen_config_radvd import *

def getGwList(config):
    result = []
    for gw in config["gws"].keys():
        s = gw.split(",")
        result.append("gw%02dn%02d"%(int(s[0]),int(s[1])))
    return result


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

def genNetwork(segments, gw, config, nobridge):
    if nobridge == True:
        templatefile="ffs-gw-no-bridge.tpl"
    else:
        templatefile="ffs-gw.tpl"
    with open(templatefile,"r") as fp:
        tmpl = Template(fp.read())
    md("etc/network")
    md("etc/network/interfaces.d")
    publicipv6pool = IPNetwork(config["gws"]["%i,%i"%(gw,instance)]["ipv6network"])
    publicipv6pool.prefixlen = 64
    publicipv6servicepool = IPNetwork(config["gws"]["%i,%i"%(gw,instance)]["ipv6servicenetwork"])
    publicipv6servicepool.prefixlen = 64
    for seg in segments:
        if seg == "00":
            continue
        ip = IPNetwork(config["segments"][seg]["ipv4network"])
        ipv4netmask=ip.netmask
        ipv6net = IPNetwork(config["segments"][seg]["ipv6network"])
        seghex = "%02x"%int(seg, 10)


        publicipv6net = publicipv6pool.next(int(seg,10))
        publicipv6servicenet = publicipv6servicepool.next(int(seg,10))
        if instance == 0:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw))
            publicipv6 = publicipv6pool.ip+IPAddress("::00%s:0:0:0:%i"%(seghex,gw))
        else:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw*100+instance))
            publicipv6 = publicipv6pool.ip+IPAddress("::00%s:0:0:0:%i"%(seghex,gw*10+instance))
        if seg == "00":
            ipv4 = config["gws"]["%s"%(gw)]["legacyipv4"]
        else:
            if instance == 0:
                ipv4 = str(ip.network+gw)
            else:
                ipv4 = str(ip.network+gw*10+instance)
        inst = tmpl.substitute(gw="%02i"%(gw),seg=seg,ipv4=ipv4,ipv4net=ip,ipv4netmask=ipv4netmask,ipv6=ipv6,ipv6net=ipv6net,publicipv6=publicipv6,publicipv6net=publicipv6net,publicipv6servicenet=publicipv6servicenet,instance="%02i"%(instance))
        with open("etc/network/interfaces.d/ffs-seg%s"%(seg), "w") as fp:
            fp.write(inst)
        #ip = IPNetwork(str(ip.broadcast+1)+"/18")


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



def genbb(segments,gw,instance,config):
    for s in segments:
        md("peers-ffs/vpn%s"%(s))
        md("peers-ffs/vpn%s/bb"%(s))
        fn = "peers-ffs/vpn%s/bb/gw%02dn%02ds%s"%(s,gw,instance,s)
        hostname = "gw%02dn%02d"%(gw,instance)
        port = 9040+int(s)
        mac = "02:00:35:%s:%02d:%02d"%(s,gw,instance)
        key = config["gws"][gwn]["fastd_bb_pubkey"]
        conf = """#MAC: %s
key "%s";
remote "%s.gw.freifunk-stuttgart.de" port %d;
"""%(mac,key,hostname,port)
        
        with open(fn,"w") as fp:
            fp.write(conf)        


def genDhcrelayUnit(segments,gw,instance,config):
    
    sample = "-id br01 -id br02 -id br03 -id br04 -id br05 -id br06 -id br07 -id br08 -id br09 -id br10 -id br11 -id br12 -id br13 -id br14 -id br15 -id br16 -id br17 -id br18 -id br19 -id br20 -id br21 -id br22 -id br23 -id br24"
    downstreamInterfaces = ""
    for s in config["gws"]["%i,%i"%(gw,instance)]["segments"]:
        downstreamInterfaces +="-id br%02d"%(s)
    
    content = """[Unit]
Description=isc-dhcp-relay
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/dhcrelay -d -q -a -iu ffsbb -iu ffsl3 %s 10.191.255.251 10.191.255.252 10.191.255.253
Restart=always

[Install]
WantedBy=multi-user.target
"""%(downstreamInterfaces)
    md("etc/systemd")    
    md("etc/systemd/system")
    with open("etc/systemd/system/isc-dhcp-relay.service","w") as fp:
        fp.write(content)


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

#segments = config["segments"].keys()
gwn = ("%i,%i"%(gw,instance))
segments = []
for s in config["gws"][gwn]["segments"]:
    segments.append("%02d"%(s))
#segments = config["gws"][gwn]["segments"]
genbb(segments,gw,instance,config)
genDhcrelayUnit(segments,gw,instance,config)
genNetwork(segments,gw,config,args.NOBRIDGE)
genRadvd(segments,gw,config,instance)
genBindOptions(segments,gw,config)
genBindLocal(segments,gw,config)
genFastdConfig(segments,gw,config,instance)
genBirdConfig(segments,gw,instance,config)
genFfrl(gw,instance,config)
genBirdFfrlPeers(gw, instance, config)
genCollectd(gw,instance,config)
print("Success")
