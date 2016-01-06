# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

hostname    = 'rentrocket'
tld         = 'vm'
fqdn        = "#{hostname}.#{tld}"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/trusty64"

  # Host and Network config

  config.vm.define hostname do | h |
    # puts "Ran config.vm.define for #{hostname}"
  end

  config.vm.hostname = hostname
  config.ssh.forward_agent = true
  config.vm.network :private_network, ip: "33.33.33.60"

  config.vm.provider 'virtualbox' do |vb, override|
    # Give VM access to all cpu cores on the host

    cpus = case RbConfig::CONFIG['host_os']
      when /darwin/ then `sysctl -n hw.ncpu`.to_i
      when /linux/ then `nproc`.to_i
      else 2
    end

    # Customize VM name
    vb.customize ['modifyvm', :id, '--name', fqdn]

    # Customize memory in MB
    vb.customize ['modifyvm', :id, '--memory', 1024]
    vb.customize ['modifyvm', :id, '--cpus', cpus]

    # Fix for slow external network connections
    vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
    vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']

    # vagrant-dns config
    if Vagrant.has_plugin? 'vagrant-dns'
      config.dns.tld        = tld
      config.dns.patterns   = [/^.*rentrocket.vm$/]
      # aliases.each do |host|
      #   config.vagrant-dns.host host, PRIVATE_IP
      # end
    else
      puts 'vagrant-dns missing, please install the plugin:'
      puts 'vagrant plugin install vagrant-dns'
    end

  end


  config.vm.provision :shell, path: "bootstrap.sh"

end

# optional
VagrantDNS::Config.logger = Logger.new("dns.log")