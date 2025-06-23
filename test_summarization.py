#!/usr/bin/env python3
"""Test script to verify the summarization functionality"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from utils.rag import RAGSystem
    from utils.vector_store import VectorStore
    from utils.simple_llm import SimpleLLM
    
    print("✅ All modules imported successfully")
    
    # Test instantiation
    vector_store = VectorStore()
    llm = SimpleLLM()
    rag = RAGSystem(vector_store, None, llm)
    
    print("✅ RAG system instantiated successfully")
    
    # Check if summarize_document method exists
    if hasattr(rag, 'summarize_document'):
        print("✅ summarize_document method exists")
    else:
        print("❌ summarize_document method missing")
    
    # Test with a non-existent document (should handle gracefully)
    try:
        result = rag.summarize_document("test_doc_id")
        print(f"✅ Summarization test completed: {result[:100]}...")
    except Exception as e:
        print(f"❌ Summarization test failed: {e}")
    
    print("🎉 Summarization feature test completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
