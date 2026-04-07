import json

from src.misc import PATHS
from src.reciptStatus import BiedronkaReceiptStatusManager

class BiedronkaProductCatalog:
    STATUS_FIELD = "cataloged"

    def __init__(self, status_manager: BiedronkaReceiptStatusManager) -> None:
        self.DOWNLOAD_DIR = PATHS.BIEDRONKA_DOWNLOADS
        self.OUTPUT_FILE = PATHS.CATALOG / "catalog.txt"

        self.status_manager = status_manager

    @staticmethod
    def __find_product_names(receipt, results) -> None:
        body = receipt["body"]

        for body_sample in body:
            sell_line = body_sample.get("sellLine")
            if sell_line:
                product_name = sell_line["name"]
                results.add(product_name.strip())

    def load_existing_product_names(self) -> set[str]:
        if not self.OUTPUT_FILE.exists():
            return set()

        existing_names = set()

        with open(self.OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    existing_names.add(name)

        return existing_names

    def catalog_products(self) -> None:
        product_names = self.load_existing_product_names()
        existing_count = len(product_names)

        for path in self.DOWNLOAD_DIR.glob("*.json"):
            try:
                if self.status_manager.get_receipt_status(receipt_name=path.name, status_field=self.STATUS_FIELD):
                    continue

                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.__find_product_names(data, product_names)
                self.status_manager.set_receipt_status(
                    receipt_name=path.name,
                    status_field=self.STATUS_FIELD,
                    value=True
                )

            except Exception as e:
                print(f"Error while reading {path.name}: {e}")

        sorted_names = sorted(product_names)
        new_products_count = len(product_names) - existing_count

        with open(self.OUTPUT_FILE, "w", encoding="utf-8") as f:
            for name in sorted_names:
                f.write(name + "\n")

        print(f"Added {new_products_count} new product names.")
        print(f"Saved {len(sorted_names)} unique product names to: {self.OUTPUT_FILE}")
