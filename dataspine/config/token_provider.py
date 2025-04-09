import logging
from dataclasses import dataclass
from typing import Optional, Union, Protocol

import requests


@dataclass
class TokenStatus:
    """
    Represents the status of a token.

    :param status: The status of the token (e.g., 'Token').
    :param last_valid_token: The last valid token.
    :param is_refreshing: Indicates whether the token is currently being refreshed.
    :param last_error: Optional error that occurred during token exchange.
    """
    status: str  # 'Token'
    last_valid_token: str
    is_refreshing: bool
    last_error: Optional["AuthenticationError"] = None

@dataclass
class UnauthorizedStatus:
    """
    Represents the status when authentication is unauthorized.

    :param status: The status of the authentication (e.g., 'Unauthorized').
    """
    status: str  # 'Unauthorized'

"""
Represents the status of authentication.
This can be either a valid token status or an unauthorized status.
"""
AuthenticationStatus = Union[TokenStatus, UnauthorizedStatus]

class AuthenticationError(Exception):
    """
    Represents an authentication error.

    :param message: The error message.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.name = 'AuthenticationError'

class TokenProvider(Protocol):
    """
    A protocol for token providers.
    """
    def get_authentication_status(self) -> AuthenticationStatus:
        """
        Returns the authentication status of the token provider.

        :return: AuthenticationStatus object representing the current authentication status.
        """
        ...

class ExchangingTokenProvider(TokenProvider):
    """
    A class that provides token exchange functionality for Dataspine.

    :param token_exchange_endpoint: The endpoint for token exchange.
    :param verify: (DANGER) Flag indicating whether to verify SSL certificates. Do not set to False in production.
    :param logger: Logger instance for logging.
    :param subject_token_type: The type of the subject token. Default is 'urn:ietf:params:oauth:token-type:id_token'.
    """
    def __init__(self, token_exchange_endpoint: str, verify: bool, logger: logging.Logger, subject_token_type: Optional[str] = 'urn:ietf:params:oauth:token-type:id_token'):
        self.token_exchange_endpoint = token_exchange_endpoint
        self.logger = logger
        self.token: Optional[AuthenticationStatus] = None
        self.subject_token_type: str = subject_token_type
        self.verify = verify

    def get_authentication_status(self) -> AuthenticationStatus:
        """
        Returns the authentication status of the token provider.

        :return: AuthenticationStatus object representing the current authentication status.
        """
        return self.token if self.token else UnauthorizedStatus(status='Unauthorized')

    def exchange_token(self, input_token: str) -> None:
        """
        Exchanges the input token for a Dataspine token.

        :param input_token: The input token to be exchanged.
        :return: None
        """
        params = {
            'subject_token': input_token,
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'subject_token_type': self.subject_token_type,
        }
        try:
            exchange_url = self.token_exchange_endpoint + '/token'
            response = requests.post(exchange_url, params=params, verify=self.verify)
            response.raise_for_status()
            data = response.json()
            self.logger.debug(data)
            self.token = TokenStatus(
                status='Token',
                last_valid_token=data['access_token'],
                is_refreshing=True
            )
        except Exception as err:
            self.logger.error(f"Error exchanging token: {err}")
            raise err

class InMemoryTokenProvider(TokenProvider):
    """
    A simple in-memory token provider for Dataspine.
    """

    def __init__(self, initial_token: Optional[str] = None):
        """
        Initializes the InMemoryTokenProvider with an optional initial token.

        :param initial_token:
        """
        self.token = initial_token

    def get_authentication_status(self) -> AuthenticationStatus:
        """
        Returns the authentication status of the token provider.

        :return: AuthenticationStatus object representing the current authentication status.
        """
        if self.token:
            return TokenStatus(
                status='Token',
                last_valid_token=self.token,
                is_refreshing=False
            )
        else:
            return UnauthorizedStatus(status='Unauthorized')

    def set_token(self, token: str) -> None:
        """
        Sets the token for the InMemoryTokenProvider.

        :param token: The token to be set.
        :return: None
        """
        self.token = token