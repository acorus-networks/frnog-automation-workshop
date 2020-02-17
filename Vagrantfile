# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

UUID = "OGVIFL"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|


    config.ssh.insert_key = false

    ### VQFX1 : 
    ###########
    config.vm.define "pfe1" do |vqfxpfe|
        vqfxpfe.ssh.insert_key = false
        vqfxpfe.vm.box = 'juniper/vqfx10k-pfe'
        vqfxpfe.vm.boot_timeout = 1200

        # DO NOT REMOVE / NO VMtools installed
        vqfxpfe.vm.synced_folder '.', '/vagrant', disabled: true
        vqfxpfe.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_1"

        # In case you have limited resources, you can limit the CPU used per vqfx-pfe VM, usually 50% is good
        # vqfxpfe.vm.provider "virtualbox" do |v|
        #    v.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
        # end
    end

    config.vm.define "vqfx1" do |vqfx|
        vqfx.vm.hostname = "vqfx1"
        vqfx.vm.box = 'juniper/vqfx10k-re'
        vqfx.vm.boot_timeout = 1200

        # DO NOT REMOVE / NO VMtools installed
        vqfx.vm.synced_folder '.', '/vagrant', disabled: true

        # Management port
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_1"
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_reserved-bridge"

        # Dataplane ports
        # Interco veos3 - xe-0/0/0
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg1"
        # Interco vqfx2 - xe-0/0/1
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg2"
        # Interco Public route server - xe-0/0/2
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg10"
        # Free
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg11"
        # Inband management port - xe-0/0/4 - seg5
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg5"
    end

    ### VQFX2 : 
    ###########
    config.vm.define "pfe2" do |vqfxpfe|
        vqfxpfe.ssh.insert_key = false
        vqfxpfe.vm.box = 'juniper/vqfx10k-pfe'
        vqfxpfe.vm.boot_timeout = 1200

        # DO NOT REMOVE / NO VMtools installed
        vqfxpfe.vm.synced_folder '.', '/vagrant', disabled: true
        vqfxpfe.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_2"

        # In case you have limited resources, you can limit the CPU used per vqfx-pfe VM, usually 50% is good
        # vqfxpfe.vm.provider "virtualbox" do |v|
        #    v.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
        # end
    end

    config.vm.define "vqfx2" do |vqfx|
        vqfx.vm.hostname = "vqfx2"
        vqfx.vm.box = 'juniper/vqfx10k-re'
        vqfx.vm.boot_timeout = 1200

        # DO NOT REMOVE / NO VMtools installed
        vqfx.vm.synced_folder '.', '/vagrant', disabled: true

        # Management port
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_2"
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_reserved-bridge"

        # Dataplane ports
        # Interco veos4 - xe-0/0/0
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg3"
        # Interco vqfx1 - xe-0/0/1
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg2"
        # Free - Backup RS ?
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg10"
        # Free
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg11"
        # Inband management port - xe-0/0/4 - seg5
        vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg5"
    end


    ### VEOS3 : 
    ###########
    config.vm.define "veos3" do |veos|
        veos.vm.hostname = "veos3"
        veos.vm.box = 'keepworld/veos-lab-4.19'
        veos.vm.boot_timeout = 240

        # DO NOT REMOVE / NO VMtools installed
        veos.vm.synced_folder '.', '/vagrant', disabled: true

        # Management port
        # No PFE on Arista
        # veos.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_veos_internal_#{id}"
        # veos.vm.network 'private_network', auto_config: false, virtualbox__intnet: "#{UUID}_reserved-bridge"

        # Interco veos3 (eth1) - vqfx1 (xe-0/0/0) - seg1
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg1"
        # Interco veos4 (eth2) - veos3 (eth3) - seg4
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg4"
        # Inband management port - eth3 - seg 5
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg5"

        # Enable eAPI in the EOS config
        veos.vm.provision 'shell', inline: <<-SHELL
            FastCli -p 15 -c "configure
            hostname veos3
            username admin privilege 15 role network-admin secret admin
            management api http-commands
            ip routing
            interface Ethernet1
              no switchport
              ip address 192.168.2.2/24
            exit
            interface Ethernet2
              no switchport
              ip address 192.168.5.1/24
            exit
            interface Ethernet3
              no switchport
              ip address 192.168.100.22/24
            exit
            "
        SHELL

    end

    ### VEOS4 : 
    ###########
    config.vm.define "veos4" do |veos|
        veos.vm.hostname = "veos4"
        veos.vm.box = 'keepworld/veos-lab-4.19'
        veos.vm.boot_timeout = 240

        # DO NOT REMOVE / NO VMtools installed
        veos.vm.synced_folder '.', '/vagrant', disabled: true

        # Management port
        # No PFE on Arista
        # veos.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_veos_internal_#{id}"
        # veos.vm.network 'private_network', auto_config: false, virtualbox__intnet: "#{UUID}_reserved-bridge"

        # Interco veos4 (eth1) - vqfx2 (xe-0/0/0) - seg3
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg3"
        # Interco veos4 (eth2) - veos3 (eth3) - seg4
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg4"
        # Inband management port - eth5 - seg 5
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg5"

        # Enable eAPI in the EOS config
        veos.vm.provision 'shell', inline: <<-SHELL
            FastCli -p 15 -c "configure
            hostname veos4
            username admin privilege 15 role network-admin secret admin
            management api http-commands
            ip routing
            interface Ethernet1
              no switchport
              ip address 192.168.4.2/24
            exit
            interface Ethernet2
              no switchport
              ip address 192.168.5.2/24
            exit
            interface Ethernet3
              no switchport
              ip address 192.168.100.23/24
            exit
            "
        SHELL

    end

    ### SRV : 
    ###########
    config.vm.define "srv" do |srv|
        srv.vm.box = "bento/ubuntu-16.04"
        srv.vm.hostname = "server"
        srv.vm.network 'private_network', ip: "192.168.100.10", virtualbox__intnet: "#{UUID}_seg5"
        srv.vm.boot_timeout = 240
        srv.ssh.insert_key = true
    end

    ##############################
    ## VQFX provisioning       ###
    ## exclude Windows host    ###
    ##############################
    if !Vagrant::Util::Platform.windows?
        config.vm.provision "ansible" do |ansible|
            ansible.groups = {
                "vqfx10k" => ["vqfx1", "vqfx2"],
                "vqfx10k-pfe" => ["vqfx1-pfe", "vqfx2-pfe"],
                "all:children" => ["vqfx10k", "vqfx10k-pfe"]
            }
            ansible.playbook = "provisioning/deploy-config-vqfx.yaml"
    end
    end


    ##############################
    ## VEOS provisioning       ###
    ## exclude Windows host    ###
    ##############################
    # if !Vagrant::Util::Platform.windows?
    #     config.vm.provision "ansible" do |ansible|
    #         ansible.groups = {
    #             "arista" => ["veos3", "veos4"],
    #             "all:children" => ["arista"]
    #         }
    #         ansible.playbook = "provisioning/deploy-config-arista.yaml"
    # end
    # end


    ##############################
    ## Server provisioning     ###
    ## exclude Windows host    ###
    ##############################
    if !Vagrant::Util::Platform.windows?
        config.vm.provision "ansible" do |ansible|
            ansible.groups = {
                "server" => ["srv"]
            }
            ansible.playbook = "provisioning/deploy-srv.yaml"
    end
    end
end
