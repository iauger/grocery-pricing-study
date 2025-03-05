import os
import requests
import base64
import time
from dotenv import load_dotenv, set_key, get_key
from datetime import datetime, timedelta

# Manually specify the exact path of the .env file
ENV_FILE = os.path.join(os.path.dirname(__file__), "kroger_client_info.env")

# Load the environment variables
load_dotenv(ENV_FILE)

# ✅ Fetch credentials
CLIENT_ID = get_key(ENV_FILE, "KROGER_CLIENT_ID")
CLIENT_SECRET = get_key(ENV_FILE, "KROGER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("❌ Missing Kroger API credentials in .env file!")

# ✅ Encode credentials for authorization
ENCODED_AUTH = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

# ✅ Define API Endpoints
TOKEN_URL = "https://api-ce.kroger.com/v1/connect/oauth2/token"
PRODUCTS_API_URL = "https://api-ce.kroger.com/v1/products"

# ✅ Token Storage (Cached in Memory)
TOKEN = None
TOKEN_EXPIRATION = None


# Function to get a new token if expired
def get_kroger_product_compact_token():
    global access_token, expiration

    # If token is missing or expired, request a new one
    if not access_token or datetime.utcnow() >= datetime.fromisoformat(expiration):
        print("🔄 Token expired or missing, requesting a new one...")

        # Encode credentials for Basic Auth
        encoded_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = "grant_type=client_credentials&scope=product.compact"

        # Request a new token
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            expires_in = response_data.get("expires_in", 1800)  # Default: 1800 seconds (30 min)
            expiration_time = datetime.now() + timedelta(seconds=expires_in)

            # ✅ Store updated tokens in GitHub Actions
            print("✅ New Token Retrieved! Updating GitHub Secrets...")
            os.system(f'echo "PRODUCT_COMPACT_ACCESS_TOKEN={access_token}" >> $GITHUB_ENV')
            os.system(f'echo "PRODUCT_COMPACT_ACCESS_TOKEN_EXPIRATION={expiration_time.isoformat()}" >> $GITHUB_ENV')

        else:
            print(f"❌ Failed to retrieve token: {response.json()}")

    return access_token

def search_kroger_products(location_id, search_terms=["Eggs", "Bread"], limit=50):
    """Search for products at a Kroger location with pagination."""
    token = get_kroger_product_compact_token()
    if not token:
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
                            product["locationId"] = location_id  # Ensure location ID is stored
                        all_products.extend(data["data"])

                        # ✅ Stop paginating if all products retrieved
                        total_results = data.get("meta", {}).get("pagination", {}).get("total", 0)
                        if len(all_products) >= total_results:
                            break

                        # ✅ Move to next batch
                        start += limit
                        time.sleep(1)  # Avoid rate-limiting
                    else:
                        break
                else:
                    print(f"❌ Error fetching products for '{term}': {response.json()}")
                    break
            except requests.RequestException as e:
                print(f"❌ Request error for '{term}' at location {location_id}: {e}")
                break

    return all_products


if __name__ == "__main__":
    test_location = "09700336"  # Example location ID
    test_results = search_kroger_products(test_location)
    if test_results:
        print(f"✅ Retrieved {len(test_results)} products for location {test_location}")
    else:
        print("⚠️ No products found.")
