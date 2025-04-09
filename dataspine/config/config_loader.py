from logging import Logger

import logging
import uuid
from pydantic.v1 import BaseSettings
from typing import Optional, Callable, Awaitable

from dataspine.config.aws_token_provider import AwsTokenProvider
from dataspine.config.behavior_version import BehaviorVersion, latest
from dataspine.config.config import Config, IngestConfig, OutletConfig, ApiConfig, uuid_to_base32
from dataspine.config.token_provider import InMemoryTokenProvider, TokenProvider, ExchangingTokenProvider

DEFAULT_ENDPOINT_URL = "https://{{component}}{{application}}{{data_product_id}}.{{region}}.cloud.dataspine.tech"

InputTokenCallback = Callable[[], Awaitable[str]]

class Settings(BaseSettings):
    """
    Settings class for Dataspine configuration.

    :param region: AWS region.
    :param endpoint_url: Endpoint URL for the Dataspine service.
    :param token_exchange_endpoint: Token exchange endpoint URL.
    :param ingest_endpoint_url: Ingest endpoint URL.
    :param outlet_endpoint_url: Outlet endpoint URL.
    :param api_endpoint_url: API endpoint URL.
    :param client_name: Optional client name.
    :param application_id: Optional application ID.
    :param auth_token_source: Source of the authentication token.
    :param auth_type: Type of authentication (e.g., static-token, token-exchange).
    :param verify_tls: (DANGER) Flag to verify TLS certificates. Do not set to False in production.
    """

    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    token_exchange_endpoint: Optional[str] = None
    ingest_endpoint_url: Optional[str] = None
    outlet_endpoint_url: Optional[str] = None
    api_endpoint_url: Optional[str] = None
    client_name: Optional[str] = None
    application_id: Optional[uuid.UUID] = None
    auth_token_source: Optional[str] = None
    auth_type: Optional[str] = None
    verify_tls: Optional[bool] = None

    class Config:
        """
        Configuration for Pydantic settings.

        :param env_prefix: Prefix for environment variables.
        :param env_file: Path to the environment file.
        :param env_file_encoding: Encoding of the environment file.
        """
        env_prefix = "DATASPINE_"
        env_file = ".env"
        env_file_encoding = "utf-8"

class ConfigLoader:
    """
    Configuration loader for Dataspine.
    """
    logger: Logger
    behavior_version: BehaviorVersion

    endpoint_url: str = DEFAULT_ENDPOINT_URL
    ingest_endpoint_url: str = DEFAULT_ENDPOINT_URL
    outlet_endpoint_url: str = DEFAULT_ENDPOINT_URL
    api_endpoint_url: str = DEFAULT_ENDPOINT_URL
    token_exchange_endpoint_url: str = DEFAULT_ENDPOINT_URL
    verify_tls: bool = True

    auth_token: Optional[str] = None
    auth_type: Optional[str] = None
    region: Optional[str] = None
    token_provider: Optional[TokenProvider] = None
    client_name: Optional[str] = None
    application_id: Optional[uuid.UUID] = None

    def __init__(self, behavior_version: Optional[BehaviorVersion] = None):
        """
        Initializes the ConfigLoader with the specified behavior version.

        :param behavior_version: Behavior version for the Dataspine service.
        :type behavior_version: BehaviorVersion
        """
        self.behavior_version = behavior_version or latest()
        self.logger = logging.getLogger("dataspine")

    @staticmethod
    def interpolate_endpoint_url(
        endpoint_url: str,
        component: str,
        app_seg: str,
        region: str,
    ) -> str:
        """
        Interpolates the endpoint URL with the specified component, application segment, and region.

        :param endpoint_url: The endpoint URL template.
        :param component: The component to be replaced in the URL (e.g., 'ing', 'out', 'api').
        :param app_seg: The application segment to be replaced in the URL.
        :param region: The region to be replaced in the URL.
        :return: The interpolated endpoint URL.
        """
        return endpoint_url.replace("{{component}}", component).replace("{{application}}", app_seg).replace("{{region}}", region)

    @staticmethod
    def strip_data_product_id(
            endpoint_url: str,
    ) -> str:
        """
        Strips the data product ID from the endpoint URL.

        :param endpoint_url: The endpoint URL to be modified.
        :return: The modified endpoint URL without the data product ID.
        """

        return endpoint_url.replace("{{data_product_id}}", "")

    @staticmethod
    def load() -> 'ConfigLoader':
        """
        Loads the configuration from environment variables and settings.

        :return: ConfigLoader instance with loaded settings.
        """
        config = ConfigLoader()
        settings = Settings()

        config.region = settings.region

        if settings.endpoint_url:
            config.endpoint_url = settings.endpoint_url
            config.ingest_endpoint_url = settings.endpoint_url
            config.outlet_endpoint_url = settings.endpoint_url
            config.api_endpoint_url = settings.endpoint_url

        config.ingest_endpoint_url = settings.ingest_endpoint_url or config.ingest_endpoint_url
        config.outlet_endpoint_url = settings.outlet_endpoint_url or config.outlet_endpoint_url
        config.api_endpoint_url = settings.api_endpoint_url or config.api_endpoint_url
        config.token_exchange_endpoint_url = settings.token_exchange_endpoint or config.token_exchange_endpoint_url
        config.verify_tls = settings.verify_tls

        config.auth_token = settings.auth_token_source or config.auth_token
        config.auth_type = settings.auth_type or config.auth_type
        config.client_name = settings.client_name or config.client_name
        config.application_id = settings.application_id or config.application_id

        return config

    def build(self) -> Config:
        """
        Builds the configuration for Dataspine.

        :return: Config object with the configured settings.
        """
        app_seg = self.get_app_segment(self.application_id)

        if not self.region:
            raise ValueError("Region is required")

        ingest_endpoint_url = ConfigLoader.interpolate_endpoint_url(
            self.ingest_endpoint_url, 'ing', app_seg, self.region
        )

        outlet_endpoint_url = ConfigLoader.interpolate_endpoint_url(
            self.outlet_endpoint_url, 'out', app_seg, self.region
        )

        api_endpoint_url = ConfigLoader.interpolate_endpoint_url(
            self.api_endpoint_url, 'api', app_seg, self.region
        )

        token_exchange_endpoint_url = ConfigLoader.interpolate_endpoint_url(
            self.token_exchange_endpoint_url, 'sts', app_seg, self.region
        )
        token_exchange_endpoint_url = ConfigLoader.strip_data_product_id(token_exchange_endpoint_url)

        if self.auth_type == 'static-token':
            if not self.auth_token:
                raise ValueError("Auth token is required.")

            if not self.auth_token.startswith("static:"):
                raise ValueError("Only static auth tokens are supported.")

            token = self.auth_token.split(":")[1]
            token_provider = InMemoryTokenProvider(token)
        elif self.auth_type == 'token-exchange':
            token_provider = ExchangingTokenProvider(token_exchange_endpoint_url, self.verify_tls, self.logger)

            if self.auth_token:
                if not self.auth_token.startswith("static:"):
                    raise ValueError("Only static auth tokens are supported.")

                token = self.auth_token.split(":")[1]
                token_provider.exchange_token(token)
            else:
                logging.warning("Exchanging token provider configured, but no initial auth token provided. Needs to be provided manually.")
        elif self.auth_type == 'aws-token-exchange':
            token_provider = AwsTokenProvider(token_exchange_endpoint_url, self.verify_tls, self.logger)
            token_provider.exchange_token_from_env()
        else:
            token_provider = InMemoryTokenProvider()

        return Config(
            client_name=self.client_name,
            region=self.region,
            endpoint_url=self.endpoint_url,
            behavior_version=self.behavior_version,
            token_provider=token_provider,
            ingest=IngestConfig(ingest_endpoint_url),
            outlet=OutletConfig(outlet_endpoint_url),
            api=ApiConfig(api_endpoint_url),
            logger=self.logger,
        )

    @staticmethod
    def get_app_segment(application_id: Optional[uuid.UUID]) -> str:
        """
        Generates the application segment for the endpoint URL based on the application ID.

        :param application_id:
        :return:
        """
        return ('-' + uuid_to_base32(application_id)) if application_id else ''
