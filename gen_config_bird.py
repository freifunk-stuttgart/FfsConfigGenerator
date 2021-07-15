from string import Template
import collections
from netaddr import *

from gen_config_utils import *

ffrlEndpoints = collections.OrderedDict()

ffrlEndpoints["bb-b-fra2-fra"] = "185.66.194.1"
ffrlEndpoints["bb-b-ak-ber"] = "185.66.195.1"
ffrlEndpoints["bb-a-ix-dus"] = "185.66.193.0"
ffrlEndpoints["bb-a-fra2-fra"] = "185.66.194.0"
ffrlEndpoints["bb-b-ix-dus"] = "185.66.193.1"
ffrlEndpoints["bb-a-ak-ber"] =  "185.66.195.0"

def genBirdFfrlMain(gw, instance, config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    natv4 = config['gws']["%i,%i"%(gw,instance)]["ffrl_ipv4"]
    with open("bird_ffrl_main.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    return tmpl.substitute(NAT_V4=natv4)

def genBirdFfrlPeers(gw, instance, config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    with open("bird_ffrl_peers.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        data += tmpl.substitute(IFACE=ep.replace("-","_"),
                                TUN_LOCAL_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])+1),
                                TUN_REMOTE_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])))

    return data

def genBird6FfrlMain(gw, instance, config):
    if not "ffrlv6" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    #natv4 = config['gws']["%i,%i"%(gw,instance)]["ffrl_ipv4"]
    with open("bird6_ffrl_main.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    return tmpl.substitute()

def genBird6FfrlPeers(gw, instance, config):
    if not "ffrlv6" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    with open("bird6_ffrl_peers.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        data += tmpl.substitute(IFACE=ep.replace("-","_"),
                                TUN_LOCAL_V6=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv6"][ep])+1),
                                TUN_REMOTE_V6=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv6"][ep])))

    return data


def genBirdConfig(segments,gw,instance,config):
    if instance == 0:
        router_id = "10.191.255.%s"%(gw)
    else:
        router_id = "10.191.255.%s"%((gw*10)+instance)

    md("etc/bird")

    #generate bird.conf
    with open("bird.conf.tpl","r") as fp:
        tlp = Template(fp.read())
    data = tlp.substitute(router_id=router_id)
    with open("etc/bird/bird.conf","w") as fp:
        fp.write(data)

    #generate bird_ffrl.conf
    dataFfrl = genBirdFfrlMain(gw, instance, config)
    dataFfrl+=genBirdFfrlPeers(gw, instance, config)
    with open("etc/bird/bird_ffrl.conf","w") as fp:
        fp.write(dataFfrl)

    #generate bird6.conf
    with open("bird6.conf.tpl","r") as fp:
        tlp = Template(fp.read())
    inst = tlp.substitute(router_id=router_id)
    with open("etc/bird/bird6.conf","w") as fp:
        fp.write(inst)

    #generate bird6_ffrl.conf
    dataFfrl = genBird6FfrlMain(gw, instance, config)
    dataFfrl+=genBird6FfrlPeers(gw, instance, config)
    with open("etc/bird/bird6_ffrl.conf","w") as fp:
        fp.write(dataFfrl)
