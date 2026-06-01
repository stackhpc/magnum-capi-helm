=======================
Configuration reference
=======================

The ``[capi_helm]`` section controls driver-level settings (Helm chart
location, flavour constraints, etc.).

The ``[capi_helm_cluster_labels]`` section controls the **default values**
for all supported cluster labels. Every option here can be overridden
per-cluster by the user via Magnum cluster (or template) labels.

.. show-options::
   :config-file: etc/oslo-config-generator/capi_helm.conf

