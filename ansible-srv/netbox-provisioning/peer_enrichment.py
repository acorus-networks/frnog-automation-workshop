import ipaddress
import sys

def find_peer_ip(address, netmask):
    """Determine peer ip when given /31 or /30 network"""
    local_ip = ipaddress.ip_interface("{}/{}".format(address, netmask))
    peer_ip = [ip for ip in list(local_ip.network.hosts()) if ip != local_ip.ip]
    try:
        assert len(peer_ip) == 1
    except AssertionError:
        sys.exit("The auto peer IP discovering is only possible for /30, /31, /127 and /126 subnets.")
    return str(peer_ip[0])

def add_peer_ip(inventory):
    # Iterate over full inventory
    for host, definition in inventory["_meta"]["hostvars"].items():
        # Iterate over transit_interfaces
        for intf in definition["transit_interfaces"]:
            # Apply for both ipv4 and ipv6
            for v in ["ipv4", "ipv6"]:
                try:
                    # Determine peer_ip
                    peer_ip = find_peer_ip(
                        intf[v]["local_ip"],
                        intf[v]["netmask"]
                    )
                    # Set peer_ip
                    intf[v]["peer_ip"] = peer_ip
                except KeyError:
                    # If an error occured, then this host is not concerned
                    pass
        # Iterate over transit_sessions
        for session in definition["transit_sessions"]:
            # Apply for both ipv4 and ipv6
            for v in ["ipv4", "ipv6"]:
                try:
                    # Determine peer_ip
                    peer_ip = find_peer_ip(
                        session[v]["local_ip"],
                        session[v]["netmask"]
                    )
                    # Set peer_ip
                    session[v]["peer_ip"] = peer_ip
                    # Optional: Clean temp variables
                    del session[v]["local_ip"]
                    del session[v]["netmask"]
                except KeyError:
                    # If an error occured, then this host is not concerned
                    pass

    return inventory