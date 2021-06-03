Name = ${gw}

# IPv6 + IPv4
AddressFamily = any

# Tinc nur über das öffentliche Netz laufen lassen
BindToInterface = ${interface}
Mode = switch
#IndirectData = yes
GraphDumpFile = /tmp/tinc.ffsbb.dotty
