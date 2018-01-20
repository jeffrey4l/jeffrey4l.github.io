Ansible with-items auto flatten list of lists
#############################################

:date: 2016-12-27
:tags: Ansible
:slug: ansible-with-items-auto-flatten-list-of-lists
:category: Ops

Ansible has ``with_items`` directive, which make task iterating the lists in
``with_items``. A normal usage is like

::
    
    - name: copy file
      copy: src={{ item }} dest=/root/.ssh/{{ item }}
      with_items:
        - id_rsa
        - id_rsa.pub

But if you use list of lists, it will not work as your expect.

::

    - name: copy file
      copy: src={{ item.0 }} dest=/root/.ssh/{{ item.1 }}
      with_items:
        - [ id_rsa, id_rsa_foo ]
        - [ id_rsa.pub, rd_rsa_foo.pub ]

Ansible will flatten the lists just like what ``with_flatten`` does. As a
result, it will work like

::
   
    - name: copy file
      copy: src={{ item.0 }} dest=/root/.ssh/{{ item.1 }}
      with_items:
        - id_rsa
        - id_rsa_foo
        - id_rsa.pub
        - id_rsa_foo.pub

This is not what we want, of curse. The workaround is wrapping the list of
lists. like:

::

    - name: copy file
      copy: src={{ item.0 }} dest=/root/.ssh/{{ item.1 }}
      with_items:
        -
          - [ id_rsa, id_rsa_foo ]
          - [ id_rsa.pub, rd_rsa_foo.pub ]

This is a historical issue rather than a bug. Here is the related ansible
bug[0] and doc fix[1].

* [0] https://github.com/ansible/ansible/issues/5913
* [1] https://github.com/ko-zu/ansible/commit/0a1a5cde86df0424441b78dd9e67b96159cfd70f

