from src.transactionDownloader import BiedronkaTransactionDownloader
from src.catalogTransactions import BiedronkaProductCatalog
from src.misc import PATHS

if __name__ == "__main__":
    downloader = BiedronkaTransactionDownloader(download_dir=PATHS.BIEDRONKA_DOWNLOADS)
    downloader.run()

    catalog = BiedronkaProductCatalog()
    catalog.catalog_products()