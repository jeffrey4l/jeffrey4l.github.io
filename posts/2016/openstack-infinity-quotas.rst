Infinity OpenStack Quotas
#########################

:date: 2016-09-02 16:00:00
:tag: OpenStack
:catalog: OpenStack

在做 ``rally`` 测试时，经常会遇到 quotas 的问题，各个资源都有资源限制。一种办法是用 quotas 的 context， 设置新建的 tenant 的 Quotas 值。如下

::

    ---
      NovaServers.boot_server:
        -
          args:
            flavor:
                name: "micro-1"
            image:
                name: "^cirros$"
          runner:
            type: "constant"
            times: 100
            concurrency: 5
          context:
            users:
              tenants: 3
              users_per_tenant: 2
            quotas:
              nova:
                instances: -1
                cores: -1
                ram: -1

但是一个文件一个文件的改太闹心了。而且有的时候搭建测试环境，根本不需要使用 Quota 的功能。这时可以通过修改配置文件来完全关闭 Quota


For Nova

::

    # nova.conf
    [DEFAULT]
    quota_instances = -1
    quota_cores = -1
    quota_ram = -1 
    quota_floating_ips = -1
    quota_fixed_ips = -1
    quota_metadata_items = -1
    quota_injected_files = -1
    quota_injected_file_content_bytes = -1
    quota_injected_file_path_length = -1
    quota_security_groups = -1
    quota_security_group_rules = -1
    quota_key_pairs = -1
    quota_server_groups = -1
    quota_server_group_members = -1


For Neutron

::
    
    # neutron.conf
    [quotas]
    default_quota = -1
    quota_network = -1
    quota_subnet = -1
    quota_port = -1
    quota_router = -1
    quota_floatingip = -1
    quota_security_group = -1
    quota_security_group_rule = -1

For Cinder

Cinder 现在是通过 quota class 来控制 default quota, 如果想要改变默认 quota 的话，使用如下命令。

::

    # cinder.conf
    [DEFAULT]
    quota_volumes = -1
    quota_snapshots = -1
    quota_consistencygroups = -1
    quota_gigabytes = -1
    quota_backups = -1
    quota_backup_gigabytes = -1


通过 quota class 来控制

::
    openstack quota set --class default \
        --instances -1 --injected-files -1 --cores -1 --ram -1 --injected-path-size -1 \
        --key-pairs -1 \
        --gigabytes -1 --volumes -1 --snapshots -1 \
        --ports -1 --subnets -1 --networks -1 --routers -1 \
        --floating-ips -1 --fixed-ips -1 \
        --health-monitors -1 --members -1 --vips -1 \
        --secgroups -1 --secgroup-rules -1 \
        --subnetpools -1 \
        --rbac-policies -1
