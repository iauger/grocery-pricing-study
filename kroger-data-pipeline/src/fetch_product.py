import os
import sys
import time
import pandas as pd
import datetime
from kroger_api import search_kroger_products
from data_processing import filter_products, save_to_csv
from tracking import update_tracker, update_log

# ✅ Set up directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the `src/` directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Define file paths
PRODUCTS_FILE = os.path.join(DATA_DIR, "kroger_product_data.csv")
LOCATION_FILE = os.path.join(DATA_DIR, "kroger_locations.csv")
PRODUCT_API_LOG = os.path.join(DATA_DIR, "product_api_log.csv")

def fetch_and_filter_products(location_id):
    """Fetch products from Kroger API, filter relevant ones, and save to CSV."""
    
    # Call API (retrieves all products from Dairy & Bakery)
    product_results = search_kroger_products(location_id=location_id)
    
    if not product_results:
        print(f"⚠️ No results found for Location ID {location_id}")
        return None

    filtered_products = []

    if product_results:  # Ensure data exists
        for product in product_results:
            # Extract core product details
            product_id = product.get("productId", "Unknown")
            upc = product.get("upc", "Unknown")
            brand = product.get("brand", "Unknown")
            description = product.get("description", "Unknown")
            category = ", ".join(product.get("categories", []))  # Convert list to string
            location_id = product.get("locationId", "UNKNOWN_LOCATION")  # Ensure location ID is included
            
            # Extract pricing & availability
            price_info = product.get("items", [{}])[0]  # Get first item
            regular_price = price_info.get("price", {}).get("regular", 0)
            promo_price = price_info.get("price", {}).get("promo", 0)
            stock_level = price_info.get("inventory", {}).get("stockLevel", "Unknown")
            
            # Extract packaging details
            size = price_info.get("size", "Unknown")
            sold_by = price_info.get("soldBy", "Unknown")
            
            # Add date retrieved
            date_retrieved = datetime.date.today().strftime('%Y-%m-%d')
            
            # Store filtered product data
            filtered_products.append({
                "Product ID": product_id,
                "UPC": upc,
                "Brand": brand,
                "Description": description,
                "Category": category,
                "Location ID": location_id,
                "Regular Price": regular_price,
                "Promo Price": promo_price,
                "Stock Level": stock_level,
                "Size": size,
                "Sold By": sold_by,
                "Date Retrieved": date_retrieved
            })

    # ✅ Convert to DataFrame
    products_df = pd.DataFrame(filtered_products)

    # ✅ Apply Filtering Step (Using `filter_products`)
    filtered_df = filter_products(products_df)

    # ✅ Save to CSV with correct pathing
    save_to_csv(filtered_df, PRODUCTS_FILE)

    return filtered_df

def fetch_products_in_batches(batch_size=10):
    """Iterates over locations that need data and fetches products."""    
    # Refresh needs_data status before fetching
    update_log()
    
    tracker_df = pd.read_csv(PRODUCT_API_LOG, dtype={"Location ID": str})
    
    # Select only locations that need data
    locations_to_process = tracker_df[tracker_df["Needs Data"] == True]["Location ID"].tolist()
    
    total_locations = len(locations_to_process)
    print(f"{total_locations} require updates, this run will process {batch_size} when complete.")
    processed_count = 0

    for i, location_id in enumerate(locations_to_process, start=1):
        try:
            fetch_and_filter_products(location_id)  # Calls the API and saves data
            update_tracker(location_id)  # Update tracker after success
            processed_count += 1

            # Mental sanity feature so I don't constantly wonder how many records have been processed    
            sys.stdout.write(f"\r🔄 Progress: {i}/{batch_size} ZIP codes processed")
            sys.stdout.flush()
            
            # Stop after reaching batch limit
            if processed_count >= batch_size:
                break

            # Prevent rate limiting
            if processed_count < batch_size:
                time.sleep(2)
                
        except Exception as e:
            print(f"\n❌ Error processing {location_id}: {str(e)}")

    print(f"\n✅ Completed {processed_count} API calls in this run.")

if __name__ == "__main__":
    fetch_products_in_batches(batch_size=10)
