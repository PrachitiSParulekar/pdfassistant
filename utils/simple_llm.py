"""
Simple LLM implementation using HuggingFace API
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

class SimpleLLM:
    """Simple LLM using HuggingFace Inference API"""
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def invoke(self, prompt):
        """Generate response for the given prompt"""
        try:
            if not self.api_key or self.api_key == "your-huggingface-api-key-here":
                return self._fallback_response(prompt)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").replace(prompt, "").strip()
                return str(result)
            else:
                logger.warning(f"HuggingFace API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling HuggingFace API: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt):
        """Provide a helpful fallback response with clean formatting (no # or * symbols)"""
        prompt_lower = prompt.lower()
        
        if "complexity" in prompt_lower:
            return """Algorithm Complexity

Algorithm complexity refers to the computational resources required by an algorithm.

Types of Complexity:

Time Complexity:
• Measures how execution time increases with input size
• Common notations: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ)

Space Complexity:
• Measures memory usage relative to input size
• Includes auxiliary space used by the algorithm

Big O Notation:
• O(1) - Constant time
• O(log n) - Logarithmic time
• O(n) - Linear time  
• O(n log n) - Linearithmic time
• O(n²) - Quadratic time

For detailed analysis, please upload relevant algorithm textbooks or materials."""
        
        elif any(word in prompt_lower for word in ["sort", "sorting"]):
            return """Sorting Algorithms

Sorting algorithms arrange data in a particular order (ascending or descending).

Common Sorting Algorithms:

1. Bubble Sort
• Time Complexity: O(n²)
• Simple but inefficient for large datasets

2. Selection Sort
• Time Complexity: O(n²)
• Finds minimum element and places it at the beginning

3. Insertion Sort
• Time Complexity: O(n²) average, O(n) best case
• Efficient for small datasets

4. Merge Sort
• Time Complexity: O(n log n)
• Divide-and-conquer approach, stable sort

5. Quick Sort
• Time Complexity: O(n log n) average, O(n²) worst case
• Often fastest in practice

6. Heap Sort
• Time Complexity: O(n log n)
• Uses heap data structure

Upload algorithm textbooks for detailed implementations and analysis."""
        
        elif "algorithm" in prompt_lower:
            return """Algorithm Definition

An algorithm is a finite sequence of well-defined instructions for solving a computational problem or performing a task.

Key Characteristics:

1. Definiteness: Each step must be precisely defined and unambiguous
2. Finiteness: The algorithm must terminate after a finite number of steps  
3. Input: An algorithm has zero or more inputs
4. Output: An algorithm produces one or more outputs
5. Effectiveness: Each operation must be basic enough to be carried out

Types of Algorithms:

• Sorting algorithms (e.g., QuickSort, MergeSort)
• Search algorithms (e.g., Binary Search, Linear Search)
• Graph algorithms (e.g., Dijkstra's algorithm, BFS, DFS)
• Dynamic programming algorithms
• Greedy algorithms

Importance:

Algorithms are fundamental to computer science and programming, serving as the blueprint for solving problems systematically and efficiently.

Note: This is a general definition. For more specific information, please upload relevant PDF documents."""
        
        else:
            return """AI Assistant Response

I can provide detailed information based on your uploaded PDF documents. 

To get comprehensive answers:
• Upload relevant PDF documents (textbooks, papers, notes)
• Ask specific questions about the content
• Use technical terms related to your documents

Current capabilities:
• PDF text extraction and analysis
• Document-based question answering
• Content search and retrieval

Please ensure your HuggingFace API key is properly configured for enhanced AI responses."""
    
    def __call__(self, prompt):
        """Allow the object to be called like a function"""
        return self.invoke(prompt)
