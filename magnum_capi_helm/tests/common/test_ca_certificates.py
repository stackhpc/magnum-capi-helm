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
from unittest import mock

from magnum.common.x509 import operations as x509
from magnum.conductor.handlers.common import cert_manager

from magnum_capi_helm.common import ca_certificates
from magnum_capi_helm.tests import base


class TestCACerts(base.TestCase):
    @mock.patch.object(cert_manager, "get_cluster_magnum_cert")
    @mock.patch.object(cert_manager, "get_cluster_ca_certificate")
    @mock.patch.object(ca_certificates, "_decode_key")
    @mock.patch.object(ca_certificates, "_decode_cert")
    def test_ensure_certificate_secrets(
        self, mock_cert, mock_key, mock_ca, mock_mag
    ):
        mock_ca.side_effect = lambda cluster, context, cert="ca": cert
        mock_key.side_effect = lambda cert: f"key-{cert}"
        mock_cert.side_effect = lambda cert: f"cert-{cert}"
        mock_mag.return_value = "cert_mag"

        context = mock.MagicMock()
        cluster = mock.MagicMock()
        data = ca_certificates.get_certificate_string_data(context, cluster)

        self.assertEqual(
            {
                "ca": {"tls.crt": "cert-ca", "tls.key": "key-ca"},
                "etcd": {
                    "tls.crt": "cert-etcd",
                    "tls.key": "key-etcd",
                },
                "proxy": {
                    "tls.crt": "cert-front_proxy",
                    "tls.key": "key-front_proxy",
                },
                "sa": {
                    "tls.crt": "cert-cert_mag",
                    "tls.key": "key-cert_mag",
                },
            },
            data,
        )

        mock_mag.assert_called_once_with(cluster, context)
        self.assertEqual(
            [
                mock.call(cluster, context),
                mock.call(cluster, context, "etcd"),
                mock.call(cluster, context, "front_proxy"),
            ],
            mock_ca.call_args_list,
        )

    def test_decode_cert(self):
        mock_cert = mock.MagicMock()
        mock_cert.get_certificate.return_value = "cert"

        result = ca_certificates._decode_cert(mock_cert)

        self.assertEqual("cert", result)

    @mock.patch.object(x509, "decrypt_key")
    def test_decode_key(self, mock_decrypt):
        mock_cert = mock.MagicMock()
        mock_cert.get_private_key.return_value = "private"
        mock_cert.get_private_key_passphrase.return_value = "pass"
        mock_decrypt.return_value = "foo"

        result = ca_certificates._decode_key(mock_cert)

        self.assertEqual("foo", result)
        mock_decrypt.assert_called_once_with("private", "pass")
