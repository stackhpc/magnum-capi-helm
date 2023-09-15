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
from unittest import mock

from magnum.common import exception
from magnum import objects
from magnum.tests.unit.db import base
from magnum.tests.unit.objects import utils as obj_utils

from magnum_capi_helm.common import app_creds
from magnum_capi_helm.common import ca_certificates
from magnum_capi_helm import conf
from magnum_capi_helm import driver
from magnum_capi_helm import helm
from magnum_capi_helm import kubernetes


CONF = conf.CONF


class ClusterAPIDriverTest(base.DbTestCase):
    def setUp(self):
        super(ClusterAPIDriverTest, self).setUp()
        self.driver = driver.Driver()
        self.cluster_obj = obj_utils.create_test_cluster(
            self.context,
            name="cluster_example_$A",
            master_flavor_id="flavor_small",
            flavor_id="flavor_medium",
            stack_id="cluster-example-a-111111111111",
        )
        # add in missing node group flavor
        for ng in self.cluster_obj.nodegroups:
            if ng.role != "master":
                ng.flavor_id = "flavor_medium"
                ng.save()

    def test_provides(self):
        self.assertEqual(
            [{"server_type": "vm", "os": "ubuntu", "coe": "kubernetes"}],
            self.driver.provides,
        )

    def test_update_cluster_status(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.update_cluster_status,
            self.context,
            self.cluster_obj,
        )

    def test_namespace(self):
        self.cluster_obj.project_id = "123-456F"

        namespace = self.driver._namespace(self.cluster_obj)

        self.assertEqual("magnum-123456f", namespace)

    def test_label_return_default(self):
        result = self.driver._label(self.cluster_obj, "foo", "bar")

        self.assertEqual("bar", result)

    def test_label_return_template(self):
        self.cluster_obj.cluster_template.labels = dict(foo=42)

        result = self.driver._label(self.cluster_obj, "foo", "bar")

        self.assertEqual("42", result)

    def test_label_return_cluster(self):
        self.cluster_obj.labels = dict(foo=41)
        self.cluster_obj.cluster_template.labels = dict(foo=42)

        result = self.driver._label(self.cluster_obj, "foo", "bar")

        self.assertEqual("41", result)

    def test_sanitized_name_no_suffix(self):
        self.assertEqual(
            "123-456fab", self.driver._sanitized_name("123-456Fab")
        )

    def test_sanitized_name_with_suffix(self):
        self.assertEqual(
            "123-456-fab-1-asdf",
            self.driver._sanitized_name("123-456_Fab!!_1!!", "asdf"),
        )
        self.assertEqual(
            "123-456-fab-1-asdf",
            self.driver._sanitized_name("123-456_Fab-1", "asdf"),
        )

    def test_get_kube_version_raises(self):
        mock_image = mock.Mock()
        mock_image.get.return_value = None
        mock_image.id = "myid"

        e = self.assertRaises(
            exception.MagnumException,
            self.driver._get_kube_version,
            mock_image,
        )

        self.assertEqual(
            "Image myid does not have a kube_version property.", str(e)
        )
        mock_image.get.assert_called_once_with("kube_version")

    def test_get_kube_version_works(self):
        mock_image = mock.Mock()
        mock_image.get.return_value = "v1.27.9"

        result = self.driver._get_kube_version(mock_image)

        self.assertEqual("1.27.9", result)
        mock_image.get.assert_called_once_with("kube_version")

    @mock.patch("magnum.common.clients.OpenStackClients")
    @mock.patch("magnum.api.utils.get_openstack_resource")
    def test_get_image_details(self, mock_get, mock_osc):
        mock_image = mock.Mock()
        mock_image.get.return_value = "v1.27.9"
        mock_image.id = "myid"
        mock_get.return_value = mock_image

        id, version = self.driver._get_image_details(
            self.context, "myimagename"
        )

        self.assertEqual("1.27.9", version)
        self.assertEqual("myid", id)
        mock_image.get.assert_called_once_with("kube_version")
        mock_get.assert_called_once_with(mock.ANY, "myimagename", "images")

    def test_get_chart_release_name_lenght(self):
        self.cluster_obj.stack_id = "foo"

        result = self.driver._get_chart_release_name(self.cluster_obj)

        self.assertEqual("foo", result)

    def test_generate_release_name_skip(self):
        self.cluster_obj.stack_id = "foo"
        self.driver._generate_release_name(self.cluster_obj)
        self.assertEqual("foo", self.cluster_obj.stack_id)

    def test_generate_release_name_generates(self):
        self.cluster_obj.stack_id = None
        self.cluster_obj.name = "a" * 77

        self.driver._generate_release_name(self.cluster_obj)
        first = self.cluster_obj.stack_id

        self.assertEqual(43, len(first))
        self.assertTrue(self.cluster_obj.name[:30] in first)

        self.cluster_obj.stack_id = None
        self.driver._generate_release_name(self.cluster_obj)
        second = self.cluster_obj.stack_id

        self.assertNotEqual(first, second)
        self.assertEqual(43, len(second))
        self.assertTrue(self.cluster_obj.name[:30] in second)

    def test_get_monitoring_enabled_from_template(self):
        self.cluster_obj.cluster_template.labels["monitoring_enabled"] = "true"

        result = self.driver._get_monitoring_enabled(self.cluster_obj)

        self.assertTrue(result)

    def test_get_kube_dash_enabled_from_template(self):
        self.cluster_obj.cluster_template.labels[
            "kube_dashboard_enabled"
        ] = "false"

        result = self.driver._get_kube_dash_enabled(self.cluster_obj)

        self.assertFalse(result)

    def test_get_chart_version_from_config(self):
        version = self.driver._get_chart_version(self.cluster_obj)

        self.assertEqual(CONF.capi_helm.default_helm_chart_version, version)

    def test_get_chart_version_from_template(self):
        self.cluster_obj.cluster_template.labels[
            "capi_helm_chart_version"
        ] = "1.42.0"

        version = self.driver._get_chart_version(self.cluster_obj)

        self.assertEqual("1.42.0", version)

    @mock.patch.object(driver.Driver, "_ensure_certificate_secrets")
    @mock.patch.object(driver.Driver, "_create_appcred_secret")
    @mock.patch.object(kubernetes.Client, "load")
    @mock.patch.object(driver.Driver, "_get_image_details")
    @mock.patch.object(helm.Client, "install_or_upgrade")
    def test_create_cluster(
        self,
        mock_install,
        mock_image,
        mock_load,
        mock_appcred,
        mock_certs,
    ):
        mock_image.return_value = ("imageid1", "1.27.4")
        mock_client = mock.MagicMock(spec=kubernetes.Client)
        mock_load.return_value = mock_client

        self.cluster_obj.keypair = "kp1"

        self.driver.create_cluster(self.context, self.cluster_obj, 10)

        app_cred_name = "cluster-example-a-111111111111-cloud-credentials"
        mock_install.assert_called_once_with(
            "cluster-example-a-111111111111",
            "openstack-cluster",
            {
                "kubernetesVersion": "1.27.4",
                "machineImageId": "imageid1",
                "cloudCredentialsSecretName": app_cred_name,
                "clusterNetworking": {
                    "internalNetwork": {"nodeCidr": "10.0.0.0/24"},
                    "dnsNameservers": ["8.8.1.1"],
                },
                "apiServer": {
                    "enableLoadBalancer": True,
                    "loadBalancerProvider": "amphora",
                },
                "controlPlane": {
                    "machineFlavor": "flavor_small",
                    "machineCount": 3,
                },
                "addons": {
                    "monitoring": {"enabled": False},
                    "kubernetesDashboard": {"enabled": True},
                    "ingress": {"enabled": False},
                },
                "nodeGroups": [
                    {
                        "name": "test-worker",
                        "machineFlavor": "flavor_medium",
                        "machineCount": 3,
                    }
                ],
                "machineSSHKeyName": "kp1",
            },
            repo=CONF.capi_helm.helm_chart_repo,
            version=CONF.capi_helm.default_helm_chart_version,
            namespace="magnum-fakeproject",
        )
        mock_client.ensure_namespace.assert_called_once_with(
            "magnum-fakeproject"
        )
        mock_appcred.assert_called_once_with(self.context, self.cluster_obj)
        mock_certs.assert_called_once_with(self.context, self.cluster_obj)

    @mock.patch.object(app_creds, "get_app_cred_string_data")
    @mock.patch.object(kubernetes.Client, "load")
    def test_create_appcred_secret(self, mock_load, mock_sd):
        mock_client = mock.MagicMock(spec=kubernetes.Client)
        mock_load.return_value = mock_client
        mock_sd.return_value = {"cacert": "ca", "clouds.yaml": "appcred"}

        self.driver._create_appcred_secret(self.context, self.cluster_obj)

        uuid = self.cluster_obj.uuid
        mock_client.apply_secret.assert_called_once_with(
            "cluster-example-a-111111111111-cloud-credentials",
            {
                "metadata": {
                    "labels": {
                        "magnum.openstack.org/project-id": "fake_project",
                        "magnum.openstack.org/user-id": "fake_user",
                        "magnum.openstack.org/cluster-uuid": uuid,
                    }
                },
                "stringData": {"cacert": "ca", "clouds.yaml": "appcred"},
            },
            "magnum-fakeproject",
        )

    @mock.patch.object(ca_certificates, "get_certificate_string_data")
    @mock.patch.object(driver.Driver, "_k8s_resource_labels")
    @mock.patch.object(kubernetes.Client, "load")
    def test_ensure_certificate_secrets(
        self, mock_load, mock_labels, mock_string_data
    ):
        mock_client = mock.MagicMock(spec=kubernetes.Client)
        mock_load.return_value = mock_client
        mock_labels.return_value = dict(foo="bar")
        mock_string_data.return_value = {
            "ca": {"tls.crt": "cert1", "tls.key": "key1"},
            "proxy": {"tls.crt": "cert2", "tls.key": "key2"},
        }

        self.driver._ensure_certificate_secrets(self.context, self.cluster_obj)

        mock_client.apply_secret.assert_has_calls(
            [
                mock.call(
                    "cluster-example-a-111111111111-ca",
                    {
                        "metadata": {"labels": {"foo": "bar"}},
                        "type": "cluster.x-k8s.io/secret",
                        "stringData": {"tls.crt": "cert1", "tls.key": "key1"},
                    },
                    "magnum-fakeproject",
                ),
                mock.call(
                    "cluster-example-a-111111111111-proxy",
                    {
                        "metadata": {"labels": {"foo": "bar"}},
                        "type": "cluster.x-k8s.io/secret",
                        "stringData": {"tls.crt": "cert2", "tls.key": "key2"},
                    },
                    "magnum-fakeproject",
                ),
            ]
        )

    @mock.patch.object(helm.Client, "uninstall_release")
    def test_delete_cluster(self, mock_uninstall):
        self.driver.delete_cluster(self.context, self.cluster_obj)

        mock_uninstall.assert_called_once_with(
            "cluster-example-a-111111111111", namespace="magnum-fakeproject"
        )

    def test_update_cluster(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.update_cluster,
            self.context,
            self.cluster_obj,
        )

    def test_resize_cluster(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.resize_cluster,
            self.context,
            self.cluster_obj,
            None,
            4,
            None,
        )

    def test_upgrade_cluster(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.upgrade_cluster,
            self.context,
            self.cluster_obj,
            self.cluster_obj.cluster_template,
            1,
            None,
        )

    def test_create_nodegroup(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.create_nodegroup,
            self.context,
            self.cluster_obj,
            objects.NodeGroup(),
        )

    def test_update_nodegroup(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.update_nodegroup,
            self.context,
            self.cluster_obj,
            objects.NodeGroup(),
        )

    def test_delete_nodegroup(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.delete_nodegroup,
            self.context,
            self.cluster_obj,
            objects.NodeGroup(),
        )

    def test_create_federation(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.create_federation,
            self.context,
            None,
        )

    def test_update_federation(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.update_federation,
            self.context,
            None,
        )

    def test_delete_federation(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.delete_federation,
            self.context,
            None,
        )
