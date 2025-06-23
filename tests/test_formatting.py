#!/usr/bin/env python3
"""Test script to verify the response formatting improvements"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from utils.simple_llm import SimpleLLM
    
    print("🧪 Testing Response Formatting Improvements")
    print("=" * 50)
    
    llm = SimpleLLM()
    
    # Test algorithm query
    print("\n📝 Testing 'algorithm' query:")
    print("-" * 30)
    response = llm.invoke("define algorithm")
    print(response)
    
    # Test complexity query
    print("\n📝 Testing 'complexity' query:")
    print("-" * 30)
    response = llm.invoke("what is algorithm complexity")
    print(response)
    
    # Test sorting query
    print("\n📝 Testing 'sorting' query:")
    print("-" * 30)
    response = llm.invoke("explain sorting algorithms")
    print(response)
    
    print("\n🎉 All formatting tests completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
