from typing import ClassVar, TypeVar

from src.misc import PATHS, FILES
from src.handlers.handlerBase import HandlerBase, StatusFields

class ProductCatalog(HandlerBase):
    STATUS_FIELD: ClassVar[str] = StatusFields.cataloged

    def __init__(self) -> None:
        super().__init__()

    def _find_data(self, receipt, results: dict[str, list[str]]) -> dict[str, list[str]]:
        body = receipt["body"]

        for body_sample in body:
            sell_line = body_sample.get("sellLine")
            if sell_line:
                product_name = sell_line["name"]
                results["catalog"].append(product_name.strip())
        return results

    def execute(self) -> None:
        existing_catalog = self._load_existing(FILES.CATALOG)

        if "catalog" not in existing_catalog:
            existing_catalog["catalog"] = []

        existing_catalog = self._execute(PATHS.BIEDRONKA_DOWNLOAD, existing_catalog)

        existing_catalog["catalog"] = list(set(existing_catalog["catalog"]))

        self.write_json(FILES.CATALOG, existing_catalog)


