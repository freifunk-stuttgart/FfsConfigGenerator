from string import Template
from gen_config_utils import *
from netaddr import IPAddress

def genFfrl(gw, instance,config):
    if not "ffrl_ipv4" in config['gws']["%i,%i"%(gw,instance)]:
        return
    with open("ffrl.tpl","r") as fp:
        tmpl = Template(fp.read())
    data = ""
    for ep in ffrlEndpoints:
        localv4 = config['gws']["%i,%i"%(gw,instance)]["internalipv4"]
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

