import os
import pandas as pd


# Ensure paths are relative to `src/`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the `src/` directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Correct file paths
location_file = os.path.join(DATA_DIR, "kroger_locations.csv")
product_api_log = os.path.join(DATA_DIR, "product_api_log.csv")

# Check if files exist
print(f"🔍 Checking if files exist...")
print(f"📂 {location_file} exists:", os.path.exists(location_file))
print(f"📂 {product_api_log} exists:", os.path.exists(product_api_log))

# Check if files have data
if os.path.exists(location_file):
    df = pd.read_csv(location_file)
    print(f"📊 kroger_locations.csv - Rows: {len(df)}")

if os.path.exists(product_api_log):
    df = pd.read_csv(product_api_log)
    print(f"📊 product_api_log.csv - Rows: {len(df)}")

