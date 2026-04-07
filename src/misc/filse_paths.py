from pathlib import Path
from typing import ClassVar

from src.misc import PATHS

class Files:
    _instance: ClassVar["Files"] = None
    _initialized: ClassVar[bool] = False

    def __init__(self):
        if self.__class__._initialized:
            return

        self.CATALOG = PATHS.CATALOG / "catalog.txt"
        self.NOMINAL_PRICES = PATHS.NOMINAL_PRICES / "nominal_prices.json"
        self.RECEIPT_STATUS = PATHS.DATA / "receipt_status.json"

    def __new__(cls) -> "Files":
        """
        Create or return the single instance of the class.

        :return: The singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
