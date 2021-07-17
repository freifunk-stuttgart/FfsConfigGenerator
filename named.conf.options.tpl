options {
    directory "/var/cache/bind";

    dnssec-validation auto;

    auth-nxdomain no;    # conform to RFC1035
    #this might not be the full list, named currently not used
    #listen-on { 127.0.0.1; ${ipv4addr} };
    #listen-on-v6 { ::1; fe80::6037:a9ff:fed4:a2fa; ${ipv6addr} };

    allow-query { 127.0.0.1; ::1; intern-s;};
    allow-recursion { 127.0.0.1; ::1; intern-s; };
};
