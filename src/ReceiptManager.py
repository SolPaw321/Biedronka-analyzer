from src.handlers.ProductCatalog import ProductCatalog
from src.handlers.prices import NominalPrices
from src.handlers.discounts import Discounts
from src.handlers.reciptStatus import BiedronkaReceiptStatusManager

class ReceiptManager:
    def __init__(self):
        pass

    def set_paragon_statuses_to_default(self) -> "ReceiptManager":
        BiedronkaReceiptStatusManager().initialize()
        return self

    def catalog_products(self) -> "ReceiptManager":
        pc = ProductCatalog()
        pc.execute()
        return self

    def price_history(self, create_charts: bool = False) -> "ReceiptManager":
        ph = NominalPrices()
        ph.execute()

        if create_charts:
            ph.create_charts()
        return self

    def discount_history(self) -> "ReceiptManager":
        dc = Discounts()
        dc.execute()
        return self