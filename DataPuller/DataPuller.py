
#!/usr/bin/env python3
"""
File Downloader Script
Downloads files specified in a configuration file to specified locations.
This is used on KeitaiArchive to pull necessary data files from external sources, leaderboards, searchresults, etc.
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List


def load_config(config_path: str) -> List[Dict[str, str]]:
    """Load the configuration file containing download information."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('downloads', [])
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)


def download_file(url: str, destination: str) -> bool:
    """
    Download a file from URL to the specified destination.
    
    Args:
        url: The download URL
        destination: The full path where the file should be saved
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create destination directory if it doesn't exist
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Downloading: {url}")
        print(f"Destination: {destination}")
        
        # Download the file
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write to file
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded to {destination}\n")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}\n")
        return False
    except IOError as e:
        print(f"Error writing to {destination}: {e}\n")
        return False


def main():
    """Main function to orchestrate the download process."""
    # Default config file path
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'download_config.json'
    
    print(f"Loading configuration from: {config_path}")
    print("=" * 60)
    
    # Load configuration
    downloads = load_config(config_path)
    
    if not downloads:
        print("No downloads specified in configuration file.")
        sys.exit(0)
    
    print(f"Found {len(downloads)} file(s) to download\n")
    
    # Download each file
    success_count = 0
    fail_count = 0
    
    for idx, item in enumerate(downloads, 1):
        url = item.get('url')
        destination = item.get('destination')
        
        if not url or not destination:
            print(f"Skipping item {idx}: Missing 'url' or 'destination' field\n")
            fail_count += 1
            continue
        
        print(f"[{idx}/{len(downloads)}]")
        if download_file(url, destination):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("=" * 60)
    print(f"Download Summary:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(downloads)}")
    
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()