# dataspine-client-python

A Python client for interacting with the Dataspine SaaS platform. This library simplifies authentication, data product management, and event-driven communication with Dataspine.

## Features

- ✅ Easy authentication based on Dataspine STS token exchange

## Installation

Work-in-Progress

## Documentation

Work-in-Progress

## Usage
```python
import uuid

from dataspine.config.config_loader import ConfigLoader
from dataspine.config.token_provider import UnauthorizedStatus

config_loader = ConfigLoader().load()
config_loader.auth_type = "aws-token-exchange"
config = config_loader.build()

region="<dataspine-region>"
application_id = uuid.UUID("<application-d>")
data_product_id = uuid.UUID("<data-product-id>")

authentication_status = config.token_provider_factory.create_token_provider(region, data_product_id, application_id).get_authentication_status()

if isinstance(authentication_status, UnauthorizedStatus):
    print("Unable to authenticate")
else:
    print(f"Dataspine token: {authentication_status.last_valid_token}")
```

## Requirements
- Python 3.8+
- httpx, pydantic, and other listed dependencies in pyproject.toml

## Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.