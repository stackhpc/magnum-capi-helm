#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from magnum import objects
from magnum.tests.unit.db import base
from magnum.tests.unit.objects import utils as obj_utils

from magnum_capi_helm import driver


class ClusterAPIDriverTest(base.DbTestCase):
    def setUp(self):
        super(ClusterAPIDriverTest, self).setUp()
        self.driver = driver.Driver()
        self.cluster_obj = obj_utils.create_test_cluster(
            self.context,
            name="cluster_example_$A",
            master_flavor_id="flavor_small",
            flavor_id="flavor_medium",
        )

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

    def test_create_cluster(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.create_cluster,
            self.context,
            self.cluster_obj,
            cluster_create_timeout=10,
        )

    def test_delete_cluster(self):
        self.assertRaises(
            NotImplementedError,
            self.driver.delete_cluster,
            self.context,
            self.cluster_obj,
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
