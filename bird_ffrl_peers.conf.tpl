protocol bgp ${IFACE} from ffrl_uplink {
    source address ${TUN_LOCAL_V4};
    neighbor ${TUN_REMOTE_V4} as 201701;
    default bgp_local_pref 200;
};

