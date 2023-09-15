# Copyright (c) 2023 VEXXHOST, Inc.
# Copyright (c) 2023 StackHPC
#
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
#
# This code is making use of the good work done here:
# https://github.com/vexxhost/magnum-cluster-api/blob/main/magnum_cluster_api/resources.py

from magnum.common.x509 import operations as x509
from magnum.conductor.handlers.common import cert_manager
from oslo_utils import encodeutils


def _decode_cert(cert):
    return encodeutils.safe_decode(cert.get_certificate())


def _decode_key(cert):
    key = x509.decrypt_key(
        cert.get_private_key(),
        cert.get_private_key_passphrase(),
    )
    return encodeutils.safe_decode(key)


def get_certificate_string_data(context, cluster):
    # Magnum creates CA certs for each of the Kubernetes components that
    # must be trusted by the cluster
    # In particular, this is required for "openstack coe cluster config"
    # to work, as that doesn't communicate with the driver and instead
    # relies on the correct CA being trusted by the cluster

    # Cluster API looks for specific named secrets for each of the CAs,
    # and generates them if they don't exist, so we create them here
    # with the correct certificates in
    certificates = {
        "ca": cert_manager.get_cluster_ca_certificate(cluster, context),
        "etcd": cert_manager.get_cluster_ca_certificate(
            cluster, context, "etcd"
        ),
        "proxy": cert_manager.get_cluster_ca_certificate(
            cluster, context, "front_proxy"
        ),
        "sa": cert_manager.get_cluster_magnum_cert(cluster, context),
    }
    certificate_string_data = {}
    for name, cert in certificates.items():
        certificate_string_data[name] = {
            "tls.crt": _decode_cert(cert),
            "tls.key": _decode_key(cert),
        }

    return certificate_string_data
