"""Flat `db` namespace — so screens can write `db.get_all_products()`.

Prefer this over importing the submodules directly.
"""
from .connection import DB_PATH, get_connection  # noqa: F401
from .errors import (  # noqa: F401
    DomainError, BarcodeExists, ProductNotFound, SaleNotFound,
    SaleAlreadyDeleted, SaleNotDeleted, NoActiveSales, NoSales,
    NoDeletedSales, InsufficientStock,
)
from .products import *   # noqa: F401,F403
from .sales import *      # noqa: F401,F403
from .reports import *    # noqa: F401,F403