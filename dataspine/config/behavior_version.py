from enum import Enum

class BehaviorVersion(Enum):
    """
    BehaviorVersion Enum class for different behavior versions.
    """
    V20250120 = 'V20050120'

def latest() -> BehaviorVersion:
    """
    Returns the latest behavior version.

    :return: BehaviorVersion object representing the latest version.
    """
    return BehaviorVersion.V20250120
