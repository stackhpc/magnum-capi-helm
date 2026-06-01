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

The driver supports cluster labels to customise cluster behaviour. The full
list of supported labels, their types, defaults, and descriptions is
maintained in the :doc:`Configuration Reference <config-reference>` under
the ``[capi_helm_cluster_labels]`` section.

Default values for all labels can be set operator-wide in ``magnum.conf``
under ``[capi_helm_cluster_labels]`` and overridden per cluster or template
by the user via Magnum labels.

.. note::

   ``capi_helm_chart_version`` can only be set via a cluster template label
   and cannot be overridden per cluster. When unset it falls back to
   ``[capi_helm] default_helm_chart_version``.



Tip & Tricks
=============

Currently, all clusters use the Calico CNI. While Cilium is also supported
in the Helm charts, it is not currently regularly tested.

We have found that cluster upgrades with ClusterAPI don't work well without
using a load balancer, even with a single node control plane, so we currently
ignore the "master-lb-enabled" flag.


