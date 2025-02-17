# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio

from azure.storage.blob.aio import BlobServiceClient
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from testcase import GlobalResourceGroupPreparer

from asyncblobtestcase import (
    AsyncBlobTestCase,
)

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '


SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


# --Test Class -----------------------------------------------------------------
class ServiceStatsTestAsync(AsyncBlobTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats['geo_replication'])

        self.assertEqual(stats['geo_replication']['status'], 'live')
        self.assertIsNotNone(stats['geo_replication']['last_sync_time'])

    def _assert_stats_unavailable(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats['geo_replication'])

        self.assertEqual(stats['geo_replication']['status'], 'unavailable')
        self.assertIsNone(stats['geo_replication']['last_sync_time'])

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda: SERVICE_LIVE_RESP_BODY

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda: SERVICE_UNAVAILABLE_RESP_BODY

    # --Test cases per service ---------------------------------------
    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyacrstorage', sku='Standard_RAGRS')
    @AsyncBlobTestCase.await_prepared_test
    async def test_blob_service_stats_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bs = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, transport=AiohttpTestTransport())
        # Act
        stats = await bs.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)

        # Assert
        self._assert_stats_default(stats)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyacrstorage', sku='Standard_RAGRS')
    @AsyncBlobTestCase.await_prepared_test
    async def test_blob_service_stats_when_unavailable_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bs = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, transport=AiohttpTestTransport())

        # Act
        stats = await bs.get_service_stats(raw_response_hook=self.override_response_body_with_unavailable_status)

        # Assert
        self._assert_stats_unavailable(stats)

# ------------------------------------------------------------------------------
