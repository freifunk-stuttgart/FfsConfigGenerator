from string import Template
from netaddr import *

def genRadvd(segments, gw,config,instance):
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
