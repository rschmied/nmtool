import json

from .nmcli import cshow

iface = "docker0"

r = cshow(iface)
print(json.dumps(r, indent=4))
print(r.ipv4.dad_timeout)
print(list(r.keys()))
