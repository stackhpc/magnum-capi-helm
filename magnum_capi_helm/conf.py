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
    ),
    cfg.StrOpt(
        "namespace_prefix",
        default="magnum",
        help=(
            "Resources for each openstack cluster are created in a "
            "separate namespace within the CAPI Management cluster "
            "specified by the configuration: [capi_helm]/kubeconfig_file "
            "You should modify this prefix when two magnum deployments "
            "want to share a single CAPI management cluster."
        ),
    ),
    cfg.StrOpt(
        "helm_chart_repo",
        default="https://stackhpc.github.io/capi-helm-charts",
        help=(
            "Reference to the helm chart repository for "
            "the cluster API driver. "
            "Note that if helm_chart_name starts with oci:// "
            "you will want this to set this to the empty string."
        ),
    ),
    cfg.StrOpt(
        "helm_chart_name",
        default="openstack-cluster",
        help=(
            "Name of the helm chart to use from the repo specified "
            "by the config: capi_driver.helm_chart_repo"
        ),
    ),
    cfg.StrOpt(
        "default_helm_chart_version",
        default="0.2.0",
        help=(
            "Version of the helm chart specified "
            "by the config: capi_driver.helm_chart_repo "
            "and capi_driver.helm_chart_name. "
            "A cluster label can override this."
        ),
    ),
    cfg.IntOpt(
        "minimum_flavor_ram",
        default=2048,
        help=("Minimum RAM for flavor used to " "create a Kubernetes node."),
    ),
    cfg.IntOpt(
        "minimum_flavor_vcpus",
        default=2,
        help=("Minimum VCPUS for flavor used to " "create a Kubernetes node."),
    ),
]

CONF = cfg.CONF
CONF.register_group(capi_helm_group)
CONF.register_opts(capi_helm_opts, group=capi_helm_group)
