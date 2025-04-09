import logging

from dataspine.config.token_provider import ExchangingTokenProvider, TokenProvider, AuthenticationStatus

try:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import ReadOnlyCredentials
except ImportError:
    boto3 = None
    SigV4Auth = None
    AWSRequest = None
    ReadOnlyCredentials = None

import base64
import json

class AwsTokenProvider(TokenProvider):
    """
    A class that provides AWS token exchange functionality for Dataspine.
    """
    token_exchange_endpoint: str
    exchanging_token_provider: ExchangingTokenProvider

    def __init__(self, token_exchange_endpoint: str, verify: bool, logger: logging.Logger):
        """
        Initializes the AwsTokenProvider with the token exchange endpoint and verification flag.

        :param token_exchange_endpoint: The endpoint for token exchange.
        :param verify: (DANGER) Flag indicating whether to verify SSL certificates. Do not set to False in production.
        :param logger: Logger instance for logging.
        """
        self.exchanging_token_provider = ExchangingTokenProvider(
            token_exchange_endpoint=token_exchange_endpoint,
            verify=verify,
            logger=logger,
            subject_token_type='urn:dataspine:params:oauth:grant-type:aws-iam-role-sigv4-token-exchange',
        )
        self.token_exchange_endpoint = token_exchange_endpoint

    def get_authentication_status(self) -> AuthenticationStatus:
        """
        Returns the authentication status of the token provider.

        :return: AuthenticationStatus object representing the current authentication status.
        """

        return self.exchanging_token_provider.get_authentication_status()

    def exchange_token(self, aws_creds: ReadOnlyCredentials, aws_region: str) -> None:
        """
        Exchanges the AWS credentials for a Dataspine token.

        :param aws_creds: AWS credentials object.
        :param aws_region: AWS region.
        :return: None
        """

        token = AwsTokenProvider.generate_sigv4_token(self.token_exchange_endpoint, aws_creds, aws_region)
        self.exchanging_token_provider.exchange_token(token)

    def exchange_token_from_env(self) -> None:
        """
        Starts the token exchange process by retrieving AWS credentials from the environment
        and exchanging them for a Dataspine token.

        This method uses the boto3 library to access AWS credentials and then calls
        `exchange_token` to perform the token exchange.
        It is assumed that the AWS credentials are set in the environment variables
        or through an AWS configuration file.

        :return: None

        Raises:
            ImportError: If boto3 is not installed.
            Exception: If there is an error during the token exchange process.
        """

        session = boto3.Session()
        credentials = session.get_credentials().get_frozen_credentials()
        self.exchange_token(credentials, "eu-central-1")

    @staticmethod
    def generate_sigv4_token(target_token_exchange_endpoint: str, aws_creds: ReadOnlyCredentials, aws_region: str) -> str:
        """
        Generates a base64-encoded JSON payload with SigV4-signed headers for
        GetCallerIdentity including a custom X-Dataspine-STS header
        to prevent replay attacks.

        Parameters:
            target_token_exchange_endpoint (str): Value for the X-Dataspine-STS header.
            aws_region (str): AWS region.
            aws_creds (ReadOnlyCredentials): AWS credentials object.

        Returns:
            str: base64-encoded JSON payload to be passed as token to the Dataspine STS Token Exchange.
        """
        service = "sts"
        url = "https://sts.amazonaws.com/"
        body = "Action=GetCallerIdentity&Version=2011-06-15"

        # Build headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Dataspine-STS": target_token_exchange_endpoint,
        }

        # Get credentials and sign the request
        request = AWSRequest(method="POST", url=url, data=body, headers=headers)
        SigV4Auth(aws_creds, service, aws_region).add_auth(request)

        payload = {
            "headers": dict(request.headers),
        }

        return base64.b64encode(json.dumps(payload).encode()).decode()