#!/usr/bin/env python3
import sys
import pynetbox
import json
import argparse
import ipaddress


class POD_SPECS:
    TENANT_NAME = "pod{pod_id:02d}"
    DEVICE_TYPES = [
        {
            "model": "vqfx",
            "manufacturer": "juniper"
        },
        {
            "model": "veos",
            "manufacturer": "arista"
        },
    ]
    CIRCUIT_PROVIDERS = [
        {
            "name": "Acorus",
            "slug": "acorus",
            "asn": 35280,
        },
        {
            "name": "Cloud-Temple",
            "slug": "cloud-temple",
            "asn": 33930,
        },
    ]
    LOOPBACKv4 = "10.{pod_id}.200.{rtr_id}/32"
    LOOPBACKv6 = "fd00:{pod_id}::{rtr_id}/128"
    SITE_NAME = "site-pod{pod_id:02d}"
    DEVICE_ROLE = "lab-pod"
    RACK = "rack-pod{pod_id:02d}"
    MODEL = {
        "devices": [
            {
                "id": 1,
                "device_type": 0,
                "mgmt": "192.168.100.20",
                "loopback": "lo0",
                "name": "vqfx 1",
                "tags": ["router", "border-router"],
                "interfaces": [
                    {
                        "name": "xe-0/0/0",
                        "id": 1
                    },
                    {
                        "name": "xe-0/0/1",
                        "id": 2
                    },
                    {
                        "name": "xe-0/0/2",
                        "id": 3,
                        "tags": ["transit", 'acorus'],
                        "provider": 0
                    },
                    {
                        "name": "xe-0/0/3",
                        "id": 4,
                        "tags": ["transit", 'acorus'],
                        "provider": 0
                    },
                ]
            },
            {
                "id": 2,
                "device_type": 0,
                "mgmt": "192.168.100.21",
                "loopback": "lo0",
                "name": "vqfx 2",
                "tags": ["router"],
                "interfaces": [
                    {
                        "name": "xe-0/0/0",
                        "id": 5
                    },
                    {
                        "name": "xe-0/0/1",
                        "id": 6
                    }
                ]
            },
            {
                "id": 3,
                "device_type": 1,
                "mgmt": "192.168.100.22",
                "loopback": "lo0",
                "tags": ["router", "border-router"],
                "interfaces": [
                    {
                        "name": "et1",
                        "id": 7
                    },
                    {
                        "name": "et2",
                        "id": 8
                    },
                    {
                        "name": "et3",
                        "id": 9,
                        "tags": ["transit", 'cloud-temple'],
                        "provider": 1
                    },
                    {
                        "name": "et4",
                        "id": 10,
                        "tags": ["transit", 'cloud-temple'],
                        "provider": 1
                    },
                ]
            },
            {
                "id": 4,
                "device_type": 1,
                "mgmt": "192.168.100.23",
                "loopback": "lo0",
                "tags": ["router"],
                "interfaces": [
                    {
                        "name": "et1",
                        "id": 11
                    },
                    {
                        "name": "et2",
                        "id": 12
                    },
                ]
            },
        ],
        "connections": [
            {
                "a": 1,
                "z": 7,
                "prefixv4": "10.{pod_id}.0.0/31",
                "prefixv6": "fd00:{pod_id}:1::0/127"
            },
            {
                "a": 2,
                "z": 6,
                "prefixv4": "10.{pod_id}.0.2/31",
                "prefixv6": "fd00:{pod_id}:1::2/127"
            },
            {
                "a": 5,
                "z": 11,
                "prefixv4": "10.{pod_id}.0.4/31",
                "prefixv6": "fd00:{pod_id}:1::4/127"
            },
            {
                "a": 8,
                "z": 12,
                "prefixv4": "10.{pod_id}.0.6/31",
                "prefixv6": "fd00:{pod_id}:1::6/127"
            }
        ],
        "uplinks": [
            {
                "prefixv4": "10.{pod_id}.99.0/31",
                "prefixv6": "fdaa:{pod_id}::0/127",
                "interface": 3,
                "tags": ["tier-1", "Acorus"]
            },
            {
                "prefixv4": "10.{pod_id}.99.2/31",
                "prefixv6": "fdaa:{pod_id}::2/127",
                "interface": 4,
                "tags": ["tier-1", "Acorus"]
            },
            {
                "prefixv4": "10.{pod_id}.99.4/31",
                "prefixv6": "fdaa:{pod_id}::4/127",
                "interface": 9,
                "tags": ["tier-1", "Cloud Temple"]
            },
            {
                "prefixv4": "10.{pod_id}.99.6/31",
                "prefixv6": "fdaa:{pod_id}::6/127",
                "interface": 10,
                "tags": ["tier-1", "Cloud Temple"]
            }
        ]
    }


def parse_cli_args(script_args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--netbox-url', required=True, action='store',
    )
    parser.add_argument(
        '--netbox-token', required=True, action='store',
    )
    parser.add_argument(
        '--id', required=True, action='store', type=int
    )

    return parser.parse_args(script_args)



def make_pod(pod_id, api_connector):
    # Setup regular routeurs
    SPEC = POD_SPECS
    model = SPEC.MODEL
    index = {
        "devices": {},
        "interfaces": {},
        "tenant": api_connector.tenancy.tenants.create(
            name=SPEC.TENANT_NAME.format(pod_id=pod_id),
            slug=SPEC.TENANT_NAME.format(pod_id=pod_id)
        ),
        "device_role": api_connector.dcim.device_roles.create(
            name=SPEC.DEVICE_ROLE,
            slug=SPEC.DEVICE_ROLE,
            color="f44336",
        ),
        "circuit_type": api_connector.circuits.circuit_types.create(
            name="transit",
            slug="transit",
        ),
        "device_types": [],
        "manufacturer": {}
    }

    index['site'] = api_connector.dcim.sites.create(
        name=SPEC.SITE_NAME.format(pod_id=pod_id),
        slug=SPEC.SITE_NAME.format(pod_id=pod_id),
        asn="655{pod_id:02d}".format(pod_id=pod_id),
        description="The site of the {}th pod.".format(pod_id),
        physical_address="2 Rue Scribe, Paris, France",
        tenant=index['tenant'].id,
    )

    index['rack'] = api_connector.dcim.racks.create(
        name=SPEC.RACK.format(pod_id=pod_id),
        site=index["site"].id
    )

    index['circuit_providers'] = []
    for prov in SPEC.CIRCUIT_PROVIDERS:
        index['circuit_providers'].append(
            api_connector.circuits.providers.create(
                prov
            )
        )

    for dt in SPEC.DEVICE_TYPES:
        mnf_name = dt["manufacturer"]
        manufacturer = index['manufacturer'].get(mnf_name)
        if not manufacturer:
            manufacturer = api_connector.dcim.manufacturers.create(
                name=mnf_name,
                slug=mnf_name.replace(' ', '_')
            )
            index['manufacturer'][mnf_name] = manufacturer

        device_model = dt["model"]
        index['device_types'].append(
            api_connector.dcim.device_types.create(
                manufacturer=manufacturer.id,
                model=device_model,
                slug=device_model
            )
        )

    i = 0
    for dev in model["devices"]:
        # Avoid looping on the same objects - dev
        assert dev['id'] not in index["devices"]

        # Setup device
        device = api_connector.dcim.devices.create(
            name="{}{}".format(index['device_types'][dev['device_type']].model, dev['id']),
            device_role=index['device_role'].id,
            device_type=index['device_types'][dev['device_type']].id,
            tenant=index['tenant'].id,
            rack=index['rack'].id,
            position=int(dev['id']) + 1,
            face=0,
            site=index['site'].id,
            tags=dev['tags']
        )

        mgmt = api_connector.dcim.interfaces.create(
            name="mgmt",
            device=device.id,
            type=0
        )

        # Setup loopback interface
        interface = api_connector.dcim.interfaces.create(
            name=dev["loopback"],
            device=device.id,
            type=0
        )

        # Attach IP to loopback
        mgmt_ip = api_connector.ipam.ip_addresses.create(
            address=dev["mgmt"],
            interface=mgmt.id
        )
        # Attach IP to loopback
        ipv4 = api_connector.ipam.ip_addresses.create(
            address=SPEC.LOOPBACKv4.format(pod_id=pod_id, rtr_id=dev['id']),
            interface=interface.id
        )
        # Attach IP to loopback
        ipv6 = api_connector.ipam.ip_addresses.create(
            address=SPEC.LOOPBACKv6.format(pod_id=pod_id, rtr_id=dev['id']),
            interface=interface.id
        )
        device.primary_ip4 = ipv4
        device.primary_ip6 = ipv6
        device.save()

        # Load device in reference
        index["devices"][dev['id']] = device

        # Setup ico interfaces
        for intf in dev['interfaces']:
            assert intf['id'] not in index['interfaces']
            tags = intf.get('tags', [])
            interface = api_connector.dcim.interfaces.create(
                name=intf["name"],
                device=device.id,
                type=1200,
                tags=tags
            )
            if "transit" in tags:
                c = api_connector.circuits.circuits.create(
                    cid="ID-{}".format(i),
                    provider=index['circuit_providers'][intf['provider']].id,
                    type=index['circuit_type'].id,
                )
                ct = api_connector.circuits.circuit_terminations.create(
                    circuit=c.id,
                    term_side="A",
                    port_speed=10000000,
                    site=index['site'].id,
                )
                api_connector.dcim.cables.create(
                    termination_a_type="circuits.circuittermination",
                    termination_a_id=ct.id,
                    termination_b_type="dcim.interface",
                    termination_b_id=interface.id
                )

                i += 1
            # Load interface in references
            index["interfaces"][intf['id']] = interface

    for co in model["connections"]:
        a = index["interfaces"][co["a"]]
        z = index["interfaces"][co["z"]]
        ends = [a, z]
        prefix4 = co["prefixv4"].format(pod_id=pod_id)
        prefix6 = co["prefixv6"].format(pod_id=pod_id)
        net4 = ipaddress.ip_network(prefix4)
        net6 = ipaddress.ip_network(prefix6)

        for net in [net4, net6]:
            api_connector.ipam.prefixes.create(
                prefix=str(net),
                description="IPv4 inner interco prefix"
            )
            for i in range(len(ends)):
                api_connector.ipam.ip_addresses.create(
                    address="{}/{}".format(list(net)[i], net.prefixlen),
                    interface=ends[i].id,
                )

        # Connect the interfaces
        api_connector.dcim.cables.create(
            termination_a_type="dcim.interface",
            termination_a_id=a.id,
            termination_b_type="dcim.interface",
            termination_b_id=z.id
        )

    return index


def main():
    args = vars(parse_cli_args(sys.argv[1:]))
    # Netbox API connector
    api_connector = pynetbox.api(
        url=args['netbox_url'],
        token=args['netbox_token']
    )

    pods_refs = make_pod(args['id'], api_connector)

    for uplink in POD_SPECS.MODEL["uplinks"]:
        subnet = uplink['prefixv4'].format(pod_id=args['id'])
        api_connector.ipam.prefixes.create(
            prefix=subnet,
            description="Tier1-ICO-v4"
        )
        api_connector.ipam.ip_addresses.create(
            address=(
                "{}/32"
                .format(str(list(ipaddress.ip_network(subnet))[1]))
            ),
            interface=pods_refs["interfaces"][uplink["interface"]].id,
        )
        api_connector.ipam.ip_addresses.create(
            address=(
                "{}/32"
                .format(str(list(ipaddress.ip_network(subnet))[0]))
            ),
            tags=uplink["tags"]
        )
        subnet = uplink['prefixv6'].format(pod_id=args['id'])
        api_connector.ipam.prefixes.create(
            prefix=subnet,
            description="Tier1-ICO-v6"
        )
        api_connector.ipam.ip_addresses.create(
            address=(
                "{}/127"
                .format(str(list(ipaddress.ip_network(subnet))[1]))
            ),
            interface=pods_refs["interfaces"][uplink["interface"]].id,
        )
        api_connector.ipam.ip_addresses.create(
            address=(
                "{}/127"
                .format(str(list(ipaddress.ip_network(subnet))[0]))
            ),
            tags=uplink["tags"]
        )


if __name__ == '__main__':
    main()
