//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";
acl "intern-s" {
${ipv4net}
${ipv6net}
};

