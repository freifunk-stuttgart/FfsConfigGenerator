#Segment: ${segment}
subnet ${ipv4net} netmask ${netmask} {
    authoritative;
    pool
    {
     range 1${ipv4start} ${ipv4end};
     allow all clients;
    }
    option routers ${ipv4gw};
    option domain-name-servers ${ipv4gw};
    if (packet(24, 4) != 00:00:00:00) {
        option routers = packet(24, 4);
        option freifunk.server-id = packet(24, 4);
        option domain-name-servers = packet(24, 4);
        option dhcp-server-identifier = packet(24, 4);
    }
}

