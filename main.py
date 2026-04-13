from src.ReceiptManager import ReceiptManager

if __name__ == "__main__":
    receipt_manager = ReceiptManager()

    receipt_manager.catalog_products()
    receipt_manager.price_history(create_charts=False)
    receipt_manager.discount_history()