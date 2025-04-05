Here's an updated `README.md` that reflects the current functionality of your Postman collection processing tools:

```markdown
# Postman Collection Processor

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A set of Python scripts for processing Postman collections with:
- Smart deduplication
- API endpoint filtering
- Folder structure preservation

## Tools

### 1. Deduplicator (`postman_collection_to_deduped.py`)
- Removes duplicate requests based on URL paths (ignoring query parameters)
- Preserves all collection metadata and folder structure
- Outputs: `*_deduped.json`

### 2. API Filter (`postman_collection_to_api.py`)
- Strictly filters for only API endpoints using comprehensive pattern matching
- Excludes static assets, HTML pages, and non-API resources
- Outputs: `*_strict_api.json`

### 3. Pipeline Processor (`main.py`)
- Runs both deduplication and API filtering sequentially
- Outputs both deduplicated and API-only versions

## Installation

```bash
git clone https://github.com/yourusername/postman-processor.git
cd postman-processor
pip install -r requirements.txt
```

## Usage

### Individual Tools
```bash
# Deduplicate only
python3 postman_collection_to_deduped.py collection.json

# API filter only
python3 postman_collection_to_api.py collection.json
```

### Full Pipeline
```bash
python3 main.py collection.json
```
Outputs:
- `collection_deduped.json`
- `collection_deduped_strict_api.json`

### Custom Output
```bash
python3 main.py collection.json -o processed/
```
Outputs:
- `processed/collection_deduped.json`
- `processed/collection_deduped_strict_api.json`

## API Detection Patterns
The API filter looks for these patterns:
- `/api/`, `/v1/`, `/v2/` paths
- `/graphql`, `/rest/`, `/json/` endpoints
- `.json`, `.xml` extensions
- `/service/`, `/endpoint/` paths
- `*_v1`, `*_v2` versioned endpoints

## Examples

Before processing:
```
pm_wolt_all.json
  ├── Login (HTML)
  ├── API v1
  │   ├── Get Users
  │   ├── Create User
  ├── Images
  │   ├── Logo.png
```

After running `main.py`:
```
pm_wolt_all_deduped.json (all unique requests)
pm_wolt_all_deduped_strict_api.json (only API endpoints)
  └── API v1
      ├── Get Users
      ├── Create User
```

## Requirements
- Python 3.7+
- No external dependencies
