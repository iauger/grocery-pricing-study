import os
import pandas as pd
from tracking import load_location_tracker, update_log
from fetch_product import fetch_products_in_batches
from kroger_api import get_kroger_product_compact_token
from data_processing import filter_products, save_to_csv

# ✅ Set up directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get `src/` directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Define file paths
PRODUCTS_FILE = os.path.join(DATA_DIR, "kroger_product_data.csv")
PRODUCT_API_LOG = os.path.join(DATA_DIR, "product_api_log.csv")

def main(batch_size=10):
    """Orchestrates the full Kroger data pipeline."""
    
    print("\n🚀 **Starting Kroger Data Pipeline** 🚀\n")

    # ✅ Step 1: Ensure API Token is Valid
    token = get_kroger_product_compact_token()
    if not token:
        print("❌ Failed to retrieve API token. Exiting...")
        return
    
    # ✅ Step 2: Initialize & Update Logs
    print("🔄 Loading tracker & checking logs...")
    load_location_tracker()
    update_log()  # Mark locations that need updates

    # ✅ Step 3: Fetch & Process Product Data
    print("📦 Fetching product data...")
    fetch_products_in_batches(batch_size=batch_size)

    # ✅ Step 4: Load & Filter Data
    print("🛠️ Processing and filtering product data...")
    if os.path.exists(PRODUCTS_FILE):
        df = pd.read_csv(PRODUCTS_FILE)
        filtered_df = filter_products(df)
        save_to_csv(filtered_df, PRODUCTS_FILE)
        print(f"✅ Processed and saved filtered product data to {PRODUCTS_FILE}")
    else:
        print("⚠️ No product data file found! Skipping filtering step.")

    # ✅ Step 5: Final Log Update
    update_log()
    
    print("\n🎉 **Pipeline Execution Complete!** 🎉")

if __name__ == "__main__":
    main(batch_size=2)  # Adjust batch size as needed
