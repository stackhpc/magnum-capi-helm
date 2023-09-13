# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg

capi_helm_group = cfg.OptGroup(
    name="capi_helm", title="Helm Cluster API Driver configuration"
)

capi_helm_opts = [
    cfg.StrOpt(
        "kubeconfig_file",
        default="",
        help=(
            "Path to a kubeconfig file for a management cluster,"
            "for use in the Cluster API driver. "
            "Defaults to the environment variable KUBECONFIG, "
            "or if not defined ~/.kube/config"
        ),
    )
]

CONF = cfg.CONF
CONF.register_group(capi_helm_group)
CONF.register_opts(capi_helm_opts, group=capi_helm_group)
