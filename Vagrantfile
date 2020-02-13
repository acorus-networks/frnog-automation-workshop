# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

UUID = "OGVIFL"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|


    config.ssh.insert_key = false

    (1..1).each do |id|
        re_name  = ( "vqfx" + id.to_s ).to_sym
        pfe_name = ( "vqfx" + id.to_s + "-pfe" ).to_sym

        ##############################
        ## Packet Forwarding Engine ##
        ##############################
        config.vm.define pfe_name do |vqfxpfe|
            vqfxpfe.ssh.insert_key = false
            vqfxpfe.vm.box = 'juniper/vqfx10k-pfe'
            vqfxpfe.vm.boot_timeout = 1200

            # DO NOT REMOVE / NO VMtools installed
            vqfxpfe.vm.synced_folder '.', '/vagrant', disabled: true
            vqfxpfe.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_#{id}"

            # In case you have limited resources, you can limit the CPU used per vqfx-pfe VM, usually 50% is good
            # vqfxpfe.vm.provider "virtualbox" do |v|
            #    v.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
            # end
        end

        ##########################
        ## Routing Engine  #######
        ##########################
        config.vm.define re_name do |vqfx|
            vqfx.vm.hostname = "vqfx#{id}"
            vqfx.vm.box = 'juniper/vqfx10k-re'
            vqfx.vm.boot_timeout = 1200

            # DO NOT REMOVE / NO VMtools installed
            vqfx.vm.synced_folder '.', '/vagrant', disabled: true

            # Management port
            vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_vqfx_internal_#{id}"
            vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_reserved-bridge"

            # Dataplane ports
            (1..6).each do |seg_id|
               vqfx.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg#{seg_id}"
            end
        end
    end

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

        # Interco veos3 (eth2) - vqfx1 (xe-0/0/0) - seg1
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg1"
        # Interco veos4 (eth3) - veos3 (eth3) - seg4
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg4"
        # Inband management port - eth4 - seg 5
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg5"

        # Enable eAPI in the EOS config
        veos.vm.provision 'shell', inline: <<-SHELL
            FastCli -p 15 -c "configure
            hostname veos3
            username admin privilege 15 role network-admin secret admin
            management api http-commands
            ip routing
            interface Ethernet2
              no switchport
              ip address 192.168.2.2/24
            exit
            interface Ethernet3
              no switchport
              ip address 192.168.5.1/24
            exit
            interface Ethernet4
              no switchport
              ip address 192.168.100.22/24
            exit
            "
        SHELL

    end

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

        # Interco veos4 (eth2) - vqfx2 (xe-0/0/0) - seg3
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg3"
        # Interco veos4 (eth3) - veos3 (eth3) - seg4
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg4"
        # Inband management port - eth4 - seg 5
        veos.vm.network 'private_network', auto_config: false, ip: '169.254.1.11', virtualbox__intnet: "#{UUID}_seg5"

        # Enable eAPI in the EOS config
        veos.vm.provision 'shell', inline: <<-SHELL
            FastCli -p 15 -c "configure
            hostname veos3
            username admin privilege 15 role network-admin secret admin
            management api http-commands
            ip routing
            interface Ethernet2
              no switchport
              ip address 192.168.4.2/24
            exit
            interface Ethernet3
              no switchport
              ip address 192.168.5.2/24
            exit
            interface Ethernet4
              no switchport
              ip address 192.168.100.23/24
            exit
            "
        SHELL

    end

    ##########################
    ## Server          #######
    ##########################
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
    #             "arista" => ["veos1", "veos2"],
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
