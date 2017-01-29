interface br${seg}
{
    AdvSendAdvert on;
    IgnoreIfMissing on;
    MinRtrAdvInterval 10;
    MaxRtrAdvInterval 200;

    # don't advertise default router
    AdvDefaultLifetime 0;
    MinDelayBetweenRAs 10;

    prefix ${ipv6net} {};
    RDNSS ${ipv6} {};
${netroutes}
};
