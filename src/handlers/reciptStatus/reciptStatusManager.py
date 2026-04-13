import json
from typing import ClassVar

from src.misc import PATHS, FILES


class StatusFields:
    cataloged = "cataloged"
    priced = "priced"
    discounted = "discounted"


    def to_list(self):
        results = []
        for attr_name in dir(self):
            if "__" not in attr_name and attr_name != "to_list":
                results.append(self.__getattribute__(attr_name))
        return results


class BiedronkaReceiptStatusManager:
    _instance: ClassVar = None
    _initialized: ClassVar[bool] = False

    def __init__(self) -> None:
        if self.__class__._initialized:
            return

        self.DOWNLOAD_DIR = PATHS.BIEDRONKA_DOWNLOAD
        self.STATUS_FILE = PATHS.DATA / FILES.RECEIPT_STATUS

        self._statuses: dict[str, dict[str, bool]] = {}

        self.__initialize_new_receipts()
        self.__normalize_status_fields()

    def __new__(cls) -> "BiedronkaReceiptStatusManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def __default_status() -> dict[str, bool]:
        return {
            status_field: False for status_field in StatusFields().to_list()
        }

    def __load_statuses(self) -> dict[str, dict[str, bool]]:
        if not self.STATUS_FILE.exists():
            return {}

        with open(self.STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def __save_statuses(self) -> None:
        with open(self.STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._statuses, f, ensure_ascii=False, indent=4)

    def __initialize_new_receipts(self) -> None:
        if not self._statuses:
            self._statuses = self.__load_statuses()

        existing_receipts = set(self._statuses.keys())
        new_receipts_count = 0

        for file_path in self.DOWNLOAD_DIR.glob("*.json"):
            receipt_name = file_path.name

            if receipt_name not in existing_receipts:
                self._statuses[receipt_name] = self.__default_status()
                new_receipts_count += 1

        self._statuses = dict(sorted(self._statuses.items()))
        self.__save_statuses()

        print(f"Updated receipt status file: {self.STATUS_FILE}")
        print(f"New tracked receipts: {new_receipts_count}")

    def __normalize_status_fields(self) -> None:
        loaded_statuses = self.__load_statuses()
        default_status = self.__default_status()

        normalized_statuses: dict[str, dict[str, bool]] = {}

        for filename, status in loaded_statuses.items():
            if not isinstance(status, dict):
                status = {}

            normalized_status = {}

            for field, default_value in default_status.items():
                if field in status:
                    normalized_status[field] = status[field]
                else:
                    normalized_status[field] = default_value

            normalized_statuses[filename] = normalized_status

        self._statuses = dict(sorted(normalized_statuses.items()))
        self.__save_statuses()

        print(f"Normalized receipt status fields in: {self.STATUS_FILE}")

    def initialize(self) -> None:
        self._statuses = {}

        for file_path in self.DOWNLOAD_DIR.glob("*.json"):
            self._statuses[file_path.name] = self.__default_status()

        self._statuses = dict(sorted(self._statuses.items()))
        self.__save_statuses()

        print(f"Initialized receipt status file: {self.STATUS_FILE}")
        print(f"Tracked receipts: {len(self._statuses)}")

    def set_receipt_status(self, receipt_name: str, status_field: str, value: bool) -> None:
        if not self._statuses:
            self._statuses = self.__load_statuses()

        if receipt_name not in self._statuses:
            raise KeyError(f"Receipt '{receipt_name}' does not exist in status file.")

        if status_field not in self.__default_status():
            raise KeyError(f"Status field '{status_field}' is not supported.")

        self._statuses[receipt_name][status_field] = value
        self.__save_statuses()

        print(f"Updated status '{status_field}' for receipt '{receipt_name}' to {value}")

    def get_receipt_status(self, receipt_name: str, status_field: str) -> bool:
        if not self._statuses:
            self._statuses = self.__load_statuses()

        if receipt_name not in self._statuses:
            raise KeyError(f"Receipt '{receipt_name}' does not exist in status file.")

        if status_field not in self.__default_status():
            raise KeyError(f"Status field '{status_field}' is not supported.")

        return self._statuses[receipt_name][status_field]
