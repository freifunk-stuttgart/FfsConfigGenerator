define ffrl_nat_address = ${NAT_V4};

function is_default() {
    return net ~ [
        0.0.0.0/0
    ];
}

function is_default_6() {
    return net ~ [
        ::/0
    ];
}

function is_ffrl_nat() {
    return net ~ [
        ${NAT_V4}/32
    ];
}

function is_ffrl_specific() {
    return net ~ [
        ${IPV6NETWORK}
    ];
}

function is_ffrl_generic() {
    return net ~ [
        ${IPV6SERVICENETWORK}
    ];
}

# BGP Import Filter fuer Rheinland
filter ebgp_ffrl_import_filter {
    if is_default() then accept;
    reject;
}

# BGP Import Filter fuer Rheinland
filter ebgp_ffrl_import_filter_6 {
    if is_default_6() then accept;
    reject;
}

# BGP Export Filter fuer Rheinland
filter ebgp_ffrl_export_filter {
    if is_ffrl_nat() then accept;
    reject;
}

# BGP Export Filter fuer Rheinland
filter ebgp_ffrl_export_filter_6 {
    if is_ffrl_specific() then accept;
    if is_ffrl_generic() then accept;
    reject;
}

# IP-NAT-Adresse legen wir in die interne BIRD Routing Table
protocol static ffrl_uplink_hostroute {
    table tk_ffsdefault;
    route ${NAT_V4}/32 reject;
}

# IP-NAT-Adresse legen wir in die interne BIRD Routing Table
protocol static ffrl_uplink_hostroute_6 {
    table tk_ffsdefault_6;
    route ${IPV6SERVICENETWORK} reject;
    route ${IPV6NETWORK} reject;
}

# BGP Template fuer Rheinland Peerings
template bgp ffrl_uplink {
    local as 65019;
    ipv4 {
        table tk_ffsdefault;
        import keep filtered;
        import filter ebgp_ffrl_import_filter;
        export filter ebgp_ffrl_export_filter;
        next hop self;
    };
    direct;
};

# BGP Template fuer Rheinland Peerings
template bgp ffrl_uplink_6 {
    local as 65019;
    ipv6 {
        table tk_ffsdefault_6;
        import keep filtered;
        import filter ebgp_ffrl_import_filter_6;
        export filter ebgp_ffrl_export_filter_6;
        next hop self;
    };
    direct;
};
