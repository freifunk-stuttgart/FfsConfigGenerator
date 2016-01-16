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

    route fd21:b4dc:4b00::a38:1/128
    {
    };
	 
};
