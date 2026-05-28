===================
Configuration Guide
===================

For complete reference of configuration options for this driver used in
magnum.conf plesese refer to:

.. toctree::
   :maxdepth: 1

   Configuration Reference <config-reference>


Features
========

The driver currently supports create, delete and upgrade operations as well
as updates to node groups and their sizes.

The Kubernetes versions against which the CAPI Helm charts are currently being
tested can be found `here <https://github.com/azimuth-cloud/capi-helm-charts/blob/main/.github/workflows/ensure-capi-images.yaml#L9>`__.

The driver respects the following cluster and template properties:

* image_id
* keypair
* fixed_network, fixed_subnet (if missing, a new one is created
  with CIDR: 10.0.0.0/24)
* external_network_id
* dns_nameserver

The driver supports the following labels:



+-----------------------------------+---------------------+
| Label                             | Default             |
+===================================+=====================+
| monitoring_enabled                | false               |
|                                   |                     |
+-----------------------------------+---------------------+
| kube_dashboard_enabled            | true                |
|                                   |                     |
+-----------------------------------+---------------------+
| fixed_subnet_cidr                 | 10.0.0.0/24         |
+-----------------------------------+---------------------+
| extra_network_name                | empty               |
+-----------------------------------+---------------------+
| capi_helm_chart_version           | 0.10.1              |
| (see bellow for additional info)  |                     |
+-----------------------------------+---------------------+
| etcd_blockdevice_size             | 0                   |
+-----------------------------------+---------------------+
| etcd_blockdevice_type             | volume              |
|                                   |                     |
+-----------------------------------+---------------------+
| etcd_blockdevice_volume_az        | ""                  |
+-----------------------------------+---------------------+
| etcd_volume_size                  | 0                   |
+-----------------------------------+---------------------+
| etcd_volume_type                  | ""                  |
+-----------------------------------+---------------------+
| csi_cinder_availability_zone      | ""                  |
+-----------------------------------+---------------------+
| csi_cinder_reclaim_policy         | Delete              |
|                                   |                     |
+-----------------------------------+---------------------+
| csi_cinder_fstype                 | ext4                |
+-----------------------------------+---------------------+
| csi_cinder_allow_volume_expansion | True                |
|                                   |                     |
+-----------------------------------+---------------------+
| octavia_provider                  | amphora             |
|                                   | ovn                 |
+-----------------------------------+---------------------+
| octavia_lb_algorithm              | ROUND_ROBIN,        |
|                                   | SOURCE_IP_PORT if   |
|                                   | octavia_provider is |
|                                   | set to "ovn".       |
+-----------------------------------+---------------------+
| boot_volume_type                  | ""                  |
+-----------------------------------+---------------------+
| extra_network_name                | ""                  |
|                                   |                     |
+-----------------------------------+---------------------+



One config option requires a little bit more explanation:


* capi_helm_chart_version: can only be set via template property
  and CAN'T be overridden by cli options. If not set in cluster template,
  value is taken from magnum.config option default_helm_chart_version.



Tip & Tricks
=============

Currently, all clusters use the Calico CNI. While Cilium is also supported
in the Helm charts, it is not currently regularly tested.

We have found that cluster upgrades with ClusterAPI don't work well without
using a load balancer, even with a single node control plane, so we currently
ignore the "master-lb-enabled" flag.


