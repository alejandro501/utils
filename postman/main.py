# main.py
import argparse
import os
from postman_collection_to_deduped import deduplicate_collection
from postman_collection_to_api import filter_api_requests

def process_pipeline(collection_path, output_dir=None):
    """Run both deduplication and API filtering"""
    # Ensure output directory exists
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate base output paths
    base_name = os.path.splitext(os.path.basename(collection_path))[0]
    deduped_path = os.path.join(output_dir or os.path.dirname(collection_path), 
                      f"{base_name}_deduped.json")
    api_path = os.path.join(output_dir or os.path.dirname(collection_path), 
                 f"{base_name}_api.json")
    
    # Run pipeline
    print("=== Starting Postman Collection Processing ===")
    
    # Step 1: Deduplicate (now expecting just the path)
    deduped_file = deduplicate_collection(collection_path, deduped_path)
    print(f"1. Deduplication complete.")
    print(f"   Saved to: {deduped_file}")
    
    # Step 2: Extract APIs
    api_file = filter_api_requests(deduped_file, api_path)
    print(f"2. API extraction complete.")
    print(f"   Saved to: {api_file}")
    
    print(f"\nFinal output files:")
    print(f"- Deduplicated: {deduped_file}")
    print(f"- API Only: {api_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Postman Collection Processing Pipeline - Deduplicate then extract APIs'
    )
    parser.add_argument('collection_file', help='Path to Postman collection JSON')
    parser.add_argument('-o', '--output-dir', help='Custom output directory')
    
    args = parser.parse_args()
    
    process_pipeline(args.collection_file, args.output_dir)