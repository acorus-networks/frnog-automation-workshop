#!/usr/bin/env python3
import sys
import pynetbox
import json
import argparse

class LAB_SPEC:
    TENANT = "tier1-operator"
    RTR_NAMING = "tier1-rtr{rtr_id}"
    LOOPBACK = "10.0.1.{rtr_id}/32"
    DEVICE_TYPES = [
        {
            "model": "MX10k",
            "manufacturer": "Juniper Networks"
        }
    ]
    DEVICE_ROLE = "lab-tier1"
    TIER1_SITE = "tier1"
    MODEL = {
        "tier1": {
            "devices": [
                {
                    "id": 1,
                    "device_type": 0
                }
            ]
        }
    }

class POD_SPECS:
    TENANT = "pod{pod_id:02d}"
    DEVICE_TYPES = [
        {
            "model": "EX3400",
            "manufacturer": "Juniper Networks"
        }
    ]
    RTR_NAMING = "pod{pod_id:02d}-rtr{rtr_id}"
    LOOPBACK = "10.{pod_id}.1.{rtr_id}/32"
    SITE = "site-pod{pod_id:02d}"
    DEVICE_ROLE = "lab-pod"
    MODEL = {
        "rtrs": [
            {
                "id": 1,
                "device_type": 0,
                "interfaces": [
                    {
                        "name": "ge-0/0/0",
                        "id": 1
                    },
                    {
                        "name": "ge-0/0/1",
                        "id": 2
                    }
                ]
            },
            {
                "id": 2,
                "device_type": 0,
                "interfaces": [
                    {
                        "name": "ge-0/0/0",
                        "id": 3
                    },
                    {
                        "name": "ge-0/0/1",
                        "id": 4
                    }
                ]
            },
            {
                "id": 3,
                "device_type": 0,
                "interfaces": [
                    {
                        "name": "ge-0/0/0",
                        "id": 5
                    },
                    {
                        "name": "ge-0/0/1",
                        "id": 6
                    }
                ]
            },
            {
                "id": 4,
                "device_type": 0,
                "interfaces": [
                    {
                        "name": "ge-0/0/0",
                        "id": 7
                    },
                    {
                        "name": "ge-0/0/1",
                        "id": 8
                    }
                ]
            },
        ],
        "connections": [
            {"a": 1, "z": 3, "subnet": "10.{pod_id}.0.0/31"},
            {"a": 4, "z": 6, "subnet": "10.{pod_id}.0.2/31"},
            {"a": 5, "z": 7, "subnet": "10.{pod_id}.0.4/31"},
            {"a": 8, "z": 2, "subnet": "10.{pod_id}.0.6/31"}
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
        '-c', '--pod-count', type=int, required=True, action='store',
    )

    # Parse script arguments and return the result
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

def setup_site(api_connector, slug, tenant):
    return api_connector.dcim.sites.create(
        name=slug,
        slug=slug,
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

def setup_device(api_connector, name, device_role, device_type, tenant, site):
    return api_connector.dcim.devices.create(
        name=name,
        device_role=device_role.id,
        device_type=device_type.id,
        tenant=tenant.id,
        site=site.id
    )

def setup_interface(api_connector, device, name):
    return api_connector.dcim.interfaces.create(
        name=name,
        device=device.id
    )

def setup_loopback(api_connector, device, address):
    interface = api_connector.dcim.interfaces.create(
        name="lo",
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


def setup_ico_network(api_connector, a, z, subnet):
    api_connector.ipam.prefixes.create(prefix=subnet)
    spl = subnet.split('/')
    mask = spl[1]
    ip = spl[0].split(".")[:-1]
    hosta = spl[0].split(".")[-1]
    hostz = str(int(hosta) + 1)

    ipa = api_connector.ipam.ip_addresses.create(
        address="{}/{}".format('.'.join(ip + [hosta]), mask),
        interface=a.id,
    )
    ipz = api_connector.ipam.ip_addresses.create(
        address="{}/{}".format('.'.join(ip + [hostz]), mask),
        interface=z.id,
    )


def make_pod(pod_id, api_connector):
    # Setup regular routeurs
    model = POD_SPECS.MODEL
    SPEC = POD_SPECS
    pod_refs = {
        "devices": {},
        "interfaces": {}
    }
    tenant = setup_tenant(api_connector, tenant_name=SPEC.TENANT.format(pod_id=pod_id))
    device_role = setup_device_role(api_connector, spec=SPEC, color="f44336")

    # make_site
    site = setup_site(api_connector, slug=SPEC.SITE.format(pod_id=pod_id), tenant=tenant)

    for rtr in model["rtrs"]:
        assert rtr['id'] not in pod_refs["devices"]
        device_type = setup_device_type(api_connector, spec=SPEC, dt_id=rtr["device_type"])

        # make_device
        device = setup_device(
            api_connector,
            name=SPEC.RTR_NAMING.format(pod_id=pod_id, rtr_id=rtr['id']),
            device_role=device_role,
            device_type=device_type,
            tenant=tenant,
            site=site
        )
        setup_loopback(
            api_connector,
            device=device,
            address=SPEC.LOOPBACK.format(pod_id=pod_id, rtr_id=rtr['id'])
        )
        pod_refs["devices"][rtr['id']] = device
        for intf in rtr['interfaces']:
            # make_interface
            assert intf['id'] not in pod_refs['interfaces']
            interface = setup_interface(api_connector, device, intf["name"])
            pod_refs["interfaces"][intf['id']] = interface

    for co in model["connections"]:
        # make ip
        # make connections
        a = pod_refs["interfaces"][co["a"]]
        z = pod_refs["interfaces"][co["z"]]
        setup_ico_network(api_connector, a, z, co["subnet"].format(pod_id=pod_id))
        setup_connection(api_connector, a, z)
    return pod_refs


def make_tier1(api_connector, pod_count, refs):
    model = LAB_SPEC.MODEL["tier1"]
    SPEC = LAB_SPEC
    pod_refs = {
        "devices": {},
        "interfaces": {}
    }

    tenant = setup_tenant(api_connector, tenant_name=SPEC.TENANT)
    device_role = setup_device_role(api_connector, spec=SPEC, color="43f436")

    # make_site
    site = setup_site(api_connector, slug=SPEC.TIER1_SITE, tenant=tenant)

    for rtr in model["devices"]:
        assert rtr['id'] not in pod_refs["devices"]
        device_type = setup_device_type(api_connector, spec=SPEC, dt_id=rtr["device_type"])

        # make_device
        device = setup_device(
            api_connector,
            name=SPEC.RTR_NAMING.format(rtr_id=rtr["id"]),
            device_role=device_role,
            device_type=device_type,
            tenant=tenant,
            site=site
        )
        setup_loopback(
            api_connector,
            device=device,
            address=SPEC.LOOPBACK.format(rtr_id=rtr["id"]),
        )
        pod_refs["devices"][rtr['id']] = device
        for i in range(0, pod_count):
            # make_interface
            assert i not in pod_refs['interfaces']
            interface = setup_interface(api_connector, device, "ge-0/0/{}".format(i))
            pod_refs["interfaces"][i] = interface

    # for co in model["connections"]:
    #     # make ip
    #     # make connections
    #     a = pod_refs["interfaces"][co["a"]]
    #     z = pod_refs["interfaces"][co["z"]]
    #     setup_ico_network(api_connector, a, z, co["subnet"].format(pod_id=pod_id))
    #     setup_connection(api_connector, a, z)
    #     return pod_refs


def main():
    args = vars(parse_cli_args(sys.argv[1:]))
    api_connector = pynetbox.api(
        url=args['netbox_url'],
        token=args['netbox_token']
    )

    pods_refs = {}
    for pod_id in range(0, args['pod_count']):
        pods_refs[pod_id] = make_pod(pod_id + 1, api_connector)

    make_tier1(api_connector, args['pod_count'], pods_refs)


if __name__ == '__main__':
    main()