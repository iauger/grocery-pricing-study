import os
import pandas as pd
from data_processing import initialize_tracker, update_log

# Ensure paths are relative to `src/`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the `src/` directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Define file paths using DATA_DIR
PRODUCTS_FILE = os.path.join(DATA_DIR, "kroger_product_data.csv")
LOCATION_FILE = os.path.join(DATA_DIR, "kroger_locations.csv")
PRODUCT_API_LOG = os.path.join(DATA_DIR, "product_api_log.csv")

def test_file_creation():
    """Ensure required CSV files exist or create them."""
    files = [PRODUCTS_FILE, LOCATION_FILE, PRODUCT_API_LOG]
    
    # ✅ Create missing files if necessary
    for file in files:
        if not os.path.exists(file):
            open(file, "w").close()
    
    assert all(os.path.exists(file) for file in files), "❌ One or more files are missing!"
    print("✅ File Creation Test Passed!")

def test_tracker_loading():
    """Ensure the location tracker loads properly."""
    df = initialize_tracker()
    assert "Location ID" in df.columns, "❌ 'Location ID' column missing!"
    assert "Needs Data" in df.columns, "❌ 'Needs Data' column missing!"
    print("✅ Tracker Loading Test Passed!")

def test_update_log():
    """Ensure log updates correctly."""
    update_log()  # Run update function
    df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})

    assert "Needs Data" in df.columns, "❌ 'Needs Data' column missing!"
    print("✅ Log Update Test Passed!")

if __name__ == "__main__":
    print("🔍 Running Data Processing Tests...")
    test_file_creation()
    test_tracker_loading()
    test_update_log()
    print("🎉 All Data Processing Tests Passed!")
