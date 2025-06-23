"""
Test script to verify PDF query functionality
"""
import requests
import json

def test_query_endpoint():
    """Test the query endpoint"""
    url = "http://127.0.0.1:5000/query"
    
    # Test query about algorithms
    test_query = "What is an algorithm?"
    
    payload = {
        "query": test_query,
        "use_web_search": False
    }
    
    print(f"🧪 Testing query: '{test_query}'")
    
    try:
        response = requests.post(
            url, 
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Query: {data.get('query', 'N/A')}")
            print(f"🤖 Response preview: {data.get('response', 'N/A')[:200]}...")
            print("✅ Query test successful!")
            return True
        else:
            print(f"❌ Query test failed! Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during query test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting PDF Assistant Query Test")
    print("=" * 50)
    
    query_ok = test_query_endpoint()
    
    print("=" * 50)
    if query_ok:
        print("🎉 Query functionality is working correctly!")
    else:
        print("⚠️  Query functionality has issues.")
