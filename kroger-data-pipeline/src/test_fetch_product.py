import os
import pandas as pd
from fetch_product import fetch_and_filter_products, fetch_products_in_batches

# ✅ Set up directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the `src/` directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Define file paths
PRODUCTS_FILE = os.path.join(DATA_DIR, "kroger_product_data.csv")
LOCATION_FILE = os.path.join(DATA_DIR, "kroger_locations.csv")
PRODUCT_API_LOG = os.path.join(DATA_DIR, "product_api_log.csv")

# ✅ Test location ID for controlled testing
TEST_LOCATION_ID = "09700336"

def test_fetch_and_filter_products():
    """Test fetching and filtering products from API."""
    print("🔄 Testing fetch_and_filter_products()...")
    
    # Call function with a test location
    df = fetch_and_filter_products(TEST_LOCATION_ID)

    # Ensure function returned DataFrame
    assert isinstance(df, pd.DataFrame), "❌ fetch_and_filter_products() did not return a DataFrame"
    assert not df.empty, "❌ No data was retrieved!"

    # Check if essential columns exist
    required_columns = ["Product ID", "UPC", "Brand", "Description", "Category", "Location ID"]
    for col in required_columns:
        assert col in df.columns, f"❌ Missing column: {col}"
    
    print("✅ fetch_and_filter_products() Test Passed!")

def test_fetch_products_in_batches():
    """Test batch fetching of products."""
    print("🔄 Testing fetch_products_in_batches()...")
    
    # Run batch processing with a small batch size
    fetch_products_in_batches(batch_size=2)

    # Load updated product file to check data persistence
    df = pd.read_csv(PRODUCTS_FILE)

    assert not df.empty, "❌ fetch_products_in_batches() did not save any products!"
    
    print("✅ fetch_products_in_batches() Test Passed!")

if __name__ == "__main__":
    print("🔍 Running Tests for fetch_products.py...")
    test_fetch_and_filter_products()
    test_fetch_products_in_batches()
    print("🎉 All fetch_products.py tests passed!")
