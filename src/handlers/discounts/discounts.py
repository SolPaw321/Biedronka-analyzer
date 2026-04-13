from typing import ClassVar

from src.misc import PATHS, FILES
from src.handlers.handlerBase import HandlerBase
from src.handlers.reciptStatus import StatusFields

class Discounts(HandlerBase):
    STATUS_FIELD: ClassVar[str] = StatusFields.discounted

    def __init__(self):
        super().__init__()
        
    def _find_data(self, receipt, results: dict[str, dict | int]) -> dict[str, dict | int]:
        date = receipt["header"][-1]["headerData"]["date"]

        body = receipt["body"]
        if not results.get("totalDiscount"):
            results["totalDiscount"] = 0

        for i in range(1, len(body)):
            if body[i].get("discountLine"):
                sellLine = body[i-1].get("sellLine")
                discountLine = body[i].get("discountLine")

                product_name = sellLine["name"]
                quantity = float(sellLine["quantity"].replace(",", "."))
                discount = discountLine["value"]
                base_value = discountLine["base"]
                percent = round(discount/base_value*100.0, 2)

                results["totalDiscount"] += discount
                print(results["totalDiscount"])

                if product_name not in results:
                    results[product_name] = {
                        "date": [date],
                        "quantity": [quantity],
                        "discount": [discount],
                        "percent": [percent],
                        "cumDiscount": discount
                    }
                elif date not in results[product_name]["date"]:
                    results[product_name]["date"].append(date)
                    results[product_name]["quantity"].append(quantity)
                    results[product_name]["discount"].append(discount)
                    results[product_name]["percent"].append(percent)
                    results[product_name]["cumDiscount"] += discount
        return results

    def execute(self) -> None:
        existing_discounts = self._load_existing(FILES.DISCOUNTS)

        existing_discounts = self._execute(PATHS.BIEDRONKA_DOWNLOAD, existing_discounts)

        self.write_json(FILES.DISCOUNTS, existing_discounts)
