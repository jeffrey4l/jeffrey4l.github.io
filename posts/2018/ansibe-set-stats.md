title: ansible set_stats
date: 2018-10-14
slug: ansible-set-stats

`set_stats` 支持用户设置任意数值，用以在 ansible 运行完后显示。

使用例子如下


```YAML
---
- hosts: all
  gather_facts: true

  pre_tasks:
    - name: set ceph iscsi gateway install 'In Progress'
      run_once: true
      set_stats:
        data:
          installer_phase_ceph_iscsi_gw:
            status: "In Progress"
            start: "{{ lookup('pipe', 'date +%Y%m%d%H%M%SZ') }}"
  tasks:
    - debug:
        msg: 'hello world'
  post_tasks:
    - name: set ceph iscsi gw install 'Complete'
      run_once: true
      set_stats:
        data:
          installer_phase_ceph_iscsi_gw:
            status: "Complete"
            end: "{{ lookup('pipe', 'date +%Y%m%d%H%M%SZ') }}"
```

* data 参数可以配置任意的值
* 还有一个 aggregate 的参数，默认值是 yes, 他表示是否要和已经存在的值聚合。

在运行 ansible 时，需在`ansible.cfg` 里配置 `show_custom_stats=true` 或通过环境变量配置`ANSIBLE_SHOW_CUSTOM_STATS=true` 来开启 stats 的输出。

```console
$ ANSIBLE_SHOW_CUSTOM_STATS=true ansible-playbook -i inventory test.yml

PLAY [all]

TASK [set ceph iscsi gateway install 'In Progress'] 
ok: [10.10.0.2]

TASK [debug] 
ok: [10.10.0.2] => {
    "msg": "hello world"
}

TASK [set ceph iscsi gw install 'Complete'] 
ok: [10.10.0.2]

PLAY RECAP 
10.10.0.2                  : ok=3    changed=0    unreachable=0    failed=0   

CUSTOM STATS: 
	RUN: { "installer_phase_ceph_iscsi_gw": {  "end": "20181009151731Z",  "start": "20181009151731Z",  "status": "Complete" }}
```

可以看到，结果上已经把 custom stats 的值打印出来了。这样就可以把运行过程中的一些状态或统计信息输出出来，方便 playbooks 运行完成后，查看其运行状态。

以外，这个模块也适用于 windows

## 相关链接

* [1] <https://docs.ansible.com/ansible/2.6/modules/set_stats_module.html>
