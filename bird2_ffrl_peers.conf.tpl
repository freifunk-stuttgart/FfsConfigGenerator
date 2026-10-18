protocol bgp ${IFACE} from ffrl_uplink {
    source address ${TUN_LOCAL_V4};
    neighbor ${TUN_REMOTE_V4} as 201701;
    ipv4 { default bgp_local_pref 200; };
};

protocol bgp ${IFACE}_6 from ffrl_uplink_6 {
    source address ${TUN_LOCAL_V6};
    neighbor ${TUN_REMOTE_V6} as 201701;
    ipv6 { default bgp_local_pref 200; };
};

