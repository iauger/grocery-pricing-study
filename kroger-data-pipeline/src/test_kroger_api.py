from kroger_api import get_kroger_product_compact_token, search_kroger_products

def test_authentication():
    """Test if the API token retrieval works."""
    token = get_kroger_product_compact_token()
    assert token is not None, "❌ API Token retrieval failed!"
    assert isinstance(token, str), "❌ API Token should be a string!"
    print("✅ Authentication Test Passed!")

def test_product_search():
    """Test if product search retrieves results."""
    sample_location = "09700336"  # Update with a known working location ID
    results = search_kroger_products(sample_location, search_terms=["Eggs", "Bread"], limit=5)

    assert results is not None, "❌ Product search returned None!"
    assert isinstance(results, list), "❌ Expected a list of products!"
    assert len(results) > 0, "❌ No products found!"
    print("✅ Product Search Test Passed!")

if __name__ == "__main__":
    print("🔍 Running API Tests...")
    test_authentication()
    test_product_search()
    print("🎉 All API tests passed!")
