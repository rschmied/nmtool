"""
ipv4:manual::::0:172.18.29.73/24:172.18.29.1::-1:0::no:no::0:yes:::no:yes:-1

ipv4:manual::::0:172.18.29.73/24:172.18.29.1::-1:0::no:no::0:yes:::no:yes:-1
ipv4:manual:198.18.133.1:demo.dcloud.cisco.com::0:198.18.134.1/18:198.18.128.1::-1:0::no:no:::0:yes:::0x0:no:yes:-1

ipv4:manual::::100:172.17.0.1/16:::-1:0::no:no:::0:yes:::0x0:no:yes:-1:-1

ipv4:auto:172.16.33.119:::0::::-1:0::no:yes:::0:yes:::0x0:no:yes:-1:-1

nmcli -g ipv4 c show docker0
"""

import logging
from unittest.mock import patch

import pytest
from nmtool.nmcli import cshow

good = """ipv4.method:auto
ipv4.dns:172.16.33.119
ipv4.dns-search:
ipv4.dns-options:
ipv4.dns-priority:0
ipv4.addresses:
ipv4.gateway:
ipv4.routes:
ipv4.route-metric:-1
ipv4.route-table:0
ipv4.routing-rules:
ipv4.ignore-auto-routes:no
ipv4.ignore-auto-dns:yes
ipv4.dhcp-client-id:
ipv4.dhcp-iaid:
ipv4.dhcp-timeout:0
ipv4.dhcp-send-hostname:yes
ipv4.dhcp-hostname:
ipv4.dhcp-fqdn:
ipv4.dhcp-hostname-flags:0x0
ipv4.never-default:no
ipv4.may-fail:yes
ipv4.required-timeout:-1
ipv4.dad-timeout:-1
ipv4.dhcp-vendor-class-identifier:
IP6.ADDRESS[1]:2001:470:1f0b:bcf:1bf5:6acf:5165:885e/64
IP6.ADDRESS[2]:2001:470:1f0b:bcf:3c79:d2c6:11f1:42f2/64
IP6.ADDRESS[3]:2001:470:1f0b:bcf:4884:f952:ae35:6f4b/64
IP6.ADDRESS[4]:2001:470:1f0b:bcf:4c6d:6642:3438:be3/64
IP6.ADDRESS[5]:2001:470:1f0b:bcf:b070:7170:49a8:51bb/64
IP6.ADDRESS[6]:2001:470:1f0b:bcf:d384:b1a6:41a6:c888/64
IP6.ADDRESS[7]:2001:470:1f0b:bcf:edf4:a4d5:5f48:2bb8/64
IP6.ADDRESS[8]:2001:470:1f0b:bcf:340:f902:111b:650a/64
IP6.ADDRESS[9]:fe80::d798:15ea:9d16:15ce/64
IP6.GATEWAY:fe80::cece:1eff:fea3:83b4
IP6.ROUTE[1]:dst = 2001:470:1f0b:bcf::/64, nh = fe80::cece:1eff:fea3:83b4, mt = 600
IP6.ROUTE[2]:dst = ::/0, nh = fe80::cece:1eff:fea3:83b4, mt = 600
IP6.ROUTE[3]:dst = fe80::/64, nh = ::, mt = 600
IP6.DNS[1]:2001:470:1f0b:bcf:20c:29ff:fe6a:e7ca
"""

bad = """ipv4.method:auto
ipv4.dns=172.16.33.119
ipv4.required-timeout:-1
"""


@patch("nmtool.nmcli.run")
def test_mocked_cshow(mock_run, caplog):

    # happy path
    mock_run.return_value = (good, 0)
    result = cshow("docker0")
    assert result.ipv4.method == "auto"

    # command returns an error
    mock_run.return_value = ("not found", 1)
    with pytest.raises(RuntimeError):
        result = cshow("docker0")

    # command run good, but returned result is bad
    mock_run.return_value = (bad, 0)
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        result = cshow("docker0")
    assert len(caplog.records) == 1
    assert result.ipv4.method == "auto"
