from string import Template
from netaddr import *


v6servicenet_template = """
    prefix ${service_net}
    {
        AdvValidLifetime 300;
        AdvPreferredLifetime 0;
    };"""

v6specific_template = """
    prefix ${specific_net}
    {
        AdvOnLink on;
        AdvAutonomous on;
        AdvRouterAddr on;
        AdvValidLifetime 7200;
        AdvPreferredLifetime 300;
    };"""

def genRadvd(segments, gw,config,instance):
    with open("radvd.conf.tpl") as fp:
        tpl = Template(fp.read())
    fp = open("etc/radvd.conf","w")
    data = ""
    no_defaultroute_template = """# don't advertise default router
    AdvDefaultLifetime 0;"""

    segments_sorted = sorted(segments)
    for seg in segments_sorted:
        if seg == "00":
            continue

        service_net_gw01n03 = "2a03:2260:3016:%02x::/64"%(int(seg))
        service_net_gw09n03 = "2a01:1e8:c003:%02x::/64"%(int(seg))
        specific_net = "2a03:2260:3016:13%02x::/64"%(int(seg))

        if int(seg) in config["gws"]["%i,%i"%(gw,instance)]["segments_v6"]:
            adv_default_lifetime=""
            v6prefixes = Template(v6servicenet_template).substitute(service_net=service_net_gw01n03)
            #v6prefixes += Template(v6servicenet_template).substitute(service_net=service_net_gw09n03)
            v6prefixes += Template(v6specific_template).substitute(specific_net=specific_net)
        else:
            adv_default_lifetime=no_defaultroute_template
            v6prefixes = ""


        netroutes = "    route fd21:b4dc:4b00::/40 { };"
        ipv6net = IPNetwork(config["segments"][seg]["ipv6network"])
        if instance == 0:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw))
        else:
            ipv6 = ipv6net.ip+IPAddress("::a38:%i"%(gw*100+instance))

        inst = tpl.substitute(gw="%02i"%(gw),seg=seg,ipv6=ipv6,ipv6net=ipv6net,netroutes=netroutes,AdvDefaultLifetime=adv_default_lifetime,v6prefixes=v6prefixes)
        data += inst
        data +="\n"

    with open("etc/radvd.conf","w") as fp:
        fp.write(data)
