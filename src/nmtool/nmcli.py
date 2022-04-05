import logging
import re
from typing import Dict

from .run_cmd import run

# -t terse
# -f fields

# ipv4.method:auto
# ipv4.dns:172.16.33.119
# ipv4.dns-search:
# ipv4.dns-options:
# ipv4.dns-priority:0
# ipv4.addresses:
# ipv4.gateway:
# ipv4.routes:
# ipv4.route-metric:-1
# ipv4.route-table:0
# ipv4.routing-rules:
# ipv4.ignore-auto-routes:no
# ipv4.ignore-auto-dns:yes
# ipv4.dhcp-client-id:
# ipv4.dhcp-iaid:
# ipv4.dhcp-timeout:0
# ipv4.dhcp-send-hostname:yes
# ipv4.dhcp-hostname:
# ipv4.dhcp-fqdn:
# ipv4.dhcp-hostname-flags:0x0
# ipv4.never-default:no
# ipv4.may-fail:yes
# ipv4.required-timeout:-1
# ipv4.dad-timeout:-1
# ipv4.dhcp-vendor-class-identifier:

# IP6.ADDRESS[1]:2001:470:1f0b:bcf:1bf5:6acf:5165:885e/64

_LOGGER = logging.getLogger(__name__)
regex = re.compile(r"^([\w-]+)\.([\w-]+)(\[\d+\])?:(.*)?$")


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __dir__ = dict.keys


def cshow(iface: str) -> Dict:
    result, code = run("nmcli", "-t", "connection", "show", iface)
    if code != 0:
        raise RuntimeError

    def normalize_key(key: str) -> str:
        return key.lower().replace("-", "_")

    out = dotdict()
    for line in result.split("\n"):
        if len(line) == 0:
            continue
        m = re.match(regex, line)
        if m is None:
            _LOGGER.warning("unparsable line %s", line)
            continue

        primary_key = normalize_key(m[1])
        subkey = normalize_key(m[2])

        if out.get(primary_key) is None:
            out[primary_key] = dotdict()

        if m[3] is None:
            out[primary_key][subkey] = m[4]
        else:
            if out.get(primary_key).get(subkey) is None:
                out[primary_key][subkey] = list()
            out[primary_key][subkey].append(m[4])

    return out
