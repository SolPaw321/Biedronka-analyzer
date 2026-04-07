from src.reciptStatus import BiedronkaReceiptStatusManager
from src.catalogTransactions import BiedronkaProductCatalog

if __name__ == "__main__":
    manager = BiedronkaReceiptStatusManager()
    manager.initialize_new_recipts()

    catalog = BiedronkaProductCatalog(manager)
    catalog.catalog_products()