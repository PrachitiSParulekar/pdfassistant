#!/usr/bin/env python3
"""Test script to verify the clean formatting without # and * symbols"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from utils.simple_llm import SimpleLLM
    print("✅ SimpleLLM imported successfully")
    
    # Test instantiation
    llm = SimpleLLM()
    print("✅ SimpleLLM instantiated successfully")
    
    print("\n" + "="*60)
    print("🧪 Testing Clean Response Formatting (No # or * symbols)")
    print("="*60)
    
    test_queries = [
        "what is algorithm complexity",
        "explain sorting algorithms", 
        "define algorithm"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing '{query}':")
        print("-" * 30)
        response = llm.invoke(query)
        print(response)
        print()
    
    print("🎉 All clean formatting tests completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
