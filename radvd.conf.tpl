interface br${seg}
{
    AdvSendAdvert on;
    IgnoreIfMissing on;
    MaxRtrAdvInterval 200;

    # don't advertise default router
    AdvDefaultLifetime 0;
    UnicastOnly on;

    prefix ${ipv6net}
    {};

    RDNSS ${ipv6}
    {};

${hostroutes}
${netroutes}
};
