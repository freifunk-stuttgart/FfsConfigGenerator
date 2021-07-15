interface br${seg}
{
    AdvSendAdvert on;
    IgnoreIfMissing on;
    MinRtrAdvInterval 10;
    MaxRtrAdvInterval 200;

    ${AdvDefaultLifetime}
    MinDelayBetweenRAs 10;

    prefix ${ipv6net} {};
    RDNSS ${ipv6} {};
${netroutes}${v6prefixes}
};
