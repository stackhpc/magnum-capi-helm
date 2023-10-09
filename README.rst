===============================
magnum-capi-helm
===============================

OpenStack Magnum driver using helm to create k8s clusters
with Cluster API.

The driver uses capi-helm-charts to create the
k8s resources needed to create a k8s cluster
using Cluster API, including various useful
add ons like a CNI and a monitoring stack.
https://github.com/stackhpc/capi-helm-charts

Note, the above helm charts are intended to be
a way to share a reference method to create K8s
on OpenStack. The charts are not expected or
indented to be specific to Magnum. The hope is
they can also be used by ArgoCD, Flux or Azimuth
to create k8s clusters on OpenStack.

Work on this driver started upstream aroun October 2021.
After failing to get merged during Bobcat,
we created this downstream repo as a stop gap to help
those wanting to use this driver now.
https://specs.openstack.org/openstack/magnum-specs/specs/bobcat/clusterapi-driver.html

Installation and Dependencies
=============================

If you install this python package within your Magnum virtual env,
it should be picked up by Magnum:::

  git clone https://github.com/stackhpc/magnum-capi-helm.git
  cd magnum-capi-helm
  pip install -e .

The driver requires access to a Cluster API management cluster.
For more information, please see:
https://cluster-api.sigs.k8s.io/user/quick-start

To access the above Cluster API management cluster,
you need to configure where the kubeconfig file
lives:::

  [capi_helm]
  kubeconfig_file = /etc/magnum/kubeconfig

To create a cluster, first you will need an image that
has been built to include kubernetes.
There are community maintained packer build pipelines here:
https://image-builder.sigs.k8s.io/capi/capi.html

The above image needs to have the correct os-distro
property set when uploaded to Glance. For example:::

  curl -fo ubuntu-focal-kube-v1.28.1-230831-1150.qcow2 'https://object.arcus.openstack.hpc.cam.ac.uk/azimuth-images/ubuntu-focal-kube-v1.28.1-230831-1150.qcow2?AWSAccessKeyId=c5bd0fa15bae4e08b305a52aac97c3a6&Expires=1725019898&Signature=%2FXW2ywkA%2FQ8bCUiJkiLCWBAf81M%3D'
  openstack image create ubuntu-focal-kube-v1.28.1 \
    --file ubuntu-focal-kube-v1.28.1-230831-1150.qcow2  \
    --disk-format qcow2 \
    --container-format bare \
    --public
  openstack image set ubuntu-focal-kube-v1.28.1 --os-distro capi-kubeadm-cloudinit --os-version 20.04
    openstack image set ubuntu-focal-kube-v1.28.1 \
        --os-distro capi-kubeadm-cloudinit

DevStack Setup
==============

Did you want to try this driver in DevStack?
Please try our setup script in this repo:
`devstack/contrib/new-devstack.sh`

The above devstack script includes creating k3s based
Cluster API management cluster.

Features
========

The driver currently supports, create, delete, upgrade and
updates to node groups and their sizes.

The CAPI helm charts are currently being tested
with K8s 1.26, 1.27 and 1.28:
https://github.com/stackhpc/capi-helm-charts/blob/main/.github/workflows/ensure-capi-images.yaml#L9

The driver respects the following cluster and template properties:

* image_id
* keypair
* fixed_network, fixed_subnet (if missing, new one is created)
* external_network_id
* dns_nameserver

The driver supports the following labels:

* monitoring_enabled: default is off, change to "true" to enable
* kube_dashboard_enabled: defalt is on, change to "false" to disable
* octavia_provider: default is "amphora"
* fixed_subnet_cidr: default is "10.0.0.0/24"
* extra_network_name: default is "", change to name of additional network,
  which can be useful if using Manila with the CephFS Native driver.

We have found upgrade with ClusterAPI doesn't work well without
using a loadbalancer, even with a single node control plane,
so we currently ignore the "master-lb-enabled" flag.

NOTE:
We are working in Cluster API provider OpenStack to add the ability
to store the etcd state on a cinder volume, separate from the root
disk. This is a big feature gap for clouds where most of your
root disks are on spinning disk Ceph, which is not fast enough
for etcd to operate correctly, but equally you don't have enough
ssd based Ceph to put all controller root disks on that Ceph:
https://github.com/kubernetes-sigs/cluster-api-provider-openstack/pull/1668

History
=======

The helm charts used by this driver started
out in August 2021 to build a template for
creating K8s on OpenStack using Cluster API.
We hope to find an upstream home for these
somewhere within OpenStack, ideally within
Magnum, but for now they are here:
https://github.com/stackhpc/capi-helm-charts

The helm charts have been in use in production
by Azimuth, since early 2022, to create
Kubernetes clusters on OpenStack:
https://github.com/stackhpc/azimuth

The hope is these helm charts can provide a common
well tested base that can be used in many different
ways to run Kubernetes on OpenStack. Be that automated
using helm directly, ArgoCD, Flux, Azimuth,
OpenStack Magnum and more.
Ideally we can eventually apply for Kubernetes
certification for these charts. The current helm chart
CI makes use of sonoboy smoke tests, and have been
manually tested to pass all conformance tests.

There has been an ongoing effort since October 2021 to create a Magnum
driver that makes use of the above helm charts, with a view to replace
the existing Heat based driver. However progress was severely delayed
getting the funding in place to do the work, which was finally confirmed
in August 2023.
You can see the upstream patches starting here:
https://review.opendev.org/c/openstack/magnum/+/815521

In early 2023 we discovered Vexhost had created
their own Cluster API Magnum driver, out of tree:
https://github.com/vexxhost/magnum-cluster-api

After subsequent PTG discussions, we agreed to continue this
effort to merge a driver upstream that makes use of cluster API,
with the above spec eventually getting merged for the Bobcat release.

The hope is that helm provides a better interface for per operator
additions to clusters, and should allow for helm to be updated to
support new Kubernetes versions, independently from the core
Magnum code.



