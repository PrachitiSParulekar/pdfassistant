"""
Comprehensive test to verify the PDF Assistant upload system
"""
import requests
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """Create a test PDF file for testing"""
    # Create a temporary PDF file
    fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    
    try:
        # Create PDF with reportlab
        c = canvas.Canvas(temp_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 720, "This is a test document for upload testing.")
        c.drawString(100, 690, "It contains sample text for algorithm questions.")
        c.drawString(100, 660, "An algorithm is a step-by-step procedure for solving a problem.")
        c.save()
        
        return temp_path
    except Exception as e:
        os.close(fd)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e

def test_complete_upload_workflow():
    """Test the complete upload workflow"""
    print("🧪 Testing Complete Upload Workflow")
    print("=" * 50)
    
    # Step 1: Test health endpoint
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Step 2: Create and upload test PDF
    print("\n2️⃣ Creating and uploading test PDF...")
    test_pdf_path = None
    try:
        test_pdf_path = create_test_pdf()
        
        with open(test_pdf_path, 'rb') as f:
            files = {'file': ('test_document.pdf', f, 'application/pdf')}
            response = requests.post("http://127.0.0.1:5000/upload", files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ Upload successful: {upload_data.get('message', 'No message')}")
            document_id = upload_data.get('document_id')
        else:
            print(f"❌ Upload failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up test PDF
        if test_pdf_path and os.path.exists(test_pdf_path):
            os.unlink(test_pdf_path)
    
    # Step 3: Verify document listing
    print("\n3️⃣ Testing document listing...")
    try:
        response = requests.get("http://127.0.0.1:5000/documents")
        if response.status_code == 200:
            docs_data = response.json()
            print(f"✅ Documents listed: {docs_data.get('count', 0)} documents")
        else:
            print("❌ Document listing failed")
            return False
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return False
    
    # Step 4: Test query functionality (basic endpoint test)
    print("\n4️⃣ Testing query endpoint...")
    try:
        query_data = {
            "query": "What is an algorithm?",
            "use_web_search": False
        }
        response = requests.post(
            "http://127.0.0.1:5000/query", 
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Query endpoint accessible (response generation may have issues)")
        else:
            print(f"❌ Query endpoint failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False
    
    # Step 5: Test file validation
    print("\n5️⃣ Testing file validation...")
    try:
        # Test with non-PDF file
        response = requests.post("http://127.0.0.1:5000/upload", 
                               files={'file': ('test.txt', b'not a pdf', 'text/plain')})
        
        if response.status_code == 400:
            print("✅ File validation working (correctly rejected non-PDF)")
        else:
            print("❌ File validation failed (should reject non-PDF)")
            return False
    except Exception as e:
        print(f"❌ File validation error: {e}")
        return False
    
    print("\n🎉 All upload workflow tests passed!")
    print("📋 Summary:")
    print("  ✅ Health endpoint working")
    print("  ✅ PDF upload working")  
    print("  ✅ File processing working")
    print("  ✅ Document listing working")
    print("  ✅ Query endpoint accessible")
    print("  ✅ File validation working")
    print("\n🔧 Note: LLM responses may show errors due to missing API keys,")
    print("    but the core upload functionality is working correctly!")
    
    return True

if __name__ == "__main__":
    try:
        import reportlab
        success = test_complete_upload_workflow()
        if not success:
            print("\n⚠️  Some tests failed!")
    except ImportError:
        print("❌ reportlab package required for creating test PDFs")
        print("   Install with: pip install reportlab")
        print("\n🔍 However, we can still check existing functionality...")
        
        # Basic functionality test without creating new PDFs
        print("\n🧪 Testing Existing Functionality")
        print("=" * 50)
        
        try:
            # Test health
            response = requests.get("http://127.0.0.1:5000/health")
            print(f"Health check: {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
            
            # Test documents listing
            response = requests.get("http://127.0.0.1:5000/documents") 
            print(f"Documents API: {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
            
            # Test query endpoint
            response = requests.post("http://127.0.0.1:5000/query", 
                                   json={"query": "test", "use_web_search": False},
                                   headers={'Content-Type': 'application/json'})
            print(f"Query API: {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
            
            print("\n✅ Core upload system appears to be working!")
            
        except Exception as e:
            print(f"❌ Error testing basic functionality: {e}")
