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

from magnum.drivers.common import driver as common

from magnum_capi_helm import driver
from magnum_capi_helm.tests import base


class TestMagnumDriverLoads(base.TestCase):
    def test_get_driver(self):
        cluster_driver = common.Driver.get_driver("vm", "ubuntu", "kubernetes")
        self.assertIsInstance(cluster_driver, driver.Driver)

    def test_get_flatcar_driver(self):
        cluster_driver = common.Driver.get_driver(
            "vm", "flatcar", "kubernetes"
        )
        self.assertIsInstance(cluster_driver, driver.Driver)
