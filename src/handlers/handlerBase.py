from typing import ClassVar, Any, List, TypeVar
from abc import ABC, abstractmethod
from pathlib import Path
import json

from src.handlers.reciptStatus import BiedronkaReceiptStatusManager, StatusFields


T_Path = str | Path

T_JSONCoder_Iterable = list | tuple
T_JSONCoder_Dict = dict
T_JSONCoder_Values = str | int | float | bool | None
T_JSONCoder = T_JSONCoder_Dict | T_JSONCoder_Values | T_JSONCoder_Iterable

T = TypeVar('T')

class HandlerBase(ABC):
    STATUS_FIELD: ClassVar[str | None] = None

    _valid_statuses: StatusFields = StatusFields()
    _status_manager: BiedronkaReceiptStatusManager = BiedronkaReceiptStatusManager()

    @staticmethod
    def __validate_input_type(v: Any, t: Any):
        if not isinstance(v, t):
            raise TypeError(f"Type {type(v)} is unsupported. Use {t}.")

    @staticmethod
    def __validate_input_type_list(vs: List[Any], t: Any):
        if any([not isinstance(v, t) for v in vs]):
            raise TypeError(f"Not every element in 'vs' has supported type {t}.")

    @staticmethod
    def __validate_input_type_json_coder(values: T_JSONCoder):
        raise NotImplemented

    def read_json(self, path: T_Path) -> dict:
        self.__validate_input_type(path, T_Path)

        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def read_json_lines(self, path: T_Path) -> list:
        self.__validate_input_type(path, T_Path)

        path = Path(path)
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                lines.append(line.strip())
        return lines

    def write_json(self, path: T_Path, data: T_JSONCoder):
        self.__validate_input_type(path, T_Path)
        self.__validate_input_type(data, T_JSONCoder)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def write_json_lines(self, path: T_Path, data: List[T_JSONCoder]):
        self.__validate_input_type(path, T_Path)
        self.__validate_input_type(data, List)

        is_data_str = [not isinstance(x, str) for x in data]
        if any(is_data_str):
            not_data_str = []
            for i in range(len(is_data_str)):
                if not is_data_str[i] and is_data_str[i] is not None:
                    not_data_str.append(data[i])
            raise TypeError(f"Not all 'data' elements have 'str' type. Founded elements: {not_data_str}.")

        with open(path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(line + "\n")

    def set_status(self, receipt_name: str, status_field: str, value: bool):
        self.__validate_input_type(receipt_name, str)
        self.__validate_input_type(status_field, str)
        self.__validate_input_type(value, bool)

        self._status_manager.set_receipt_status(
            receipt_name=receipt_name,
            status_field=status_field,
            value=value
        )

    def get_status(self, receipt_name: str, status_field: str) -> bool:
        self.__validate_input_type(receipt_name, str)
        self.__validate_input_type(status_field, str)

        return self._status_manager.get_receipt_status(
            receipt_name=receipt_name,
            status_field=status_field
        )

    def _execute(self, download_path: T_Path, data: T) -> T:
        for path in download_path.glob("*.json"):
            try:
                if self.get_status(receipt_name=path.name, status_field=self.STATUS_FIELD):
                    continue

                receipt = self.read_json(path)

                self._find_data(receipt, data)
                self.set_status(
                    receipt_name=path.name,
                    status_field=self.STATUS_FIELD,
                    value=True
                )
            except Exception as e:
                print(f"Error while reading {path.name}: {e}")

        return data

    def _load_existing(self, path: T_Path) -> T_JSONCoder:
        if not path.exists():
            return {}
        return self.read_json(path)

    @abstractmethod
    def _find_data(self, receipt, results: T) -> T:
        pass


    @abstractmethod
    def execute(self) -> None:
        pass



