import uuid
from dataclasses import dataclass
from logging import Logger
from typing import Optional

from dataspine.config.behavior_version import BehaviorVersion
from dataspine.config.interpolate import interpolate_endpoint_url
from dataspine.config.token_provider import TokenProviderFactory

@dataclass
class IngestConfig:
    """
    Ingest configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the ingest service.
    """
    endpoint_url: str

    def build_endpoint_url(self, region: str, data_product_id: uuid.UUID, application_id: Optional[uuid.UUID]) -> str:
        """
        Build the endpoint URL for the ingest service.

        :param region: Dataspine region.
        :param data_product_id: UUID of the data product.
        :param application_id: Optional application ID.
        :return: Formatted endpoint URL with the data product ID.
        """
        return interpolate_endpoint_url(self.endpoint_url, region, data_product_id, application_id)

@dataclass
class OutletConfig:
    """
    Outlet configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the outlet service.
    """
    endpoint_url: str

    def build_endpoint_url(self, region: str, data_product_id: uuid.UUID, application_id: Optional[uuid.UUID]) -> str:
        """
        Build the endpoint URL for the outlet service.

        :param region: Dataspine region.
        :param data_product_id: UUID of the data product.
        :param application_id: Optional application ID.
        :return: Formatted endpoint URL with the data product ID.
        """
        return interpolate_endpoint_url(self.endpoint_url, region, data_product_id, application_id)

@dataclass
class ApiConfig:
    """
    API configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the API service.
    """
    endpoint_url: str

    def build_endpoint_url(self, region: str, data_product_id: uuid.UUID, application_id: Optional[uuid.UUID]) -> str:
        """
        Build the endpoint URL for the API service.

        :param region: Dataspine region.
        :param data_product_id: UUID of the data product.
        :param application_id: Optional application ID.
        :return: Formatted endpoint URL with the data product ID.
        """
        return interpolate_endpoint_url(self.endpoint_url, region, data_product_id, application_id)

@dataclass
class Config:
    """
    Configuration class for Dataspine.

    :param endpoint_url: Endpoint URL for the Dataspine service.
    :param behavior_version: Behavior version for the Dataspine service.
    :param ingest: Ingest configuration.
    :param outlet: Outlet configuration.
    :param api: API configuration.
    :param logger: Logger instance for logging.
    :param client_name: Optional client name.
    """
    endpoint_url: str
    behavior_version: BehaviorVersion
    ingest: IngestConfig
    outlet: OutletConfig
    api: ApiConfig
    logger: Logger
    token_provider_factory: TokenProviderFactory
    client_name: Optional[str] = None
