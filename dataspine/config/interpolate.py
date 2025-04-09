import base64
import uuid
from typing import Optional


def uuid_to_base32(u: uuid.UUID) -> str:
    """
    Convert a UUID to a base32 string representation.

    :param u: UUID to convert.
    :return: Base32 encoded string representation of the UUID.
    """

    return base64.b32encode(u.bytes).decode('utf-8').rstrip('=').lower()

def interpolate_component(
    endpoint_url: str,
    component: str,
) -> str:
    """
    Interpolates the endpoint URL with the specified component, application segment, and region.

    :param endpoint_url: The endpoint URL template.
    :param component: The component to be replaced in the URL (e.g., 'ing', 'out', 'api').
    :return: The interpolated endpoint URL.
    """
    return endpoint_url.replace("{{component}}", component)

def interpolate_region(
    endpoint_url: str,
    region: str
) -> str:
    """
    Interpolate the region into the endpoint URL.

    :param endpoint_url: Endpoint URL with placeholders.
    :param region: Dataspine region.
    :return: Formatted endpoint URL with the region.
    """

    return endpoint_url.replace("{{region}}", region)

def interpolate_endpoint_url(
    endpoint_url: str,
    region: str,
    data_product_id: uuid.UUID,
    application_id: Optional[uuid.UUID] = None
) -> str:
    """
    Interpolate the data product ID into the endpoint URL.

    :param endpoint_url: Endpoint URL with placeholders.
    :param region: Dataspine region.
    :param data_product_id: UUID of the data product.
    :param application_id: Optional application ID.
    :return: Formatted endpoint URL with the data product ID.
    """

    app_seg = ('-' + uuid_to_base32(application_id)) if application_id else ''
    data_product_segment = ('-' + uuid_to_base32(data_product_id)) if data_product_id else ''
    return endpoint_url.replace('{{data_product_id}}', data_product_segment).replace("{{application_id}}", app_seg).replace("{{region}}", region)

