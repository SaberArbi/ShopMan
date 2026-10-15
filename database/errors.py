"""Domain exceptions. Screens translate these with `t(e.key, **e.kwargs)`."""


class DomainError(Exception):
    """Base class. `key` is an i18n key; `kwargs` feed `str.format`."""
    key = "msg.error"
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__(self.key)


class BarcodeExists(DomainError):
    key = "err.barcode_exists"
    def __init__(self, barcode):
        super().__init__(barcode=barcode)


class ProductNotFound(DomainError):
    key = "err.product_not_found"


class SaleNotFound(DomainError):
    key = "err.sale_not_found"


class SaleAlreadyDeleted(DomainError):
    key = "err.sale_already_deleted"


class SaleNotDeleted(DomainError):
    key = "err.sale_not_deleted"


class NoActiveSales(DomainError):
    key = "err.no_active_sales"


class NoSales(DomainError):
    key = "err.no_sales"


class NoDeletedSales(DomainError):
    key = "err.no_deleted_sales"


class InsufficientStock(DomainError):
    key = "err.insufficient_stock"
    def __init__(self, available, required=None):
        super().__init__(available=available, required=required)