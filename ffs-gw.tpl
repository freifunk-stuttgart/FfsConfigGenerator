auto br${seg}
iface br${seg} inet static
    hwaddress 02:00:0a:39:${seg}:${gw}
    address ${ipv4}
    netmask 255.255.192.0
    pre-up          /sbin/brctl addbr $$IFACE || true
    up              /sbin/ip address add ${ipv6}/64 dev $$IFACE || true
    post-down       /sbin/brctl delbr $$IFACE || true
    # be sure all incoming traffic is handled by the appropriate rt_table
    post-up         /sbin/ip rule add iif $$IFACE table stuttgart priority 5600 || true
    pre-down        /sbin/ip rule del iif $$IFACE table stuttgart priority 5600 || true
    post-up         /sbin/ip rule add iif $$IFACE table nodefault priority 5650 || true
    pre-down        /sbin/ip rule del iif $$IFACE table nodefault priority 5650 || true
    post-up         /sbin/ip route add ${ipv4net} table stuttgart dev $$IFACE || true
    post-down       /sbin/ip route del ${ipv4net} table stuttgart dev $$IFACE || true
    # default route is unreachable
    post-up         /sbin/ip route add unreachable default table nodefault || true
    # ULA route for rt_table stuttgart
    post-up         /sbin/ip -6 route add ${ipv6net} proto static dev $$IFACE table stuttgart || true
    post-down       /sbin/ip -6 route del ${ipv6net} proto static dev $$IFACE table stuttgart || true

allow-hotplug bat${seg}
iface bat${seg} inet6 manual
    pre-up          /sbin/modprobe batman-adv || true
    post-up         /sbin/brctl addif br${seg} $$IFACE || true
    post-up         /usr/sbin/batctl -m $$IFACE it 10000 || true
    post-up         /usr/sbin/batctl -m $$IFACE vm server || true
    post-up         /usr/sbin/batctl -m $$IFACE gw server  96mbit/96mbit || true
    post-up         /usr/sbin/service alfred-vpn${seg} start || true
    pre-down        /sbin/brctl delif br${seg} $$IFACE || true
    pre-down        /usr/sbin/service alfred-vpn${seg} stop || true

allow-hotplug vpn${seg}
iface vpn${seg} inet6 manual
    hwaddress 02:00:0a:38:${seg}:${gw}
    pre-up          /sbin/modprobe batman_adv || true
    post-up         /usr/sbin/batctl -m bat${seg} if add $$IFACE || true
    post-up         /sbin/ip link set dev bat${seg} up || true


