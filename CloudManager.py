import logging
import certifi
from pymongo import MongoClient
from datetime import datetime

# Primary cloud-based category predictor (may fail or return generic 'Other')
try:
    from Brain import predict_category
except Exception:
    predict_category = None

# Fallback local categorizer
try:
    from SmartCategorizer import categorize_item as fallback_categorize
except Exception:
    fallback_categorize = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudManager:
    def __init__(self):
        self.uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
        try:
            self.client = MongoClient(self.uri, tlsCAFile=certifi.where())
            # Use the DB/collection names your app reads from
            self.db = self.client["spendpal"]
            self.receipts_col = self.db["receipts"]
            logger.info("CloudManager connected to MongoDB: spendpal -> receipts")
        except Exception as e:
            logger.exception("CloudManager connection error")

    def process_and_save(self, items, total):
        """Categorize items and save a receipt doc to MongoDB.

        Uses `Brain.predict_category` when available; if it returns a generic
        'Other' or is unavailable, we fall back to `SmartCategorizer.categorize_item`.
        """
        categorized_items = []

        for name, price in items:
            main_cat = None
            sub_cat = None

            # Primary predictor
            if predict_category:
                try:
                    main_cat, sub_cat = predict_category(name)
                except Exception:
                    logger.exception("predict_category failed for '%s'", name)

            # If primary not available or returned a generic/empty result, try fallback
            if (not main_cat or main_cat == "Other") and fallback_categorize:
                try:
                    fb_main, fb_sub = fallback_categorize(name)
                    # Only adopt fallback if it gives something other than Other
                    if fb_main and fb_main != "Other":
                        main_cat, sub_cat = fb_main, fb_sub
                        logger.debug("Fallback categorizer assigned %s/%s for %s", fb_main, fb_sub, name)
                except Exception:
                    logger.exception("Fallback categorize failed for '%s'", name)

            # Final safety: force sensible defaults
            if not main_cat:
                main_cat = "Other"
            if not sub_cat:
                sub_cat = "General"

            categorized_items.append({
                "name": name,
                "price": price,
                "category": main_cat,
                "subcategory": sub_cat
            })

        receipt_doc = {
            "date": datetime.now(),
            "items": categorized_items,
            "total": total
        }

        try:
            self.receipts_col.insert_one(receipt_doc)
            logger.info("Successfully saved receipt to Cloud (items=%d, total=%s)", len(categorized_items), total)
        except Exception:
            logger.exception("Failed to save receipt to Cloud")

        return categorized_items