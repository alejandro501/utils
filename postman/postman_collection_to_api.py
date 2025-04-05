#!/usr/bin/env python3
import json
import re
import os
import argparse
from urllib.parse import urlparse

def is_api_url(url):
    """Strict check for API endpoints"""
    if isinstance(url, dict):
        url_str = url.get('raw', '')
    else:
        url_str = str(url)
    
    # More comprehensive API patterns
    api_patterns = [
        r'\/api\/',          # /api/
        r'\/v[0-9]+\/',      # /v1/, /v2/
        r'\/graphql',        # /graphql
        r'\/rest\/',         # /rest/
        r'\/json\/',         # /json/
        r'\/endpoint\/',     # /endpoint/
        r'\/[a-z0-9-]+_v[0-9]+'  # endpoint_v1, service_v2
    ]
    
    # Exclude common non-API patterns
    non_api_patterns = [
        r'\.html$',
        r'\.php$',
        r'\/static\/',
        r'\/assets\/',
        r'\/images\/',
        r'\/css\/',
        r'\/js\/',
        r'\/favicon\.ico'
    ]
    
    # Check for API patterns
    has_api_pattern = any(re.search(pattern, url_str, re.I) for pattern in api_patterns)
    # Check for non-API patterns
    has_non_api_pattern = any(re.search(pattern, url_str, re.I) for pattern in non_api_patterns)
    
    return has_api_pattern and not has_non_api_pattern

def filter_api_requests(collection_path, output_path=None):
    """Strictly filter for only API requests"""
    with open(collection_path) as f:
        data = json.load(f)

    # Update collection name
    data['info']['name'] = f"{data.get('info', {}).get('name', 'Collection')} [API]"

    def process_items(items):
        filtered = []
        for item in items:
            # Skip folders that don't contain API requests
            if 'item' in item:
                item['item'] = process_items(item['item'])
                if item['item']:  # Only keep folders with API items
                    filtered.append(item)
            # Only include API requests
            elif 'request' in item and 'url' in item['request']:
                if is_api_url(item['request']['url']):
                    filtered.append(item)
        return filtered

    data['item'] = process_items(data['item'])
    
    output_path = output_path or f"{os.path.splitext(collection_path)[0]}_strict_api.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Strictly filter Postman collection for API requests')
    parser.add_argument('collection_file', help='Path to Postman collection JSON')
    parser.add_argument('-o', '--output', help='Custom output path')
    args = parser.parse_args()
    
    output_file = filter_api_requests(args.collection_file, args.output)
    print(f"Strict API-only collection saved to {output_file}")