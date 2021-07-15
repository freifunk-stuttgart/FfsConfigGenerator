from string import Template
import os

def genFastdConfig(segments,gw,config,instance):
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
