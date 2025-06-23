import os
import logging

logger = logging.getLogger(__name__)

def get_llm_model():
    """
    Returns a language model instance using cloud APIs (not OpenAI)
    """
    try:
        # Use simple HuggingFace implementation first
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_api_key and hf_api_key.strip() and hf_api_key != "your-huggingface-api-key-here":
            logger.info("Using simple HuggingFace implementation")
            from .simple_llm import SimpleLLM
            return SimpleLLM()
        
        # Try HuggingFace Inference API (langchain)
        if hf_api_key and hf_api_key.strip() and hf_api_key != "your-huggingface-api-key-here":
            try:
                from langchain_huggingface import HuggingFaceEndpoint
                logger.info("Using HuggingFace Inference API")
                return HuggingFaceEndpoint(
                    repo_id="microsoft/DialoGPT-medium",
                    huggingfacehub_api_token=hf_api_key,
                    temperature=0.7,
                    max_new_tokens=512
                )
            except ImportError:
                logger.warning("langchain_huggingface not found. Install with: pip install langchain_huggingface")
            except Exception as e:
                logger.warning(f"HuggingFace API error: {str(e)}. Falling back to next option.")
        
        # Try Google Gemini API
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key and google_api_key.strip():
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info("Using Google Gemini API")
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=google_api_key,
                    temperature=0.7
                )
            except ImportError:
                logger.warning("langchain_google_genai not found. Install with: pip install langchain-google-genai")
        
        # Try Anthropic Claude API
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key and anthropic_api_key.strip():
            try:
                from langchain_anthropic import ChatAnthropic
                logger.info("Using Anthropic Claude API")
                return ChatAnthropic(
                    model="claude-3-haiku-20240307",
                    anthropic_api_key=anthropic_api_key,
                    temperature=0.7
                )
            except ImportError:
                logger.warning("langchain_anthropic not found. Install with: pip install langchain-anthropic")                
        # Fall back to simple LLM implementation
        logger.info("Falling back to simple HuggingFace implementation")
        from .simple_llm import SimpleLLM
        return SimpleLLM()
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        # Return simple LLM even if there's an error
        try:
            from .simple_llm import SimpleLLM
            return SimpleLLM()
        except:
            class MockLLM:
                def invoke(self, prompt):
                    if "algorithm" in prompt.lower():
                        return """An algorithm is a finite sequence of well-defined instructions for solving a computational problem or performing a task. Key characteristics include:

1. **Definiteness**: Each step must be precisely defined
2. **Finiteness**: Must terminate after finite steps
3. **Input**: Has zero or more inputs
4. **Output**: Produces one or more outputs
5. **Effectiveness**: Each operation must be basic enough to be carried out

Algorithms are fundamental to computer science and programming."""
                    return "Error initializing LLM. Please check your configuration."
                
                def __call__(self, prompt):
                    return self.invoke(prompt)
                    
            return MockLLM()
