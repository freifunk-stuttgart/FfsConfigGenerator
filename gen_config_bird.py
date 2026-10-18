from string import Template

from netaddr import IPAddress

from gen_config_utils import *


def genBirdFfrlMain(gw, instance, config):
    if not "ffrlv6" in config['gws']["%i,%i" % (gw, instance)]:
        return ""
    natv4 = config['gws']["%i,%i"%(gw,instance)]["ffrl_ipv4"]
    with open("bird_ffrl_main.conf.tpl", "r") as fp:
        tmpl = Template(fp.read())
    return tmpl.substitute(NAT_V4=natv4, IPV6NETWORK=config['gws']["%i,%i" % (gw, instance)]['ipv6network'],
                           IPV6SERVICENETWORK=config['gws']["%i,%i" % (gw, instance)]['ipv6servicenetwork'])

def genBirdFfrlPeers(gw, instance, config):
    if not "ffrlv6" in config['gws']["%i,%i"%(gw,instance)]:
        return ""
    with open("bird_ffrl_peers.conf.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        data += tmpl.substitute(IFACE=ep.replace("-","_"),
                                TUN_LOCAL_V6=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv6"][ep])+1),
                                TUN_REMOTE_V6=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv6"][ep])),
                                TUN_LOCAL_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])+1),
                                TUN_REMOTE_V4=str(IPAddress(config['gws']["%i,%i"%(gw,instance)]["ffrlv4"][ep])))
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


