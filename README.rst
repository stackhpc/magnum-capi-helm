===============================
magnum-capi-helm
===============================

OpenStack Magnum driver using helm to create k8s clusters
with Cluster API.
The long stated aim of this driver is to merge
in upstream Magnum:
https://specs.openstack.org/openstack/magnum-specs/specs/bobcat/clusterapi-driver.html

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
