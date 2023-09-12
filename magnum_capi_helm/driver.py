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

from oslo_log import log as logging

from magnum.drivers.common import driver

LOG = logging.getLogger(__name__)


class Driver(driver.Driver):
    @property
    def provides(self):
        return [
            {
                "server_type": "vm",
                # TODO(johngarbutt) OS list should probably come from config?
                "os": "ubuntu",
                "coe": "kubernetes",
            },
        ]

    def update_cluster_status(self, context, cluster):
        raise NotImplementedError("don't support update_cluster_status yet")

    def create_cluster(self, context, cluster, cluster_create_timeout):
        raise NotImplementedError("don't support create yet")

    def update_cluster(
        self, context, cluster, scale_manager=None, rollback=False
    ):
        raise NotImplementedError("don't support update yet")

    def delete_cluster(self, context, cluster):
        raise NotImplementedError("don't support delete yet")

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
