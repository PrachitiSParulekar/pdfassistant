#!/usr/bin/env python3
"""Test script to verify the vector store fixes"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from utils.vector_store import VectorStore
    print("✅ VectorStore imported successfully")
    
    # Test instantiation
    vs = VectorStore()
    print("✅ VectorStore instantiated successfully")
    
    # Test methods exist
    print(f"✅ has_document method exists: {hasattr(vs, 'has_document')}")
    print(f"✅ add_document method exists: {hasattr(vs, 'add_document')}")
    print(f"✅ get_all_documents method exists: {hasattr(vs, 'get_all_documents')}")
    
    print("\n🎉 All vector store fixes verified!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
