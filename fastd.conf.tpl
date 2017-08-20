log to syslog level warn;
interface "${scope}${seg}";
method "salsa2012+gmac";    # new method, between gateways for the moment (faster)
method "salsa2012+umac";  
method "null+salsa2012+umac";

# Bind von v4 and v6 interfaces
${bindv4}
${bindv6}

include "../secret_${group}.conf";
mtu ${mtu}; # maxmtu - IPv4/IPv6 Header - fastd Header = ${mtu}
#on verify "/root/freifunk/unclaimed.py";
status socket "/var/run/fastd-${scope}${seg}.sock";

include peers from "/etc/fastd/peers-ffs/vpn${seg}/${group}";
