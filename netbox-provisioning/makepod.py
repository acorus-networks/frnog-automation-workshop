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
            "manufacturer": "Juniper Networks"
        },
        {
            "model": "veos",
            "manufacturer": "Arista Networks"
        },
    ]
    LOOPBACKv4 = "10.{pod_id}.200.{rtr_id}/32"
    LOOPBACKv6 = "fddd:{pod_id}::{rtr_id}/128"
    SITE_NAME = "site-pod{pod_id:02d}"
    DEVICE_ROLE = "lab-pod"
    MODEL = {
        "devices": [
            {
                "id": 1,
                "device_type": 0,
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
                        "id": 3
                    },
                    {
                        "name": "xe-0/0/3",
                        "id": 4
                    },
                ]
            },
            {
                "id": 2,
                "device_type": 0,
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
                        "id": 9
                    },
                    {
                        "name": "et4",
                        "id": 10
                    },
                ]
            },
            {
                "id": 4,
                "device_type": 1,
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
                "prefixv6": "fe80:{pod_id}::0/127"
            },
            {
                "a": 2,
                "z": 6,
                "prefixv4": "10.{pod_id}.0.2/31",
                "prefixv6": "fe80:{pod_id}::2/127"
            },
            {
                "a": 5,
                "z": 11,
                "prefixv4": "10.{pod_id}.0.4/31",
                "prefixv6": "fe80:{pod_id}::4/127"
            },
            {
                "a": 8,
                "z": 12,
                "prefixv4": "10.{pod_id}.0.6/31",
                "prefixv6": "fe80:{pod_id}::6/127"
            }
        ],
        "uplinks": [
            {
                "prefixv4": "10.{pod_id}.99.0/31",
                "prefixv6": "fc00:{pod_id}::99:0/127",
                "interface": 3,
                "tags": ["tier-1", "Acorus"]
            },
            {
                "prefixv4": "10.{pod_id}.99.2/31",
                "prefixv6": "fc00:{pod_id}::99:2/127",
                "interface": 4,
                "tags": ["tier-1", "Acorus"]
            },
            {
                "prefixv4": "10.{pod_id}.99.4/31",
                "prefixv6": "fc00:{pod_id}::99:4/127",
                "interface": 9,
                "tags": ["tier-1", "Cloud Temple"]
            },
            {
                "prefixv4": "10.{pod_id}.99.6/31",
                "prefixv6": "fc00:{pod_id}::99:6/127",
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


def setup_rack(api_connector, pod_id, site):
    return api_connector.dcim.racks.create(
        name=POD_SPECS.RACK.format(pod_id=pod_id),
        site=site.id
    )


def setup_device_type(api_connector, spec, dt_id):
    mnf_name = spec.DEVICE_TYPES[dt_id]["manufacturer"]
    manufacturer = api_connector.dcim.manufacturers.get(
        name=mnf_name,
    )
    if manufacturer is None:
        manufacturer = api_connector.dcim.manufacturers.create(
            name=mnf_name,
            slug=mnf_name.replace(' ', '_')
        )

    model = spec.DEVICE_TYPES[dt_id]["model"]

    device_type = api_connector.dcim.device_types.get(
        slug=model
    )
    if device_type is None:
        device_type = api_connector.dcim.device_types.create(
            manufacturer=manufacturer.id,
            model=model,
            slug=model
        )

    return device_type


def make_pod(pod_id, api_connector):
    # Setup regular routeurs
    SPEC = POD_SPECS
    model = SPEC.MODEL
    pod_refs = {
        "devices": {},
        "interfaces": {}
    }

    # Setup tenant
    tenant_name = SPEC.TENANT_NAME.format(pod_id=pod_id)
    tenant = api_connector.tenancy.tenants.get(name=tenant_name)
    if tenant is None:
        tenant = api_connector.tenancy.tenants.create(
            name=tenant_name,
            slug=tenant_name
        )

    # Setup device role
    device_role = api_connector.dcim.device_roles.get(name=SPEC.DEVICE_ROLE)
    if device_role is None:
        device_role = api_connector.dcim.device_roles.create(
            name=SPEC.DEVICE_ROLE,
            slug=SPEC.DEVICE_ROLE,
            color="f44336",
        )

    # Setup site
    site = api_connector.dcim.sites.create(
        name=SPEC.SITE_NAME.format(pod_id=pod_id),
        slug=SPEC.SITE_NAME.format(pod_id=pod_id),
        asn="655{pod_id:02d}".format(pod_id=pod_id),
        description="The site of the {}th pod.".format(pod_id),
        physical_address="2 Rue Scribe, Paris, France",
        tenant=tenant.id,
    )

    for dev in model["devices"]:
        # Avoid looping on the same objects - dev
        assert dev['id'] not in pod_refs["devices"]

        device_type = setup_device_type(
            api_connector,
            spec=SPEC,
            dt_id=dev["device_type"]
        )

        # Setup device
        device = api_connector.dcim.devices.create(
            name="{}{}".format(device_type.model, dev['id']),
            device_role=device_role.id,
            device_type=device_type.id,
            tenant=tenant.id,
            site=site.id,
            tags=dev['tags']
        )

        # Setup loopback interface
        interface = api_connector.dcim.interfaces.create(
            name=dev["loopback"],
            device=device.id,
            type=0
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
        pod_refs["devices"][dev['id']] = device

        # Setup ico interfaces
        for intf in dev['interfaces']:
            assert intf['id'] not in pod_refs['interfaces']
            interface = api_connector.dcim.interfaces.create(
                name=intf["name"],
                device=device.id
            )
            # Load interface in references
            pod_refs["interfaces"][intf['id']] = interface

    for co in model["connections"]:
        a = pod_refs["interfaces"][co["a"]]
        z = pod_refs["interfaces"][co["z"]]
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

    return pod_refs


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
