import json
from typing import ClassVar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

from src.misc import PATHS, FILES
from src.reciptStatus import BiedronkaReceiptStatusManager


class NominalPrices:
    STATUS_FIELD: ClassVar[str] = "priced"

    def __init__(self, status_manager: BiedronkaReceiptStatusManager):
        self.RECEIPTS_PATH = PATHS.BIEDRONKA_DOWNLOADS
        self.CATALOG_FILE = PATHS.CATALOG / FILES.CATALOG
        self.OUTPUT_FILE = PATHS.NOMINAL_PRICES / FILES.NOMINAL_PRICES

        self.status_manager = status_manager

    def __load_catalog(self) -> tuple[str]:
        if not self.CATALOG_FILE.exists():
            return tuple()

        existing_names = []

        with open(self.CATALOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    existing_names.append(name)

        return tuple(existing_names)

    def __load_existing_prices(self) -> dict[str, dict]:
        if not self.OUTPUT_FILE.exists():
            return {}

        with open(self.OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_prices = json.load(f)
        return existing_prices


    @staticmethod
    def __find_product_prices(receipt, existing_prices: dict[str, dict]):
        date = receipt["header"][-1]["headerData"]["date"]

        body = receipt["body"]
        for body_sample in body:
            sellLine = body_sample.get("sellLine")
            if sellLine:
                product_name = sellLine["name"]
                product_price = sellLine["price"]

                if product_name not in existing_prices:
                    existing_prices[product_name] = {
                        "date": [date],
                        "price": [product_price]
                    }
                else:
                    last_product_price = existing_prices[product_name]["price"][-1]

                    if product_price != last_product_price:
                        print(f"Price of product {product_name} has changed from {last_product_price} to {product_price}.")

                    existing_prices[product_name]["date"].append(date)
                    existing_prices[product_name]["price"].append(product_price)


    def nominal_prices(self):
        existing_prices = self.__load_existing_prices()

        for path in self.RECEIPTS_PATH.glob("*.json"):
            try:
                if self.status_manager.get_receipt_status(receipt_name=path.name, status_field=self.STATUS_FIELD):
                    continue

                with open(path, "r", encoding="utf-8") as f:
                    receipt = json.load(f)

                self.__find_product_prices(receipt, existing_prices)
                self.status_manager.set_receipt_status(
                    receipt_name=path.name,
                    status_field=self.STATUS_FIELD,
                    value=True
                )

            except Exception as e:
                print(f"Error while reading {path.name}: {e}")

        with open(self.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_prices, f, ensure_ascii=False, indent=4)

    @staticmethod
    def __sanitize_filename(text: str) -> str:
        """
        Zamienia znaki specjalne i białe znaki na "_".
        """
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^\w]", "_", text)
        text = re.sub(r"_+", "_", text)
        return text.strip("_")

    def create_charts(self):
        existing_prices = self.__load_existing_prices()

        for product_name in existing_prices:
            date = pd.to_datetime(existing_prices[product_name]["date"])
            price = np.array(existing_prices[product_name]["price"]) / 100.0

            fig = plt.figure(figsize=(10, 5))
            plt.plot(date, price, marker="o")

            plt.title(f"Price history: {product_name}")
            plt.ylabel("Price [zł]")
            plt.grid(True)

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
            plt.xticks(rotation=45)

            plt.tight_layout()

            plt.savefig(PATHS.NOMINAL_PRICES_CHARTS / self.__sanitize_filename(f"{product_name}.png"), dpi=300, bbox_inches="tight")
            plt.close(fig)
            print(f"Saved chart: {product_name}")

if __name__ == "__main__":
    manager = BiedronkaReceiptStatusManager()
    manager.initialize()

    prices = NominalPrices(manager)
    prices.nominal_prices()
    prices.create_charts()