import socket

import netifaces as ni


def extract_host():
    try:
        return ni.ifaddresses('eth1')[2][0]['addr']
    except ValueError:
        return '127.0.0.1'


fqdn = socket.getfqdn()
host = extract_host()
