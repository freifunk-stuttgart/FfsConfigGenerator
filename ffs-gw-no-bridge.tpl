allow-hotplug bat${seg}
iface bat${seg} inet static
    hwaddress 02:00:39:${seg}:${gw}:${instance}
    address ${ipv4}
    netmask ${ipv4netmask}
    # be sure all incoming traffic is handled by the appropriate rt_table
    post-up         /sbin/ip rule add iif $$IFACE table stuttgart priority 10000 || true
    pre-down        /sbin/ip rule del iif $$IFACE table stuttgart priority 10000 || true
    post-up         /sbin/ip rule add iif $$IFACE table nodefault priority 10010 || true
    pre-down        /sbin/ip rule del iif $$IFACE table nodefault priority 10010 || true
    post-up         /sbin/ip route add ${ipv4net} table stuttgart dev $$IFACE || true
    post-down       /sbin/ip route del ${ipv4net} table stuttgart dev $$IFACE || true
    # default route is unreachable
    post-up         /sbin/ip route add unreachable default table nodefault || true
    pre-up          /sbin/modprobe batman-adv || true
    post-up         /sbin/ip link set dev $$IFACE up || true
    post-up         /sbin/ip link set dev $$IFACE address 02:00:39:${seg}:${gw}:${instance} || true
    post-up         /usr/sbin/batctl -m $$IFACE it 10000 || true
    post-up         /usr/sbin/batctl -m $$IFACE vm server || true
    post-up         /usr/sbin/batctl -m $$IFACE gw server  96mbit/96mbit || true
    post-up         echo 60 > /sys/devices/virtual/net/$$IFACE/mesh/hop_penalty || true

iface bat${seg} inet6 static
    address ${ipv6}
    netmask 64
    # ULA route for rt_table stuttgart
    post-up         /sbin/ip -6 route add ${ipv6net} proto static dev $$IFACE table stuttgart || true
    post-down       /sbin/ip -6 route del ${ipv6net} proto static dev $$IFACE table stuttgart || true

allow-hotplug vpn${seg}
iface vpn${seg} inet6 manual
    hwaddress 02:00:38:${seg}:${gw}:${instance}
    pre-up          /sbin/modprobe batman_adv || true
    pre-up          /sbin/ip link set dev $$IFACE address 02:00:38:${seg}:${gw}:${instance} || true
    post-up         /sbin/ip link set dev $$IFACE up || true
    post-up         /usr/sbin/batctl -m bat${seg} if add $$IFACE || true


allow-hotplug vpn${seg}bb
iface vpn${seg}bb inet6 manual
    hwaddress 02:00:35:${seg}:${gw}:${instance}
    pre-up          /sbin/modprobe batman_adv || true
    pre-up          /sbin/ip link set dev $$IFACE address 02:00:35:${seg}:${gw}:${instance} || true
    post-up         /sbin/ip link set dev $$IFACE up || true
    post-up         /usr/sbin/batctl -m bat${seg} if add $$IFACE || true
