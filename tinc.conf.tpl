Name = ${gw}

# IPv6 + IPv4
AddressFamily = any

# Tinc nur über das öffentliche Netz laufen lassen
BindToInterface = ${interface}
Broadcast = mst

${connects}

Mode = switch
Forwarding = internal
GraphDumpFile = /tmp/tinc.ffsbb.dotty
