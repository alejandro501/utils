#!/usr/bin/env python3
import json
import re
import os
import argparse
from urllib.parse import urlparse

def filter_by_baseurl(collection_path, base_url, output_path=None):
    """Filter collection to only requests matching the base URL"""
    with open(collection_path) as f:
        data = json.load(f)

    # Update collection name
    data['info']['name'] = f"{data.get('info', {}).get('name', 'Collection')} [{base_url}]"

    def process_items(items):
        filtered = []
        for item in items:
            if 'request' in item and 'url' in item['request']:
                url = item['request']['url'].get('raw', str(item['request']['url']))
                if re.search(fr'https?://[^/]*{re.escape(base_url)}', url, re.I):
                    filtered.append(item)
            elif 'item' in item:  # Preserve folders with matching children
                item['item'] = process_items(item['item'])
                if item['item']:
                    filtered.append(item)
        return filtered

    data['item'] = process_items(data['item'])
    
    output_path = output_path or f"{os.path.splitext(collection_path)[0]}_{base_url}.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter Postman collection by base URL')
    parser.add_argument('collection_file', help='Input collection JSON')
    parser.add_argument('--base-url', required=True, help='Base URL to filter (e.g. "registration-api")')
    parser.add_argument('-o', '--output', help='Custom output path')
    args = parser.parse_args()
    
    output_file = filter_by_baseurl(args.collection_file, args.base_url, args.output)
    print(f"Filtered collection saved to {output_file}")