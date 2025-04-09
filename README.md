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
from dataspine.config.config_loader import ConfigLoader

config_loader = ConfigLoader().load()
config_loader.auth_type = "aws-token-exchange"
config = config_loader.build()

authentication_status = config.token_provider.get_authentication_status()
print(authentication_status.last_valid_token)
```

## Requirements
- Python 3.8+
- httpx, pydantic, and other listed dependencies in pyproject.toml

## Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.