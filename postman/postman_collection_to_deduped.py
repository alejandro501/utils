# postman_collection_to_deduped.py
import json
import os
import argparse
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    """Strip query parameters and fragments from URL"""
    if isinstance(url, dict):
        url_str = url.get('raw', '')
    else:
        url_str = str(url)
    
    parsed = urlparse(url_str)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def deduplicate_collection(collection_path, output_path=None):
    """Remove duplicates with consistent naming"""
    with open(collection_path) as f:
        data = json.load(f)

    # Update internal name
    data['info']['name'] = f"{data.get('info', {}).get('name', 'Collection')} [Deduped]"

    unique_urls = set()
    duplicates_removed = 0

    def process_items(items):
        nonlocal duplicates_removed
        filtered_items = []
        for item in items:
            if 'request' in item and 'url' in item['request']:
                normalized = normalize_url(item['request']['url'])
                if normalized in unique_urls:
                    duplicates_removed += 1
                    continue
                unique_urls.add(normalized)
            filtered_items.append(item)
        return filtered_items

    data['item'] = process_items(data['item'])
    
    output_path = output_path or f"{os.path.splitext(collection_path)[0]}_deduped.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Removed {duplicates_removed} duplicates. Saved to {output_path}")
    return output_path  # Now returning just the path, not a tuple

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deduplicate Postman collection')
    parser.add_argument('collection_file', help='Input collection JSON')
    parser.add_argument('-o', '--output', help='Custom output path')
    args = parser.parse_args()
    
    output_file = deduplicate_collection(args.collection_file, args.output)
    print(f"Output: {output_file}")