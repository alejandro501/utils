#!/usr/bin/env python3
import argparse
import os
from postman_collection_to_deduped import deduplicate_collection
from postman_collection_to_api import filter_api_requests
from postman_collection_to_baseurl import filter_by_baseurl

def process_pipeline(collection_path, output_dir=None, base_url=None):
    """Run processing pipeline with optional base URL filtering"""
    # Ensure output directory exists
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(os.path.basename(collection_path))[0]
    
    # Generate output paths
    outputs = {
        'deduped': os.path.join(output_dir or os.path.dirname(collection_path), 
                               f"{base_name}_deduped.json"),
        'api': os.path.join(output_dir or os.path.dirname(collection_path), 
                           f"{base_name}_deduped_api.json"),
        'baseurl': os.path.join(output_dir or os.path.dirname(collection_path), 
                               f"{base_name}_{base_url}.json") if base_url else None
    }

    print("=== Starting Postman Collection Processing ===")
    
    # Step 1: Deduplicate
    deduped_file = deduplicate_collection(collection_path, outputs['deduped'])
    print(f"1. Deduplication complete: {deduped_file}")
    
    # Step 2: API Filter (always runs)
    api_file = filter_api_requests(deduped_file, outputs['api'])
    print(f"2. API extraction complete: {api_file}")
    
    # Step 3: Base URL Filter (conditional)
    if base_url:
        baseurl_file = filter_by_baseurl(deduped_file, base_url, outputs['baseurl'])
        print(f"3. Base URL filter complete: {baseurl_file}")
        outputs['baseurl'] = baseurl_file
    
    print("\n=== Processing Complete ===")
    print(f"Final outputs:\n- Deduplicated: {outputs['deduped']}")
    print(f"- API Only: {outputs['api']}")
    if base_url:
        print(f"- {base_url} Only: {outputs['baseurl']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Postman Collection Processor - Deduplicate, API extraction, and optional base URL filtering'
    )
    parser.add_argument('collection_file', help='Path to Postman collection JSON')
    parser.add_argument('--base-url', help='Filter by base URL (e.g. "registration-api")')
    parser.add_argument('-o', '--output-dir', help='Custom output directory')
    
    args = parser.parse_args()
    process_pipeline(args.collection_file, args.output_dir, args.base_url)