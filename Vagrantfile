# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

UUID = "OGVIFL"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|


    config.ssh.insert_key = false

    (1..2).each do |id|
        re_name  = ( "vqfx" + id.to_s ).to_sym
        pfe_name = ( "vqfx" + id.to_s + "-pfe" ).to_sym

        ##############################
        ## Packet Forwarding Engine ##
        ##############################
        config.vm.define pfe_name do |vqfxpfe|
            vqfxpfe.ssh.insert_key = false
            vqfxpfe.vm.box = 'juniper/vqfx10k-pfe'
            vqfxpfe.vm.boot_timeout = 240

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
            vqfx.vm.boot_timeout = 240

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

    (3..4).each do |id|
        re_name  = ( "veos" + id.to_s ).to_sym

        ##########################
        ## Routing Engine  #######
        ##########################
        config.vm.define re_name do |veos|
            veos.vm.hostname = "veos#{id}"
            veos.vm.box = 'keepworld/veos-lab-4.19'
            veos.vm.boot_timeout = 120

            # DO NOT REMOVE / NO VMtools installed
            #veos.vm.synced_folder '.', '/vagrant', disabled: true

            # Management port
            # No PFE on Arista
            # veos.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_veos_internal_#{id}"
            veos.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_reserved-bridge"

            # Dataplane ports
            (1..6).each do |seg_id|
               veos.vm.network 'private_network', auto_config: false, nic_type: '82540EM', virtualbox__intnet: "#{UUID}_seg#{seg_id}"
            end

            # Enable eAPI in the EOS config
            veos.vm.provision 'shell', inline: <<-SHELL
                FastCli -p 15 -c "configure
                username admin privilege 15 role network-admin secret admin
                management api http-commands
                ip routing
                interface Ethernet4
                  no switchport
                  ip address 192.168.100.99/24
                exit"
            SHELL

        end
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
