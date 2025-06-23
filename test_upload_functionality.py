"""
Test script to verify PDF upload functionality
"""
import requests
import os

def test_upload_endpoint():
    """Test the upload endpoint"""
    url = "http://127.0.0.1:5000/upload"
    
    # Check if there are any PDF files in uploads directory
    uploads_dir = "./uploads"
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in uploads directory for testing")
        return False
    
    # Test with the first PDF file
    test_file = pdf_files[0]
    file_path = os.path.join(uploads_dir, test_file)
    
    print(f"🧪 Testing upload with file: {test_file}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response data: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Upload test successful!")
            return True
        else:
            print("❌ Upload test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload test: {str(e)}")
        return False

def test_documents_endpoint():
    """Test the documents listing endpoint"""
    url = "http://127.0.0.1:5000/documents"
    
    try:
        response = requests.get(url)
        print(f"📊 Documents endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📚 Number of documents: {data.get('count', 0)}")
            print("✅ Documents endpoint working!")
            return True
        else:
            print("❌ Documents endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing documents endpoint: {str(e)}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    url = "http://127.0.0.1:5000/health"
    
    try:
        response = requests.get(url)
        print(f"🏥 Health check status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during health check: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting PDF Assistant Upload Tests")
    print("=" * 50)
    
    # Test health check first
    health_ok = test_health_endpoint()
    print()
    
    # Test documents endpoint
    docs_ok = test_documents_endpoint()
    print()
    
    # Test upload functionality
    upload_ok = test_upload_endpoint()
    print()
    
    print("=" * 50)
    print("📋 Test Summary:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Documents API: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"Upload API: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if all([health_ok, docs_ok, upload_ok]):
        print("\n🎉 All tests passed! Upload functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. There may be issues with the upload functionality.")
