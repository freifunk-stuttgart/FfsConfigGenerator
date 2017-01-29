Hostname "${HOSTNAME}"
LoadPlugin syslog

<Plugin syslog>
	LogLevel info
</Plugin>

LoadPlugin cpu
LoadPlugin df
LoadPlugin disk
LoadPlugin entropy
LoadPlugin interface
LoadPlugin irq
LoadPlugin load
LoadPlugin memory
LoadPlugin processes
LoadPlugin rrdtool
LoadPlugin swap
LoadPlugin uptime
LoadPlugin users
LoadPlugin write_graphite

<Plugin df>
	FSType rootfs
	FSType sysfs
	FSType proc
	FSType devtmpfs
	FSType devpts
	FSType tmpfs
	FSType fusectl
	FSType cgroup
	IgnoreSelected true
</Plugin>

<Plugin rrdtool>
	DataDir "/var/lib/collectd/rrd"
</Plugin>

<Plugin write_graphite>
	<Node "netinfo">
		Host "10.191.255.243"
		Port "2003"
		Protocol "tcp"
	</Node>
</Plugin>

<Include "/etc/collectd/collectd.conf.d">
	Filter "*.conf"
</Include>

