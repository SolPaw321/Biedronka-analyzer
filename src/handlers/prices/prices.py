from typing import ClassVar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

from src.misc import PATHS, FILES
from src.handlers.handlerBase import HandlerBase, StatusFields


class NominalPrices(HandlerBase):
    STATUS_FIELD: ClassVar[str] = StatusFields.priced

    def __init__(self):
        super().__init__()

    @staticmethod
    def __sanitize_filename(text: str) -> str:
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^\w]", "_", text)
        text = re.sub(r"_+", "_", text)
        return text.strip("_")

    def _find_data(self, receipt, existing_prices: dict[str, dict]) -> dict[str, dict]:
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
        return existing_prices

    def execute(self):
        existing_prices = self._load_existing(FILES.NOMINAL_PRICES)

        existing_prices = self._execute(PATHS.BIEDRONKA_DOWNLOAD, existing_prices)

        self.write_json(FILES.NOMINAL_PRICES, existing_prices)

    def create_charts(self):
        existing_prices = self._load_existing(FILES.NOMINAL_PRICES)

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
