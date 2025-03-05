import os
import requests
from requests.exceptions import RequestException
import base64
import time
from datetime import datetime, timedelta

# Load API credentials from GitHub Actions environment variables
CLIENT_ID = os.getenv("KROGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("❌ Missing Kroger API credentials in environment variables!")

# Encode credentials for API authentication
encoded_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

TOKEN_URL = "https://api-ce.kroger.com/v1/connect/oauth2/token"
HEADERS = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Function to get a new token if expired
def get_kroger_product_compact_token():
    """Retrieve or refresh the Kroger Product Compact API access token."""
    access_token = os.getenv("PRODUCT_COMPACT_ACCESS_TOKEN")
    expiration = os.getenv("PRODUCT_COMPACT_ACCESS_TOKEN_EXPIRATION")

    if not access_token or datetime.now() >= datetime.fromisoformat(expiration):
        print("🔄 Token expired or missing, requesting a new one...")

        response = requests.post(TOKEN_URL, headers=HEADERS, data="grant_type=client_credentials&scope=product.compact")
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            expires_in = response_data.get("expires_in", 1800)
            expiration_time = datetime.now() + timedelta(seconds=expires_in)

            # Save new tokens in environment for next steps
            os.environ["PRODUCT_COMPACT_ACCESS_TOKEN"] = access_token
            os.environ["PRODUCT_COMPACT_ACCESS_TOKEN_EXPIRATION"] = expiration_time.isoformat()

            print("✅ New Token Retrieved!")
        else:
            raise RuntimeError(f"❌ Failed to retrieve token: {response.json()}")

    return access_token

# ✅ Ensure API base URL is set
PRODUCTS_API_URL = "https://api-ce.kroger.com/v1/products"

def search_kroger_products(location_id, search_terms=["Eggs", "Bread"], limit=50):
    """Search for products at a Kroger location with pagination and enhanced error handling."""
    
    token = get_kroger_product_compact_token()
    if not token:
        print("❌ Failed to retrieve API token. Skipping product search.")
        return None

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    all_products = []
    max_pages = 5

    for term in search_terms:
        start = 1
        for page in range(max_pages):
            params = {
                "filter.term": term,
                "filter.locationId": location_id,
                "filter.limit": limit,
                "filter.start": start,
            }

            try:
                response = requests.get(PRODUCTS_API_URL, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    
                    if "data" in data:
                        for product in data["data"]:
                            product["locationId"] = location_id  # ✅ Ensure location ID is stored
                        all_products.extend(data["data"])

                        # ✅ Check pagination limits
                        total_results = data.get("meta", {}).get("pagination", {}).get("total", 0)
                        if len(all_products) >= total_results or len(data["data"]) < limit:
                            break  # Stop pagination if we've fetched all results

                        # ✅ Move to next batch
                        start += limit
                        time.sleep(1)  # Prevent rate-limiting
                    else:
                        print(f"⚠️ No more products found for '{term}' at location {location_id}.")
                        break
                else:
                    print(f"❌ API Error ({response.status_code}) fetching '{term}': {response.json()}")
                    break

            except RequestException as e:
                print(f"❌ Network error while fetching '{term}' at location {location_id}: {e}")
                break  # Exit loop on request failure

    return all_products


