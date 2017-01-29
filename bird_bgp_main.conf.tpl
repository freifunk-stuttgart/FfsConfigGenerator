define ffrl_nat_address = ${NAT_V4};

function is_default() {
    return net ~ [
        0.0.0.0/0
    ];
}

function is_ffrl_nat() {
    return net ~ [
        ${NAT_V4}/32
    ];
}

function is_ffrl_tunnel_nets() {
    return net ~ [
        100.64.8.164/31
        #FIXME here are some missing
    ];
}

# BGP Import Filter fuer Rheinland
filter ebgp_ffrl_import_filter {
    if is_default() then accept;
    reject;
}

# BGP Export Filter fuer Rheinland
filter ebgp_ffrl_export_filter {
    if is_ffrl_nat() then accept;
    reject;
}

# IP-NAT-Adresse legen wir in die interne BIRD Routing Table
protocol static ffrl_uplink_hostroute {
    route ${NAT_V4}/32 reject;
}

# Wir legen die Transfernetze in die interne BIRD Routing Table
protocol direct {
    interface "tun-*";
    import where is_ffrl_tunnel_nets();
}

# BGP Template fuer Rheinland Peerings
template bgp ffrl_uplink {
    local as 65019;
    import keep filtered;
    import filter ebgp_ffrl_import_filter;
    export filter ebgp_ffrl_export_filter;
    next hop self;
    direct;
};
