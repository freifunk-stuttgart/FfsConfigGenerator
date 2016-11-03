allow-hotplug ffsbb
auto ffsbb
iface ffsbb inet static
    tinc-net ffsbb
    tinc-mlock yes
    tinc-pidfile /var/run/tinc.ffsbb.pid
    up ip l set dev $$IFACE up
    address 10.191.255.${idv4}/24    # Z.B. 10.191.255.10
    netmask 255.255.255.0
    broadcast 10.191.255.255
    post-up         /sbin/ip rule add iif $$IFACE table stuttgart priority 7000 || true
    pre-down        /sbin/ip rule del iif $$IFACE table stuttgart priority 7000 || true
    post-up         /sbin/ip r a 10.191.255.0/24 table stuttgart dev ffsbb ||true 
    pre-down        /sbin/ip r d 10.191.255.0/24 table stuttgart dev ffsbb ||true 
    post-up         /sbin/ip r a fd21:b4dc:4b00::/64 table stuttgart dev ffsbb ||true 
    pre-down        /sbin/ip r d fd21:b4dc:4b00::/64 table stuttgart dev ffsbb ||true 
    post-up         /usr/sbin/service isc-dhcp-relay restart || true
    pre-down        /usr/sbin/service isc-dhcp-relay stop || true
    #might also be the update server:
    post-up         /sbin/ip address add fd21:b4dc:4b00::a38:${idv6}/64 dev ffsbb || true
    pre-down        /sbin/ip address del fd21:b4dc:4b00::a38:${idv6}/64 dev ffsbb || true
