import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIConfig:
    def __init__(self, api_key=None, **kwargs):
        # Update this line with a valid model that exists on HuggingFace
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # More likely to exist
        
        # Inside __init__ or wherever api_key is handled
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            self.api_key = None  # Make it optional
            print("Warning: HuggingFace API key not found. Some features may not work.")
            # Alternatively, you could set a demo/test key or functionality

# Initialize default config
default_config = APIConfig()