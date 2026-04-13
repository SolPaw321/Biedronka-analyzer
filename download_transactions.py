from src.handlers.transactionDownloader import BiedronkaTransactionDownloader
from src.misc import PATHS

if __name__ == "__main__":
    downloader = BiedronkaTransactionDownloader(download_dir=PATHS.BIEDRONKA_DOWNLOAD)
    downloader.run()

