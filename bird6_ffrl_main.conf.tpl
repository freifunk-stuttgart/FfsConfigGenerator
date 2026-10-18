function is_default() {
    return net ~ [
        ::/0
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

# BGP Export Filter fuer Rheinland
filter ebgp_ffrl_export_filter {
    if is_ffrl_specific() then accept;
    if is_ffrl_generic() then accept;
    reject;
}

# IP-NAT-Adresse legen wir in die interne BIRD Routing Table
protocol static ffrl_uplink_hostroute {
    table tk_ffsdefault;
    route ${IPV6SERVICENETWORK} reject;
    route ${IPV6NETWORK} reject;
}

# BGP Template fuer Rheinland Peerings
template bgp ffrl_uplink {
    table tk_ffsdefault;
    local as 65019;
    import keep filtered;
    import filter ebgp_ffrl_import_filter;
    export filter ebgp_ffrl_export_filter;
    next hop self;
    direct;
};
