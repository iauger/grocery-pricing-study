import pandas as pd
from datetime import datetime
import os

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

print(f"📂 Looking for location file in: {LOCATION_FILE}")
print(f"📂 Looking for product log in: {PRODUCT_API_LOG}")

# Ensure 'data' folder exists
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"❌ Data directory is missing: {DATA_DIR}")

# Ensure 'kroger_locations.csv' exists
if not os.path.exists(LOCATION_FILE):
    raise FileNotFoundError(f"❌ Missing location file: {LOCATION_FILE}")

# Ensure 'PRODUCT_API_LOG.csv' exists
if not os.path.exists(PRODUCT_API_LOG):
    print("⚠️ Tracker file missing! Creating new file...")
    pd.DataFrame(columns=["Location ID", "Last Retrieved Date", "Successful Calls", "Needs Data"]).to_csv(PRODUCT_API_LOG, index=False)

def load_location_tracker():
    """Loads the location tracker and initializes missing locations."""
    if not os.path.exists(LOCATION_FILE):
        raise FileNotFoundError(f"❌ Missing location file: {LOCATION_FILE}")

    locations_df = pd.read_csv(LOCATION_FILE, dtype={"Location ID": str})
    location_ids = locations_df["Location ID"].astype(str).tolist()

    if os.path.exists(PRODUCT_API_LOG):
        print("🔄 Loading existing product API tracker...")
        tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})
        
        # Ensure column types are correct
        tracker_df["Last Retrieved Date"] = tracker_df["Last Retrieved Date"].astype(str)
        tracker_df["Successful Calls"] = tracker_df["Successful Calls"].astype(int)
        tracker_df["Needs Data"] = tracker_df["Needs Data"].astype(bool)
    else:
        print("🆕 Creating new product tracker file...")
        tracker_df = pd.DataFrame({
            "Location ID": location_ids,
            "Last Retrieved Date": "",
            "Successful Calls": 0,
            "Needs Data": True
        })
        tracker_df.to_csv(PRODUCT_API_LOG, index=False)

    return tracker_df

def update_tracker(location_id):
    """Updates the tracker after a successful API call."""
    tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})

    today_str = datetime.today().strftime("%Y-%m-%d")
    
    # ✅ Ensure we're updating the correct row
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Last Retrieved Date"] = today_str
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Successful Calls"] += 1

    print(f"📝 Updating tracker: {location_id} - {today_str}")

    tracker_df.to_csv(PRODUCT_API_LOG, index=False)  # ✅ Ensure changes are saved

def update_log():
    """Updates 'Needs Data' column based on the last retrieval date and removes duplicates."""
    tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})

    # ✅ Remove Duplicate Entries Based on 'Location ID'
    tracker_df = tracker_df.drop_duplicates(subset=["Location ID"], keep="last")

    def check_needs_data(row):
        last_call = str(row["Last Retrieved Date"])  # Convert NaN to string

        # ✅ Handle empty or invalid dates gracefully
        if last_call in ["", "nan", "NaT", "None"] or pd.isna(row["Last Retrieved Date"]):
            return True  # No previous retrieval, needs data

        try:
            last_call_date = datetime.strptime(last_call, "%Y-%m-%d")
            return (datetime.today() - last_call_date).days >= 7
        except ValueError:
            return True  # Handle invalid date format

    # ✅ Apply function to update 'Needs Data' column
    tracker_df["Needs Data"] = tracker_df.apply(check_needs_data, axis=1)

    # ✅ Save the updated tracker, ensuring no duplicates
    tracker_df.to_csv(PRODUCT_API_LOG, index=False)
    print("✅ 'Needs Data' column refreshed and duplicates removed.")
