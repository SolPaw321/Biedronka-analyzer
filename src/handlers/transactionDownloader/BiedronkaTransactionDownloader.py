from pathlib import Path
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError

from src.misc import PATHS
from src.handlers.reciptStatus import BiedronkaReceiptStatusManager


class BiedronkaTransactionDownloader:
    def __init__(
        self,
        status_manager: BiedronkaReceiptStatusManager,
        download_dir: str | Path = PATHS.BIEDRONKA_DOWNLOAD,
        cdp_url: str = "http://127.0.0.1:9222",
    ) -> None:
        self.DOWNLOAD_DIR = Path(download_dir)
        self.cdp_url = cdp_url

        self.status_manager = status_manager

    @staticmethod
    def parse_possible_date(value):
        if not value:
            return None

        candidates = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d.%m.%Y %H:%M:%S",
        ]

        for fmt in candidates:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def show_latest_local_transaction(self) -> None:
        receipts = []

        for path in self.DOWNLOAD_DIR.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if data["header"][-1]["headerData"]["date"] is not None:
                    receipts.append(data)

            except Exception as e:
                print(e)

        if not receipts:
            print("No local JSON transactions found.")
            return

        latest = max(receipts, key=lambda x: x["header"][-1]["headerData"]["date"])

        print("Latest locally saved transaction:")
        print(f'Date:  {latest["header"][-1]["headerData"]["date"]}')

    def run(self) -> None:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(self.cdp_url)
            context = browser.contexts[0]
            page = context.pages[0]

            self.show_latest_local_transaction()
            input("Set the page with the transaction list and press Enter...")

            buttons = page.locator("text=JSON")
            count = buttons.count()
            print(f"Found JSON buttons: {count}")

            for i in range(count):
                try:
                    buttons = page.locator("text=JSON")
                    button = buttons.nth(i)

                    button.scroll_into_view_if_needed()

                    with page.expect_download(timeout=10000) as download_info:
                        button.click()

                    download = download_info.value
                    target = self.DOWNLOAD_DIR / download.suggested_filename
                    download.save_as(str(target))
                    print(f"[{i+1}/{count}] Saved: {target}")

                    page.wait_for_timeout(1000)

                except TimeoutError:
                    print(f"[{i+1}/{count}] No download detected after clicking")
                except Exception as e:
                    print(f"[{i+1}/{count}] Error: {e}")