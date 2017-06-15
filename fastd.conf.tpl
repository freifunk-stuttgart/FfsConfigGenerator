log to syslog level warn;
interface "vpn${seg}${segext}${mtu_hack}";
method "salsa2012+gmac";    # new method, between gateways for the moment (faster)
method "salsa2012+umac";  
# Bind von v4 and v6 interfaces
${bindv4}
${bindv6}

include "../secret_vpn${segext}.conf";
mtu ${mtu}; # maxmtu - IPv4/IPv6 Header - fastd Header = ${mtu}
on verify "/root/freifunk/unclaimed.py";
status socket "/var/run/fastd-vpn${seg}${segext}${mtu_hack}.sock";

peer group "${group}" {
    include peers from "/etc/fastd/peers-ffs/vpn${seg}/${group}";
}
