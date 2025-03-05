from dotenv import load_dotenv, get_key
import os

# # Manually specify the exact path of the .env file
# ENV_FILE = os.path.join(os.path.dirname(__file__), "kroger_client_info.env")

# # Load the environment variables
# load_dotenv(ENV_FILE)

# # Try retrieving the variables again
# CLIENT_ID = get_key(ENV_FILE, "KROGER_CLIENT_ID")
# CLIENT_SECRET = get_key(ENV_FILE, "KROGER_CLIENT_SECRET")

# print(f"CLIENT_ID: {CLIENT_ID}")  # Debugging
# print(f"CLIENT_SECRET: {CLIENT_SECRET}")  # Debugging

# # Raise error if credentials are missing
# if not CLIENT_ID or not CLIENT_SECRET:
#     raise ValueError("❌ Missing Kroger API credentials in .env file!")


data_dir = os.path.abspath("data")  # Get absolute path of the data directory
location_file = os.path.join(data_dir, "kroger_locations.csv")  # Construct full path

print(f"Checking for 'kroger_locations.csv' in: {data_dir}")

if os.path.exists(location_file):
    print("✅ File found:", location_file)
else:
    print("❌ File missing! Listing contents of data directory:")
    print(os.listdir(data_dir))