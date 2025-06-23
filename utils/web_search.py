# utils/web_search.py
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

class WebSearch:
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY") 
        self.search_engine_id = os.getenv("GOOGLE_CSE_ID")
        self.last_request = 0
        self.min_delay = 1  # Minimum delay between requests in seconds
        
    def search(self, query, num_results=3):
        """Search the web for information related to the query"""
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request < self.min_delay:
            time.sleep(self.min_delay - (current_time - self.last_request))
        
        try:
            # Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params)
            self.last_request = time.time()
            
            if response.status_code != 200:
                print(f"Search API error: {response.status_code}")
                return []
            
            results = response.json()
            
            # Format and return relevant information
            formatted_results = []
            if 'items' in results:
                for item in results['items']:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'source': 'web'
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return []
        
def perform_web_search(query, num_results=3):
    """
    Perform a web search for the given query
    
    Args:
        query: Search query
        num_results: Number of results to return
    
    Returns:
        list: List of search results
    """
    try:
        # Ensure search_client is properly initialized
        if search_client is None:
            logger.error("Search client is not initialized")
            return []
            
        # Make sure query is a string
        if query is None:
            logger.warning("Search query is None")
            return []
            
        # Ensure we're not concatenating None with strings
        search_term = str(query).strip()
        if not search_term:
            logger.warning("Empty search query")
            return []
        
        # Perform the search
        search_results = search_client.search(search_term, num_results=num_results)
        
        # Process and return results
        results = []
        for result in search_results:
            # Guard against None values
            title = result.get('title', '') or ''
            snippet = result.get('snippet', '') or ''
            url = result.get('link', '') or ''
            
            # Create result object with safe values
            results.append({
                'title': title,
                'snippet': snippet,
                'url': url
            })
            
        return results
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []