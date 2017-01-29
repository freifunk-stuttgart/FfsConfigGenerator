auto tun-${IFACE}
iface tun-${IFACE} inet tunnel
    mode gre
    netmask 255.255.255.255
    address ${TUN_LOCAL_V4}
    dstaddr ${TUN_REMOTE_V4}
    local ${GRE_LOCAL}
    endpoint ${GRE_REMOTE}
    ttl 64
    mtu 1400
    post-up /sbin/ip addr add ${NAT_V4}/32 dev $$IFACE  || true

iface tun-${IFACE} inet6 static
    address ${TUN_LOCAL_V6}/64

