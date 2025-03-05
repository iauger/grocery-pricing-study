import pandas as pd
from datetime import datetime
import os

import os

# Get absolute path of the current script (tracking.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  

# Move up to the src directory and set the data folder path
DATA_DIR = os.path.join(BASE_DIR, "data")

# Define correct file paths
location_file = os.path.join(DATA_DIR, "kroger_locations.csv")
product_api_log = os.path.join(DATA_DIR, "product_api_log.csv")

print(f"📂 Looking for location file in: {location_file}")
print(f"📂 Looking for product log in: {product_api_log}")

# Ensure 'data' folder exists
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"❌ Data directory is missing: {DATA_DIR}")

# Ensure 'kroger_locations.csv' exists
if not os.path.exists(location_file):
    raise FileNotFoundError(f"❌ Missing location file: {location_file}")

# Ensure 'product_api_log.csv' exists
if not os.path.exists(product_api_log):
    print("⚠️ Tracker file missing! Creating new file...")
    pd.DataFrame(columns=["Location ID", "Last Retrieved Date", "Successful Calls", "Needs Data"]).to_csv(product_api_log, index=False)

def load_location_tracker():
    """Loads the location tracker and initializes missing locations."""
    if not os.path.exists(location_file):
        raise FileNotFoundError(f"❌ Missing location file: {location_file}")

    locations_df = pd.read_csv(location_file, dtype={"Location ID": str})
    location_ids = locations_df["Location ID"].astype(str).tolist()

    if os.path.exists(product_api_log):
        print("🔄 Loading existing product API tracker...")
        tracker_df = pd.read_csv(product_api_log, dtype={"Location ID": str})
        
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
        tracker_df.to_csv(product_api_log, index=False)

    return tracker_df

def update_tracker(location_id):
    """Updates the tracker after a successful API call."""
    tracker_df = pd.read_csv(product_api_log, dtype={"Location ID": str})

    # Update Last Retrieved Date and increment Successful Calls
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Last Retrieved Date"] = datetime.today().strftime("%Y-%m-%d")
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Successful Calls"] += 1

    tracker_df.to_csv(product_api_log, index=False)

def update_log():
    """Updates 'Needs Data' column based on the last retrieval date and removes duplicates."""
    tracker_df = pd.read_csv(product_api_log, dtype={"Location ID": str})

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
    tracker_df.to_csv(product_api_log, index=False)
    print("✅ 'Needs Data' column refreshed and duplicates removed.")
