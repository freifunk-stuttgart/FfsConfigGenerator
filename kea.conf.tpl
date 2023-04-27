// Segment ${segment}
{   
	"subnet": "${ipv4net}/${netmask}",

	"pools": [ { "pool": "${ipv4start} - ${ipv4end}" } ],

	"option-data": [
		{
			// dummy router, will be overwritten
			"name": "routers",
			"data": "192.0.2.1"
		},
		{
			// dummy dhcp server, will be overwritten
			"name": "domain-name-servers",
			"data": "192.0.2.1"
		}
	]
},
