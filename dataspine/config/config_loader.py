import logging
import uuid
from logging import Logger
from typing import Optional, Callable, Awaitable

from pydantic.v1 import BaseSettings

from dataspine.config.aws_token_provider import AwsTokenProviderFactory
from dataspine.config.behavior_version import BehaviorVersion, latest
from dataspine.config.config import Config, IngestConfig, OutletConfig, ApiConfig
from dataspine.config.interpolate import interpolate_component
from dataspine.config.token_provider import TokenProvider, InMemoryTokenProviderFactory, ExchangingTokenProviderFactory

DEFAULT_ENDPOINT_URL = "https://{{component}}{{application_id}}{{data_product_id}}.{{region}}.cloud.dataspine.tech"

InputTokenCallback = Callable[[], Awaitable[str]]

class Settings(BaseSettings):
    """
    Settings class for Dataspine configuration.

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
    def load() -> 'ConfigLoader':
        """
        Loads the configuration from environment variables and settings.

        :return: ConfigLoader instance with loaded settings.
        """
        config = ConfigLoader()
        settings = Settings()

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
        ingest_endpoint_url = interpolate_component(self.ingest_endpoint_url, 'ing')
        outlet_endpoint_url = interpolate_component(self.outlet_endpoint_url, 'out')
        api_endpoint_url = interpolate_component(self.api_endpoint_url, 'api')
        token_exchange_endpoint_url = interpolate_component(self.token_exchange_endpoint_url, 'sts')

        if self.auth_type == 'static-token':
            if not self.auth_token:
                raise ValueError("Auth token is required.")

            if not self.auth_token.startswith("static:"):
                raise ValueError("Only static auth tokens are supported.")

            token = self.auth_token.split(":")[1]
            token_provider_factory = InMemoryTokenProviderFactory(token)
        elif self.auth_type == 'token-exchange':
            token_provider_factory = ExchangingTokenProviderFactory(token_exchange_endpoint_url, self.verify_tls, self.logger)
        elif self.auth_type == 'aws-token-exchange':
            token_provider_factory = AwsTokenProviderFactory(token_exchange_endpoint_url, self.verify_tls, self.logger)
        else:
            token_provider_factory = InMemoryTokenProviderFactory()

        return Config(
            client_name=self.client_name,
            endpoint_url=self.endpoint_url,
            behavior_version=self.behavior_version,
            token_provider_factory=token_provider_factory,
            ingest=IngestConfig(ingest_endpoint_url),
            outlet=OutletConfig(outlet_endpoint_url),
            api=ApiConfig(api_endpoint_url),
            logger=self.logger,
        )
