from logging import Logger

import base64
import uuid
from dataclasses import dataclass
from typing import Optional

from dataspine.config.behavior_version import BehaviorVersion
from dataspine.config.token_provider import TokenProvider

def uuid_to_base32(u: uuid.UUID) -> str:
    """
    Convert a UUID to a base32 string representation.

    :param u: UUID to convert.
    :return: Base32 encoded string representation of the UUID.
    """

    return base64.b32encode(u.bytes).decode('utf-8').rstrip('=').lower()

def data_product_segment(data_product_id: uuid.UUID) -> str:
    """
    Generate a data product segment for the endpoint URL.

    :param data_product_id: UUID of the data product.
    :return: String representation of the data product segment.
    """

    return ('-' + uuid_to_base32(data_product_id)) if data_product_id else ''

@dataclass
class IngestConfig:
    """
    Ingest configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the ingest service.
    """
    endpoint_url: str

    def build_endpoint_url(self, data_product_id: uuid.UUID) -> str:
        """
        Build the endpoint URL for the ingest service.

        :param data_product_id: UUID of the data product.
        :return: Formatted endpoint URL with the data product ID.
        """
        return self.endpoint_url.replace('{{data_product_id}}', data_product_segment(data_product_id))

@dataclass
class OutletConfig:
    """
    Outlet configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the outlet service.
    """
    endpoint_url: str

    def build_endpoint_url(self, data_product_id: uuid.UUID) -> str:
        """
        Build the endpoint URL for the outlet service.

        :param data_product_id: UUID of the data product.
        :return: Formatted endpoint URL with the data product ID.
        """
        return self.endpoint_url.replace('{{data_product_id}}', data_product_segment(data_product_id))

@dataclass
class ApiConfig:
    """
    API configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the API service.
    """
    endpoint_url: str

    def build_endpoint_url(self, data_product_id: uuid.UUID) -> str:
        """
        Build the endpoint URL for the API service.

        :param data_product_id: UUID of the data product.
        :return: Formatted endpoint URL with the data product ID.
        """
        return self.endpoint_url.replace('{{data_product_id}}', data_product_segment(data_product_id))

@dataclass
class Config:
    """
    Configuration class for Dataspine.

    :param region: AWS region.
    :param endpoint_url: Endpoint URL for the Dataspine service.
    :param behavior_version: Behavior version for the Dataspine service.
    :param token_provider: Token provider for authentication.
    :param ingest: Ingest configuration.
    :param outlet: Outlet configuration.
    :param api: API configuration.
    :param logger: Logger instance for logging.
    :param client_name: Optional client name.
    :param application_id: Optional application ID.
    """
    region: str
    endpoint_url: str
    behavior_version: BehaviorVersion
    token_provider: TokenProvider
    ingest: IngestConfig
    outlet: OutletConfig
    api: ApiConfig
    logger: Logger
    client_name: Optional[str] = None
    application_id: Optional[uuid.UUID] = None
