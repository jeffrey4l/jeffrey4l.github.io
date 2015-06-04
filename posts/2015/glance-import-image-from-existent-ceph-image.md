Title: Glance Create Image from Existent Image in Ceph
Date: 2015-06-04
Category: OpenStack

当使用 Ceph + Glance 时，镜像需要使用 RAW 格式，这会导致创建镜像时非常的慢。有的时候，也需要把 Ceph 中现有的镜像导入到 Glance 中。这时可以使用 --location 参数来指定镜像所在的远程位置。也就可以使用现有的 Ceph 镜像来快速创建。

可以先用 rbd 上传镜像，转换格式(也会比较慢，还不如直接上传 RAW 格式的镜像)。然后再做好对应的 snap , 并加以保护。是后一步的location必须按格式写(见[0])，这样才会使用rbd的 COW clone 功能。


```shell
# image format 2 support layering
rbd --image-format 2 import /tmp/ubuntu14.04.2.dsk $uuid

# Convert to raw image type
qemu-img convert -O raw rbd:$pool/$uuid rbd:$pool/$uuid

# Make Snapshot and protect it which is require by image clone in nova libvirt.
rbd --pool images snap create --snap snap $uuid
rbd --pool images snap protect --image $uuid --snap snap

# Create Image in Glance
glance image-create --id $uuid --name ubuntu14.04.2 --disk-format raw --container-format bare --is-public True --location rbd://$fsid/images/$uuid/snap
```

# REF

* [0] <https://github.com/openstack/nova/blob/4a02d9415f64e8d579d1b674d6d2efda902b01fa/nova/virt/libvirt/rbd_utils.py#L179>
* [1] <http://www.sebastien-han.fr/down/OpenStack%20_%20Ceph%20-%20Liberty.pdf>
* [2] <http://www.sebastien-han.fr/blog/2013/05/07/use-existing-rbd-images-and-put-it-into-glance/>
