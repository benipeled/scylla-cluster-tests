# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright (c) 2021 ScyllaDB

from functools import cached_property
from typing import Optional, Any

from sdcm.provision.helpers.certificate import install_client_certificate
from sdcm.provision.scylla_yaml.auxiliaries import ScyllaYamlAttrBuilderBase, ClientEncryptionOptions, \
    ServerEncryptionOptions


class ScyllaYamlCertificateAttrBuilder(ScyllaYamlAttrBuilderBase):
    """
    Builds scylla yaml attributes regarding encryption
    """
    node: Any

    @cached_property
    def _ssl_files_path(self) -> str:
        install_client_certificate(self.node.remoter)
        return '/etc/scylla/ssl_conf'

    @property
    def client_encryption_options(self) -> Optional[ClientEncryptionOptions]:
        if not self.params.get('client_encrypt'):
            return None
        return ClientEncryptionOptions(
            enabled=True,
            certificate=self._ssl_files_path + '/client/test.crt',
            keyfile=self._ssl_files_path + '/client/test.key',
            truststore=self._ssl_files_path + '/client/catest.pem',
        )

    @property
    def server_encryption_options(self) -> Optional[ServerEncryptionOptions]:
        if not self.params.get('internode_encryption') or not self.params.get('server_encrypt'):
            return None
        return ServerEncryptionOptions(
            internode_encryption=self.params.get('internode_encryption'),
            certificate=self._ssl_files_path + '/db.crt',
            keyfile=self._ssl_files_path + '/db.key',
            truststore=self._ssl_files_path + '/cadb.pem',
        )
