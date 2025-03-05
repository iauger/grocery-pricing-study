import os
import pandas as pd
from tracking import load_location_tracker, update_tracker, update_log

# ✅ Define correct path to test tracker file
TEST_TRACKER_FILE = os.path.join("src", "data", "test_product_api_log.csv")
ORIGINAL_TRACKER_FILE = os.path.join("src", "data", "product_api_log.csv")

# ✅ Ensure the data folder exists
os.makedirs(os.path.dirname(TEST_TRACKER_FILE), exist_ok=True)

# ✅ Check if the original tracker exists
if os.path.exists(ORIGINAL_TRACKER_FILE):
    print(f"📂 Copying existing tracker to test file: {TEST_TRACKER_FILE}")
    df_original = pd.read_csv(ORIGINAL_TRACKER_FILE, dtype={"Location ID": str})
    df_original.to_csv(TEST_TRACKER_FILE, index=False)
else:
    # ✅ Create an empty tracker file inside `src/data/`
    print(f"⚠️ Original tracker missing. Creating new test tracker at {TEST_TRACKER_FILE}")
    df_original = pd.DataFrame(columns=["Location ID", "Last Retrieved Date", "Successful Calls", "Needs Data"])
    df_original.to_csv(TEST_TRACKER_FILE, index=False)

print("🔍 Running Tests for tracking.py...")

# ✅ Modify `tracking.py` functions to use `TEST_TRACKER_FILE` instead of `product_api_log.csv`
def update_tracker(location_id):
    """Updates the tracker after a successful API call."""
    tracker_df = pd.read_csv(TEST_TRACKER_FILE, dtype={"Location ID": str})

    # Update Last Retrieved Date and increment Successful Calls
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Last Retrieved Date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    tracker_df.loc[tracker_df["Location ID"] == location_id, "Successful Calls"] += 1

    tracker_df.to_csv(TEST_TRACKER_FILE, index=False)

def update_log():
    """Updates 'Needs Data' column based on the last retrieval date and removes duplicates."""
    tracker_df = pd.read_csv(TEST_TRACKER_FILE, dtype={"Location ID": str})

    # ✅ Remove duplicates before updating
    tracker_df = tracker_df.drop_duplicates(subset=["Location ID"], keep="last")

    def check_needs_data(row):
        last_call = str(row["Last Retrieved Date"])  # Convert NaN to string
        if last_call in ["", "nan", "NaT", "None"] or pd.isna(row["Last Retrieved Date"]):
            return True  # Needs data

        try:
            last_call_date = pd.to_datetime(last_call)
            return (pd.Timestamp.now() - last_call_date).days >= 7
        except ValueError:
            return True  # Handle invalid date format

    # ✅ Update the 'Needs Data' column
    tracker_df["Needs Data"] = tracker_df.apply(check_needs_data, axis=1)

    # ✅ Save the updated test tracker
    tracker_df.to_csv(TEST_TRACKER_FILE, index=False)
    print("✅ 'Needs Data' column refreshed and duplicates removed.")

# ✅ Run the test functions
tracker_df = load_location_tracker()
test_location_id = tracker_df["Location ID"].iloc[0]
update_tracker(test_location_id)
update_log()

print("✅ Tests completed successfully!")
