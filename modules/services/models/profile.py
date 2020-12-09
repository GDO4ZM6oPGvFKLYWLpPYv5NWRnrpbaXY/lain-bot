from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Any

class Profile:
    """Represents a profile to be used to store extra data related to a service"""

    __slots__ = []

    @property
    def dict(self) -> Dict[str, Any]:
        return {}