"""Minimal placeholder for future trade specification contracts.

The formal request and validation models will be introduced in the domain and API
contract step so this module does not lock in business fields too early.
"""

from pydantic import BaseModel


class TradeSpecPlaceholder(BaseModel):
    """Placeholder model that preserves the package seam for later expansion."""

    pass
