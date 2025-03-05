import pandas as pd
from datetime import datetime, timedelta
import os

# ✅ Set base directory dynamically
BASE_DIR = os.getenv("GITHUB_WORKSPACE", os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "kroger-data-pipeline", "src", "data")

# ✅ Update file paths
PRODUCTS_FILE = os.path.join(DATA_DIR, "kroger_product_data.csv")
LOCATION_FILE = os.path.join(DATA_DIR, "kroger_locations.csv")
PRODUCT_API_LOG = os.path.join(DATA_DIR, "product_api_log.csv")

# Ensure data folder exists in GitHub Actions runner
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"✅ Created missing data directory: {DATA_DIR}")

# ✅ Ensure the product data CSV exists (Creates empty file if missing)
if not os.path.exists(PRODUCTS_FILE):
    pd.DataFrame(columns=[
        "Product ID", "UPC", "Brand", "Description", "Category", "Location ID", 
        "Regular Price", "Promo Price", "Stock Level", "Size", "Sold By", "Date Retrieved"
    ]).to_csv(PRODUCTS_FILE, index=False)
    print(f"✅ Created new CSV file: {PRODUCTS_FILE}")


def initialize_tracker():
    """Initializes or loads the location tracking file."""
    locations_df = pd.read_csv(LOCATION_FILE, dtype={"Location ID": str})

    if os.path.exists(PRODUCT_API_LOG):
        print("🔄 Loading existing product API tracker...")
        tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})
    else:
        print("🆕 Creating new product tracker file...")
        tracker_df = pd.DataFrame({
            "Location ID": locations_df["Location ID"].astype(str),
            "Last Retrieved Date": "",
            "Successful Calls": 0,
            "Needs Data": True
        })
        tracker_df.to_csv(PRODUCT_API_LOG, index=False)
        print(f"✅ Created new tracker file: {PRODUCT_API_LOG}")

    return tracker_df


def update_tracker(location_id):
    """Updates the tracker after a successful API call."""
    tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})

    # ✅ Update Last Retrieved Date & Increment Successful Calls
    today_str = datetime.today().strftime("%Y-%m-%d")
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Last Retrieved Date"] = today_str
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Successful Calls"] += 1

    tracker_df.to_csv(PRODUCT_API_LOG, index=False)
    print(f"✅ Tracker updated for Location ID {location_id}")


def update_log():
    """Updates 'Needs Data' column based on last retrieval date and removes duplicates."""
    tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})

    # ✅ **Remove Duplicates**
    tracker_df = tracker_df.drop_duplicates(subset=["Location ID"], keep="last")

    # ✅ **Optimize Date Processing (Vectorized Approach)**
    tracker_df["Last Retrieved Date"] = pd.to_datetime(tracker_df["Last Retrieved Date"], errors="coerce")

    # ✅ **Set 'Needs Data' True if never retrieved OR 7+ days since last call**
    tracker_df["Needs Data"] = tracker_df["Last Retrieved Date"].isna() | \
                               (datetime.today() - tracker_df["Last Retrieved Date"]).dt.days >= 7

    # ✅ Save the cleaned tracker
    tracker_df.to_csv(PRODUCT_API_LOG, index=False)
    print("✅ 'Needs Data' column refreshed and duplicates removed.")


def filter_products(df):
    """Filter products based on relevant categories and keywords."""
    
    valid_categories = ["Dairy", "Bakery"]
    valid_keywords = ["egg", "bread"]

    return df[
        df["Category"].apply(lambda x: any(cat in x for cat in valid_categories)) &
        df["Description"].str.lower().apply(lambda x: any(kw in x for kw in valid_keywords))
    ]


def save_to_csv(df, filename):
    """Append DataFrame to CSV file or create new file if missing."""
    
    if df.empty:
        print("⚠️ No relevant products found, skipping file update.")
        return
    
    # ✅ Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(filename, index=False)
    print(f"✅ Filtered data saved to {filename}")
