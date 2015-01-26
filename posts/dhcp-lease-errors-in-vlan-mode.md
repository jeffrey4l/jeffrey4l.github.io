title: Dhcp lease errors in vlan mode
date: 2013-08-27 08:50
tags: DHCP, Network, VLAN 
Category: Openstack


在使用``keepalived``的过程中，出现了dhcp失败，而导致keepalived工作不正常的问题。而且之前也出现过dhcp偶尔失败，导致虚拟机不能得到IP, 从而不能访问的情况。虽然在``/etc/sysconfig/network-scripts/ifcfg-eth0``中加上了如下语句：

    PERSISTENT_DHCLIENT=1

使得dhcp单次失败后，继续重试。但是仔细查看dhclient的日志后，发现它有大量的dhcp request失败/超时。在一个[邮件列表](http://openstack.markmail.org/search/?q=Dhcp+lease+errors+in+vlan+mode#query:Dhcp%20lease%20errors%20in%20vlan%20mode+page:1+mid:7kjf4hljszpydsrx+state:results)中找到原因，如下：


To fix issues with failed dhcp leases in vlan mode, upgrade to dnsmasq 2.6.1

THE LONG VERSION

There is an issue with the way nova uses dnsmasq in VLAN mode. It starts up a
single copy of dnsmasq for each vlan on the network host (or on every host in
multi_host mode). The problem is in the way that dnsmasq binds to an ip address
and port. Both copies can respond to broadcast packet, but unicast packets
can only be answered by one of the copies.

In nova this means that guests from only one project will get responses to their
unicast dhcp renew requests.  Unicast projects from guests in other projects get
ignored. What happens next is different depending on the guest os.  Linux
generally will send a broadcast packet out after the unicast fails, and so the
only effect is a small (tens of ms) hiccup while interface is reconfigured.  It
can be much worse than that, however. I have seen cases where Windows just gives
up and ends up with a non-configured interface.

This bug was first noticed by some users of openstack who rolled their own fix.
Basically, on linux, if you set the SO_BINDTODEVICE socket option, it will allow
different daemons to share the port and respond to unicast packets, as long as
they listen on different interfaces. I managed to communicate with Simon Kelley,
the maintainer of dnsmasq and he has integrated a fix for the issue in the
current version of dnsmaq.

I don't know how may users out there are using vlan mode, but you should be able
to deal with this issue by upgrading dnsmasq. It would be great if the various
distributionss could upgrade as well, or at least try to patch in the fix. If
upgrading dnsmasq is out of the question, a possible workaround is to minimize
lease renewals with something like the following combination of config options.


    # release leases immediately on terminate
    force_dhcp_release=true
    # one week lease time
    dhcp_lease_time=604800
    # two week disassociate timeout
    fixed_ip_disassociate_timeout=1209600

This is also documented [ Known issue with failed DHCP leases in VLAN configuration](http://docs.openstack.org/trunk/openstack-compute/admin/content/configuring-vlan-networking.html#vlan-known-issues)
