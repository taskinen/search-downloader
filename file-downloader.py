#!/usr/bin/env python3
"""
File Downloader by Extension and Domain - Google Custom Search API Version
Downloads files matching a given extension from a specific domain using Google's official API.
"""

import requests
import os
import time
import argparse
from urllib.parse import urlparse
import json
from typing import List, Dict, Optional

class GoogleFileSearcher:
    """Handles file searching using Google Custom Search API"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.api_url = 'https://www.googleapis.com/customsearch/v1'
    
    def search_files(self, domain: str, extension: str, num_results: int = 10) -> List[Dict]:
        """
        Search for files using Google Custom Search API.
        Returns a list of search results.
        """
        results = []
        
        # Google Custom Search API returns max 10 results per request
        # Need to paginate for more results
        for start_index in range(1, num_results + 1, 10):
            items_to_fetch = min(10, num_results - len(results))
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': f'filetype:{extension} site:{domain}',
                'num': items_to_fetch,
                'start': start_index
            }
            
            try:
                response = requests.get(self.api_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Check if we got results
                if 'items' in data:
                    results.extend(data['items'])
                else:
                    print(f"No more results found (fetched {len(results)} total)")
                    break
                    
                # Check if we have all results we need
                if len(results) >= num_results:
                    break
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Rate limit exceeded. Please try again later.")
                else:
                    print(f"HTTP error occurred: {e}")
                break
            except requests.RequestException as e:
                print(f"Error making API request: {e}")
                break
            except json.JSONDecodeError:
                print("Error parsing API response")
                break
        
        return results[:num_results]

def extract_file_url_from_result(result: Dict, extension: str) -> Optional[str]:
    """
    Extract the actual file URL from a search result.
    Returns None if no valid file URL is found.
    """
    # First check the main link
    if 'link' in result:
        link = result['link']
        if link.lower().endswith(f'.{extension.lower()}'):
            return link
    
    # Sometimes the file link might be in the pagemap metadata
    if 'pagemap' in result and 'metatags' in result['pagemap']:
        for metatag in result['pagemap']['metatags']:
            # Check common metadata fields that might contain file URLs
            for key in ['og:url', 'url', 'citation_pdf_url']:
                if key in metatag:
                    url = metatag[key]
                    if url.lower().endswith(f'.{extension.lower()}'):
                        return url
    
    # Check if the link might be a download page that contains the actual file
    # This is a simple heuristic - you might need to enhance this
    if 'link' in result and extension.lower() in result['link'].lower():
        return result['link']
    
    return None

def download_file(url: str, destination_folder: str = '.') -> bool:
    """
    Download a file from the given URL to the destination folder.
    """
    try:
        # Remove trailing slashes from URL for cleaner filename extraction
        clean_url = url.rstrip('/')
        
        # Extract filename from URL
        parsed_url = urlparse(clean_url)
        filename = os.path.basename(parsed_url.path)
        
        # If filename is empty or doesn't have an extension, generate one
        if not filename or '.' not in filename:
            # Try to extract filename from the URL path segments
            path_segments = [seg for seg in parsed_url.path.split('/') if seg]
            if path_segments and '.' in path_segments[-1]:
                filename = path_segments[-1]
            else:
                timestamp = int(time.time())
                # Extract extension from URL more carefully
                url_parts = clean_url.split('.')
                if len(url_parts) > 1:
                    extension = url_parts[-1].split('/')[0][:4]  # Get extension, max 4 chars
                else:
                    extension = 'download'
                filename = f"download_{timestamp}.{extension}"
        
        # Clean the filename - remove any trailing slashes or invalid characters
        filename = filename.rstrip('/').replace('/', '_')
        
        filepath = os.path.join(destination_folder, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"File already exists: {filename}")
            return False
        
        # Download the file
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check if the response is actually a file (not an HTML page)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type and not url.lower().endswith('.html'):
            print(f"Skipping {url} - appears to be an HTML page, not a file")
            return False
        
        # Save the file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify file size
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            os.remove(filepath)
            print(f"Removed empty file: {filename}")
            return False
        
        print(f"Downloaded: {filename} ({file_size:,} bytes)")
        return True
        
    except requests.exceptions.Timeout:
        print(f"Timeout downloading {url}")
        return False
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error downloading {url}: {e}")
        return False

def load_api_credentials(config_file: str = 'google_api_config.json') -> tuple:
    """
    Load API credentials from a JSON file.
    Returns (api_key, search_engine_id) or (None, None) if not found.
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('api_key'), config.get('search_engine_id')
    except FileNotFoundError:
        return None, None
    except json.JSONDecodeError:
        print(f"Error parsing {config_file}")
        return None, None

def save_api_credentials(api_key: str, search_engine_id: str, config_file: str = 'google_api_config.json'):
    """Save API credentials to a JSON file for future use."""
    config = {
        'api_key': api_key,
        'search_engine_id': search_engine_id
    }
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"API credentials saved to {config_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Download files with a specific extension from a given domain using Google Custom Search API',
        epilog='First time setup: You\'ll be prompted for your Google API key and Search Engine ID.\n'
               'Get these from: https://developers.google.com/custom-search/v1/overview',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('domain', help='Domain name to search (e.g., puolustusvoimat.fi)')
    parser.add_argument('extension', help='File extension to search for (e.g., pdf)')
    parser.add_argument('-n', '--number', type=int, default=10, 
                       help='Number of files to download (default: 10)')
    parser.add_argument('-d', '--directory', default='.', 
                       help='Directory to save files (default: current directory)')
    parser.add_argument('--api-key', help='Google Custom Search API key')
    parser.add_argument('--search-engine-id', help='Google Custom Search Engine ID')
    parser.add_argument('--save-credentials', action='store_true',
                       help='Save API credentials for future use')
    
    args = parser.parse_args()
    
    # Get API credentials
    api_key = args.api_key
    search_engine_id = args.search_engine_id
    
    # Try to load from config file if not provided
    if not api_key or not search_engine_id:
        saved_key, saved_id = load_api_credentials()
        if saved_key and saved_id:
            print("Using saved API credentials")
            api_key = api_key or saved_key
            search_engine_id = search_engine_id or saved_id
    
    # Prompt for credentials if still missing
    if not api_key:
        print("\nGoogle Custom Search API key not found.")
        print("Get your API key from: https://console.cloud.google.com/apis/credentials")
        api_key = input("Enter your API key: ").strip()
    
    if not search_engine_id:
        print("\nGoogle Custom Search Engine ID not found.")
        print("Create a search engine at: https://programmablesearchengine.google.com/")
        search_engine_id = input("Enter your Search Engine ID: ").strip()
    
    # Save credentials if requested
    if args.save_credentials:
        save_api_credentials(api_key, search_engine_id)
    
    # Create directory if it doesn't exist
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    
    # Initialize the searcher
    searcher = GoogleFileSearcher(api_key, search_engine_id)
    
    print(f"\nSearching for {args.extension} files on {args.domain}...")
    
    # Search for files
    results = searcher.search_files(args.domain, args.extension, args.number)
    
    if not results:
        print(f"No {args.extension} files found on {args.domain}")
        return
    
    print(f"Found {len(results)} search results")
    
    # Extract file URLs and download
    downloaded = 0
    file_urls = []
    
    # Extract file URLs from results
    for result in results:
        url = extract_file_url_from_result(result, args.extension)
        if url:
            file_urls.append(url)
    
    if not file_urls:
        print(f"No direct {args.extension} file links found in search results")
        print("The search found pages mentioning these files, but no direct download links.")
        return
    
    print(f"Found {len(file_urls)} direct file links\n")
    
    # Download files
    for i, url in enumerate(file_urls[:args.number]):
        print(f"Downloading file {i+1}/{min(len(file_urls), args.number)}: {url}")
        if download_file(url, args.directory):
            downloaded += 1
        
        # Add a small delay between downloads to be polite
        if i < len(file_urls) - 1:
            time.sleep(1)
    
    print(f"\nDownload complete. Successfully downloaded {downloaded} files.")
    
    # Show API usage info
    print(f"\nAPI Usage: {len(results)} search results fetched")
    print("Note: Google Custom Search API has a free tier of 100 queries per day")

if __name__ == "__main__":
    main()
