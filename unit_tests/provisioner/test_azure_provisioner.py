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
# Copyright (c) 2022 ScyllaDB
import uuid

import pytest

from sdcm.keystore import KeyStore  # pylint: disable=import-error
from sdcm.provision.azure.provisioner import AzureProvisioner  # pylint: disable=import-error
from sdcm.provision.provisioner import InstanceDefinition, InstancePurpose  # pylint: disable=import-error


class TestProvisionScyllaInstanceAzureE2E:
    """this is rather e2e test - takes around 8 minutes (2m provisioning, 6 min cleanup with wait=True)"""

    @pytest.fixture(scope='session')
    def test_id(self):  # pylint: disable=no-self-use
        return f"unit-test-{str(uuid.uuid4())}"

    @pytest.fixture(scope='session')
    def definition(self):  # pylint: disable=no-self-use
        return InstanceDefinition(
            name="test-vm-1",
            purpose=InstancePurpose.SCYLLA,
            version="master:latest",
            size="Standard_D2s_v3",
            admin_name="tester",
            admin_public_key=KeyStore().get_ec2_ssh_key_pair().public_key.decode(),
            tags={'test-tag': 'test_value'}
        )

    @pytest.fixture(scope="function")
    def provisioner(self, test_id):  # pylint: disable=no-self-use
        return AzureProvisioner(test_id)

    def test_can_provision_scylla_vm(self, test_id, definition):  # pylint: disable=no-self-use
        provisioner = AzureProvisioner(test_id)
        region = "eastus"
        v_m = provisioner.create_virtual_machine(region, definition)
        assert v_m.name == definition.name
        assert v_m.purpose == InstancePurpose.SCYLLA
        assert v_m.region == region
        assert v_m.admin_name == definition.admin_name
        assert v_m.public_ip_address
        assert v_m.private_ip_address
        assert v_m.tags == definition.tags

        assert v_m == provisioner.list_virtual_machines()[0]

    @pytest.mark.timeout(2)
    def test_can_discover_existing_resources_for_test_id(self, provisioner, definition):  # pylint: disable=no-self-use
        """should read from cache instead creating anything - so should be fast (after provisioner initialized)"""
        region = "eastus"
        v_m = provisioner.create_virtual_machine(region, definition)
        assert v_m.name == definition.name
        assert v_m.purpose == InstancePurpose.SCYLLA
        assert v_m.region == region
        assert v_m.admin_name == definition.admin_name
        assert v_m.public_ip_address
        assert v_m.private_ip_address
        assert v_m.tags == definition.tags

        assert v_m == provisioner.list_virtual_machines()[0]

    def test_can_trigger_cleanup(self, test_id):  # pylint: disable=no-self-use
        provisioner = AzureProvisioner(test_id)
        provisioner.cleanup(wait=True)
        assert not provisioner.list_virtual_machines(), "failed cleaning up cache"
        # validating real cleanup - this takes most of the testing time (6mins)
        provisioner = AzureProvisioner(test_id)
        assert not provisioner.list_virtual_machines(), "failed cleaning up resources"