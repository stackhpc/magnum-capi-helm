===============================
magnum-capi-helm
===============================

OpenStack Magnum driver using helm to create k8s clusterswith Cluster API.

The helm charts started out in August 2021 to build a template for
creating K8s on OpenStack using Cluster API:
https://github.com/stackhpc/capi-helm-charts

The helm charts have been in use by Azimuth since early 2022 to create
Kubernetes clusters on OpenStack, in preference to previous Magnum
support:
https://github.com/stackhpc/azimuth

There has been an ongoing effort since October 2021 to create a Magnum
driver that makes use of the above helm charts, with a view to replace
the existing Heat based driver:
https://review.opendev.org/c/openstack/magnum/+/815521

In early 2023 we discovered Vexhost had created thier own Cluster API
Magnum driver, out of tree:
https://github.com/vexxhost/magnum-cluster-api

After PTG discussons, we wanted something that would merge upstream
and allowed for simple downstream modifications of templates, with
updates that are independent of Magnum releases. The helm abstraction
looked best able to deliver these aims, alongside being equaly useful
outside of Magnum, potentially operated using ArgoCD or similar.

Where possible, this driver is attempting to re-use logic from the
vexhost driver, in the hope of both drivers eventually sharing
more code, prehaps similar to the old cut and paste
openstack common of old. In particular, the vexhost driver had
already fixed some nasty problems around ensuring the existing
"coe credentials" API calls work with Cluster API, and
being able to generate appropriate application credentials for
use with both Cluster API Provider OpenStack (CAPO) and
Cloud Provider OpenStack, with appropriate ca cetificates
included.

* Free software: Apache license
* Source: https://github.com/stackhpc/magnum-capi-helm
