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
        "rtrs": [
            {
                "id": 1,
                "device_type": 0,
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
            {"a": 1, "z": 7, "prefixv4": "10.{pod_id}.0.0/31", "prefixv6": "fe80:{pod_id}::0/127"},
            {"a": 2, "z": 6, "prefixv4": "10.{pod_id}.0.2/31", "prefixv6": "fe80:{pod_id}::2/127"},
            {"a": 5, "z": 11, "prefixv4": "10.{pod_id}.0.4/31", "prefixv6": "fe80:{pod_id}::4/127"},
            {"a": 8, "z": 12, "prefixv4": "10.{pod_id}.0.6/31", "prefixv6": "fe80:{pod_id}::6/127"}
        ],
        "uplinks": [
            {"subnet": "10.{pod_id}.99.0/31", "interface": 3, "tags": ["tier-1", "Acorus"]},
            {"subnet": "10.{pod_id}.99.2/31", "interface": 4, "tags": ["tier-1", "Acorus"]},
            {"subnet": "10.{pod_id}.99.4/31", "interface": 9, "tags": ["tier-1", "Cloud Temple"]},
            {"subnet": "10.{pod_id}.99.6/31", "interface": 10, "tags": ["tier-1", "Cloud Temple"]}
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


def setup_device_role(api_connector, spec, color):
    device_role = api_connector.dcim.device_roles.get(name=spec.DEVICE_ROLE)
    if device_role is None:
        device_role = api_connector.dcim.device_roles.create(
            name=spec.DEVICE_ROLE,
            slug=spec.DEVICE_ROLE,
            color=color,
        )
    return device_role


def setup_tenant(api_connector, tenant_name):
    tenant = api_connector.tenancy.tenants.get(name=tenant_name)
    if tenant is None:
        tenant = api_connector.tenancy.tenants.create(
            name=tenant_name,
            slug=tenant_name
        )
    return tenant


def setup_site(api_connector, slug, tenant, asn):
    return api_connector.dcim.sites.create(
        name=slug,
        slug=slug,
        asn=asn,
        tenant=tenant.id,
    )


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


def setup_device(api_connector, name, device_role, device_type, tenant, site, tags=[]):
    return api_connector.dcim.devices.create(
        name=name,
        device_role=device_role.id,
        device_type=device_type.id,
        tenant=tenant.id,
        site=site.id,
        tags=tags
    )


def setup_interface(api_connector, device, name):
    return api_connector.dcim.interfaces.create(
        name=name,
        device=device.id
    )


def setup_loopback(api_connector, device, address):
    interface = api_connector.dcim.interfaces.create(
        name="lo0",
        device=device.id,
        type=0
    )
    ip = api_connector.ipam.ip_addresses.create(
        address=address,
        interface=interface.id
    )
    device.primary_ip4 = ip
    device.save()


def setup_connection(api_connector, a, z):
    api_connector.dcim.cables.create(
        termination_a_type="dcim.interface",
        termination_a_id=a.id,
        termination_b_type="dcim.interface",
        termination_b_id=z.id
    )

def make_pod(pod_id, api_connector):
    # Setup regular routeurs
    SPEC = POD_SPECS
    model = SPEC.MODEL
    pod_refs = {
        "devices": {},
        "interfaces": {}
    }

    tenant = setup_tenant(
        api_connector,
        tenant_name=SPEC.TENANT_NAME.format(pod_id=pod_id)
    )

    device_role = setup_device_role(
        api_connector,
        spec=SPEC,
        color="f44336"
    )

    site = api_connector.dcim.sites.create(
        name=SPEC.SITE_NAME.format(pod_id=pod_id),
        slug=SPEC.SITE_NAME.format(pod_id=pod_id),
        asn="655{pod_id:02d}".format(pod_id=pod_id),
        description="The site of the {}th pod.".format(pod_id),
        tenant=tenant.id,
    )

    for rtr in model["rtrs"]:
        assert rtr['id'] not in pod_refs["devices"]

        device_type = setup_device_type(
            api_connector,
            spec=SPEC,
            dt_id=rtr["device_type"]
        )

        # make_device
        device = setup_device(
            api_connector,
            name="{}{}".format(device_type.model, rtr['id']),
            device_role=device_role,
            device_type=device_type,
            tenant=tenant,
            site=site,
            tags=rtr['tags']
        )

        interface = api_connector.dcim.interfaces.create(
            name="lo0",
            device=device.id,
            type=0
        )
        ipv4 = api_connector.ipam.ip_addresses.create(
            address=SPEC.LOOPBACKv4.format(pod_id=pod_id, rtr_id=rtr['id']),
            interface=interface.id
        )
        ipv6 = api_connector.ipam.ip_addresses.create(
            address=SPEC.LOOPBACKv6.format(pod_id=pod_id, rtr_id=rtr['id']),
            interface=interface.id
        )
        device.primary_ip4 = ipv4
        device.primary_ip6 = ipv6
        device.save()

        pod_refs["devices"][rtr['id']] = device
        for intf in rtr['interfaces']:
            # make_interface
            assert intf['id'] not in pod_refs['interfaces']
            interface = setup_interface(api_connector, device, intf["name"])
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
        setup_connection(api_connector, a, z)
    return pod_refs

def main():
    args = vars(parse_cli_args(sys.argv[1:]))
    api_connector = pynetbox.api(
        url=args['netbox_url'],
        token=args['netbox_token']
    )

    pods_refs = make_pod(args['id'], api_connector)
    for uplink in POD_SPECS.MODEL["uplinks"]:
        subnet = uplink['subnet'].format(pod_id=args['id'])
        api_connector.ipam.prefixes.create(
            prefix=subnet,
            description="Tier1-ICO"
        )
        api_connector.ipam.ip_addresses.create(
            address="{}/32".format(str(list(ipaddress.ip_network(subnet))[1])),
            interface=pods_refs["interfaces"][uplink["interface"]].id,
        )
        api_connector.ipam.ip_addresses.create(
            address="{}/32".format(str(list(ipaddress.ip_network(subnet))[0])),
            tags=uplink["tags"]
        )


if __name__ == '__main__':
    main()