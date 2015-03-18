Title: Nova Security Group相关配置
Date: 2015-3-18
Category: OpenStack
Tags: Network


# 相关配置

* network\_api\_class - 设置 network 模块所用的api
    * `nova.network.api.API` - 通过rpc与nova-network交互
    * `nova.network.neutronv2.API` - 通过http与neutron-server交互
* security\_group\_api - 设置 security group 模块所用的api类
    * `nova` (`nova.compute.api.SecurityGroupAPI`) - 通过rcp与nova-compute交互
    * `neutron` ( `nova.network.security_group.neutron_driver.SecurityGroupAPI` ) - 通过http与neutron-server交互
* linuxnet\_interface\_driver - 在机器与 ethernet interface plug&unplug时调用 。
    * `nova.network.linux_net.LinuxBridgeInterfaceDriver` - used in nova-network
    * `nova.network.linux_net.linuxOVSInterfaceDriver` - use in neutron + ml2 + ovs
    * `nova.network.linux_net.NeutronLinuxBridgeInterfaceDriver` - use in neutron + ml2 + linuxbridge
* firewall\_driver - 虚拟化层所用的 firewall。在nova-network时代，security group由iptables和ebtables实现。在neutron时代，这个已经不需要了。但是neutron里现在还有arp-spoofing的bug, 参见[2]
    * `nova.virt.firewall.IptablesFirewallDrive` - 
    * `nova.virt.firewall.NoopFirewallDriver`

# 使用组合：

nova-network + libvirt

    nova_api_class=nova.network.api.API
    security_group_ap=nova
    linuxnet_interface_driver=nova.network.linux_net.LinuxBridgeInterfaceDriver
    firewall_driver=nova.virt.firewall.IptablesFirewallDrive

neutron + ml2 + linuxbridge plugin + libvirt

    nova_api_class=nova.network.neutronv2.API
    security_group_ap=neutron
    linuxnet_interface_driver=nova.network.linux_net.NeutronLinuxBridgeInterfaceDriver
    firewall_driver=nova.virt.firewall.NoopFirewallDriver

neutron + ml2 + ovs plugin + libvirt

    nova_api_class=nova.network.neutronv2.API
    security_group_ap=neutron
    linuxnet_interface_driver=nova.network.linux_net.linuxOVSInterfaceDriver
    firewall_driver=nova.virt.firewall.NoopFirewallDriver

# REF

1. [ebtables in Openstack Nova](http://kennethjiang.blogspot.jp/2012/02/ebtables-in-openstack-nova-and.html) - nwfilter explaination
1. [Preventing ARP spoofing via ebtables](https://blueprints.launchpad.net/neutron/+spec/arp-spoof-patch-ebtables) - Neutron BP for preventing arp snoofing. Expected in Kilo
    1. [Neutron firewall anti-spoofing does not prevent ARP poisoning](https://bugs.launchpad.net/neutron/+bug/1274034) - Related bug
