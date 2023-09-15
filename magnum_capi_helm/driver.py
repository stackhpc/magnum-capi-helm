# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import re

from magnum.api import utils as api_utils
from magnum.common import clients
from magnum.common import exception
from magnum.common import short_id
from magnum.drivers.common import driver
from oslo_log import log as logging

from magnum_capi_helm.common import app_creds
from magnum_capi_helm.common import ca_certificates
from magnum_capi_helm import conf
from magnum_capi_helm import helm
from magnum_capi_helm import kubernetes

LOG = logging.getLogger(__name__)
CONF = conf.CONF


class Driver(driver.Driver):
    def __init__(self):
        self._helm_client = helm.Client()
        self.__k8s_client = None

    @property
    def _k8s_client(self):
        if not self.__k8s_client:
            self.__k8s_client = kubernetes.Client.load()
        return self.__k8s_client

    @property
    def provides(self):
        return [
            {
                "server_type": "vm",
                "os": "ubuntu",
                "coe": "kubernetes",
            },
        ]

    def update_cluster_status(self, context, cluster):
        raise NotImplementedError("don't support update_cluster_status yet")

    def _namespace(self, cluster):
        # We create clusters in a project-specific namespace
        # To generate the namespace, first sanitize the project id
        project_id = re.sub("[^a-z0-9]", "", cluster.project_id.lower())
        suffix = CONF.capi_helm.namespace_suffix
        return f"{suffix}-{project_id}"

    def _k8s_resource_labels(self, cluster):
        # TODO(johngarbutt) need to check these are safe labels
        return {
            "magnum.openstack.org/project-id": cluster.project_id[:63],
            "magnum.openstack.org/user-id": cluster.user_id[:63],
            "magnum.openstack.org/cluster-uuid": cluster.uuid[:63],
        }

    def _create_appcred_secret(self, context, cluster):
        string_data = app_creds.get_app_cred_string_data(context, cluster)
        name = self._get_app_cred_name(cluster)
        self._k8s_client.apply_secret(
            name,
            {
                "metadata": {"labels": self._k8s_resource_labels(cluster)},
                "stringData": string_data,
            },
            self._namespace(cluster),
        )

    def _ensure_certificate_secrets(self, context, cluster):
        # Magnum creates CA certs for each of the Kubernetes components that
        # must be trusted by the cluster
        # In particular, this is required for "openstack coe cluster config"
        # to work, as that doesn't communicate with the driver and instead
        # relies on the correct CA being trusted by the cluster

        # Cluster API looks for specific named secrets for each of the CAs,
        # and generates them if they don't exist, so we create them here
        # with the correct certificates in
        for (
            name,
            data,
        ) in ca_certificates.get_certificate_string_data().items():
            self._k8s_client.apply_secret(
                self._sanitized_name(
                    self._get_chart_release_name(cluster), name
                ),
                {
                    "metadata": {"labels": self._k8s_resource_labels(cluster)},
                    "type": "cluster.x-k8s.io/secret",
                    "stringData": data,
                },
                self._namespace(cluster),
            )

    def _label(self, cluster, key, default):
        all_labels = helm.mergeconcat(
            cluster.cluster_template.labels, cluster.labels
        )
        if not all_labels:
            return default
        raw = all_labels.get(key, default)
        # NOTE(johngarbutt): filtering untrusted user input
        return re.sub(r"[^a-zA-Z0-9\.\-\/ ]+", "", raw)

    def _get_chart_version(self, cluster):
        version = cluster.cluster_template.labels.get(
            "capi_helm_chart_version",
            CONF.capi_helm.default_helm_chart_version,
        )
        # NOTE(johngarbutt): filtering untrusted user input
        return re.sub(r"[^a-z0-9\.\-]+", "", version)

    def _sanitized_name(self, name, suffix=None):
        return re.sub(
            "[^a-z0-9]+",
            "-",
            (f"{name}-{suffix}" if suffix else name).lower(),
        )

    def _get_kube_version(self, image):
        # The image should have a property containing the Kubernetes version
        kube_version = image.get("kube_version")
        if not kube_version:
            raise exception.MagnumException(
                message=f"Image {image.id} does not "
                "have a kube_version property."
            )
        raw = kube_version.lstrip("v")
        # TODO(johngarbutt) more validation required?
        return re.sub(r"[^0-9\.]+", "", raw)

    def _get_image_details(self, context, image_identifier):
        osc = clients.OpenStackClients(context)
        image = api_utils.get_openstack_resource(
            osc.glance().images, image_identifier, "images"
        )
        return image.id, self._get_kube_version(image)

    def _get_app_cred_name(self, cluster):
        return self._sanitized_name(
            self._get_chart_release_name(cluster), "cloud-credentials"
        )

    def _get_monitoring_enabled(self, cluster):
        mon_label = self._label(cluster, "monitoring_enabled", "")
        # NOTE(mkjpryor) default of, like heat driver,
        # as requires cinder and takes a while
        return mon_label == "true"

    def _get_kube_dash_enabled(self, cluster):
        kube_dash_label = self._label(cluster, "kube_dashboard_enabled", "")
        # NOTE(mkjpryor) default on, like the heat driver
        return kube_dash_label != "false"

    def _update_helm_release(self, context, cluster):
        cluster_template = cluster.cluster_template
        image_id, kube_version = self._get_image_details(
            context, cluster_template.image_id
        )
        values = {
            "kubernetesVersion": kube_version,
            "machineImageId": image_id,
            "cloudCredentialsSecretName": self._get_app_cred_name(cluster),
            # TODO(johngarbutt): need to respect requested networks
            "clusterNetworking": {
                "internalNetwork": {
                    "nodeCidr": self._label(
                        cluster, "fixed_subnet_cidr", "10.0.0.0/24"
                    ),
                }
            },
            "apiServer": {
                "enableLoadBalancer": True,
                "loadBalancerProvider": self._label(
                    cluster, "octavia_provider", "amphora"
                ),
            },
            "controlPlane": {
                "machineFlavor": cluster.master_flavor_id,
                "machineCount": cluster.master_count,
            },
            "addons": {
                "monitoring": {
                    "enabled": self._get_monitoring_enabled(cluster)
                },
                "kubernetesDashboard": {
                    "enabled": self._get_kube_dash_enabled(cluster)
                },
                # TODO(mkjpryor): can't enable ingress until code exists to
                #                 remove the load balancer
                "ingress": {"enabled": False},
            },
            "nodeGroups": [
                {
                    "name": self._sanitized_name(ng.name),
                    "machineFlavor": ng.flavor_id,
                    "machineCount": ng.node_count,
                }
                for ng in cluster.nodegroups
                if ng.role != "master"
            ],
        }

        if cluster_template.dns_nameserver:
            dns_nameservers = cluster_template.dns_nameserver.split(",")
            values["clusterNetworking"]["dnsNameservers"] = dns_nameservers

        if cluster.keypair:
            values["machineSSHKeyName"] = cluster.keypair

        chart_version = self._get_chart_version(cluster)

        self._helm_client.install_or_upgrade(
            self._get_chart_release_name(cluster),
            CONF.capi_helm.helm_chart_name,
            values,
            repo=CONF.capi_helm.helm_chart_repo,
            version=chart_version,
            namespace=self._namespace(cluster),
        )

    def _generate_release_name(self, cluster):
        if cluster.stack_id:
            return

        # Make sure no duplicate names
        # by generating 12 character random id
        random_bit = short_id.generate_id()
        base_name = self._sanitized_name(cluster.name)
        # valid release names are 53 chars long
        # and stack_id is 12 characters
        # but we also use this to derive hostnames
        trimmed_name = base_name[:30]
        # Save the full name, so users can rename in the API
        cluster.stack_id = f"{trimmed_name}-{random_bit}".lower()
        # be sure to save this before we use it
        cluster.save()

    def _get_chart_release_name(self, cluster):
        return cluster.stack_id

    def create_cluster(self, context, cluster, cluster_create_timeout):
        LOG.info("Starting to create cluster %s", cluster.uuid)

        # we generate this name (on the initial create call only)
        # so we hit no issues with duplicate cluster names
        # and it makes renaming clusters in the API possible
        self._generate_release_name(cluster)

        self._k8s_client.ensure_namespace(self._namespace(cluster))
        self._create_appcred_secret(context, cluster)
        self._ensure_certificate_secrets(context, cluster)

        self._update_helm_release(context, cluster)

    def update_cluster(
        self, context, cluster, scale_manager=None, rollback=False
    ):
        raise NotImplementedError("don't support update yet")

    def delete_cluster(self, context, cluster):
        LOG.info("Starting to delete cluster %s", cluster.uuid)
        # Begin the deletion of the cluster resources by uninstalling the
        # Helm release
        # Note that this just marks the resources for deletion - it does not
        # wait for the resources to be deleted
        self._helm_client.uninstall_release(
            self._get_chart_release_name(cluster),
            namespace=self._namespace(cluster),
        )

    def resize_cluster(
        self,
        context,
        cluster,
        resize_manager,
        node_count,
        nodes_to_remove,
        nodegroup=None,
    ):
        raise NotImplementedError("don't support removing nodes this way yet")

    def upgrade_cluster(
        self,
        context,
        cluster,
        cluster_template,
        max_batch_size,
        nodegroup,
        scale_manager=None,
        rollback=False,
    ):
        raise NotImplementedError("don't support upgrade yet")

    def create_nodegroup(self, context, cluster, nodegroup):
        raise NotImplementedError("we don't support node groups yet")

    def update_nodegroup(self, context, cluster, nodegroup):
        raise NotImplementedError("we don't support node groups yet")

    def delete_nodegroup(self, context, cluster, nodegroup):
        raise NotImplementedError("we don't support node groups yet")

    def create_federation(self, context, federation):
        raise NotImplementedError("Will not implement 'create_federation'")

    def update_federation(self, context, federation):
        raise NotImplementedError("Will not implement 'update_federation'")

    def delete_federation(self, context, federation):
        raise NotImplementedError("Will not implement 'delete_federation'")
