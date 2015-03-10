Title: Cinder V2 API
Date: 2015-3-10
Tags: Cinder,OpenStack
Category: OpenStack

cinder v2 api add more feature than v1, Like QoS. And the v1 is marked deprecated in juno and will be removed soon. ( may be in kilo).

# Enable the v2 in cinder

Change the following config. The v1 and v2 is enabled in default.

```ini
# DEPRECATED: Deploy v1 of the Cinder API. (boolean value)
#enable_v1_api=true

# Deploy v2 of the Cinder API. (boolean value)
#enable_v2_api=true

```

# Enable the cinder v2 api in nova

In current nova config ( juno ), the default config like below. Depend on `catalog_info` key, it use the v2 first. If v2 is not found, it will fall back to v1 version.

```ini
[cinder]

#
# Options defined in nova.volume.cinder
#

# Info to match when looking for cinder in the service
# catalog. Format is: separated values of the form:
# <service_type>:<service_name>:<endpoint_type> (string value)
#catalog_info=volumev2:cinderv2:publicURL

# Override service catalog lookup with template for cinder
# endpoint e.g. http://localhost:8776/v1/%(project_id)s
# (string value)
#endpoint_template=<None>

# Region name of this node (string value)
#os_region_name=<None>

# Number of cinderclient retries on failed http calls (integer
# value)
#http_retries=3

# Allow attach between instance and volume in different
# availability zones. (boolean value)
#cross_az_attach=true

```

You can just add the endpoint to the keystone to enable the cinder v2 api.

```bash
keystone service-create --name=cinderv2 --type=volumev2 \
  --description="Cinder Volume Service V2"
  
keystone endpoint-create \
  --service-id=the_service_id_above \
  --publicurl=http://controller:8776/v2/%\(tenant_id\)s \
  --internalurl=http://controller:8776/v2/%\(tenant_id\)s \
  --adminurl=http://controller:8776/v2/%\(tenant_id\)s
  
service cinder-scheduler restart
service cinder-api restart
```

# REF

* http://docs.openstack.org/havana/install-guide/install/apt/content/cinder-controller.html
* https://wiki.openstack.org/wiki/CinderAPIv2
