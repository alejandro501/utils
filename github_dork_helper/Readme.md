# GitHub Code Search Scanner

A Python script to automate searching GitHub for sensitive information using multiple search queries from text files.

## Features

- **Bulk Search Processing**: Reads multiple GitHub search URLs from text files
- **Rate Limit Handling**: Automatically checks and respects GitHub API rate limits
- **Results Logging**: Saves findings in both verbose and minimal formats
- **Retry Mechanism**: Implements exponential backoff for failed requests
- **Query Normalization**: Properly decodes and formats search queries

## Requirements

- Python 3.x
- `requests` library
- GitHub personal access token

## Setup

1. Install the required package:
   ```bash
   pip install requests
   ```

2. Create a file named `_github_token.txt` in the same directory and paste your GitHub personal access token in it.

3. Create one or more text files containing GitHub search URLs (one per line). Example search URL:
   ```
   https://github.com/search?q=password+in%3Aurl+extension%3Aenv
   ```

## Usage

1. Place all your search query URLs in `.txt` files in the script's directory
2. Run the script:
   ```bash
   python scanner.py
   ```

The script will:
- Process all search URLs found in `.txt` files (except `_github_token.txt`)
- Save results in two output files:
  - `_hits_verbose.txt`: Detailed results with timestamps and query information
  - `_hits.txt`: Minimal format with just the found URLs

## Output Files

- `_hits_verbose.txt`: Contains detailed information about each hit including:
  - The exact query used
  - Number of results found
  - Timestamp of discovery
  - All matching repository URLs

- `_hits.txt`: Contains just the URLs of repositories with matches (one per line)

## Rate Limiting

The script automatically:
- Checks your remaining API calls before each search
- Pauses when approaching rate limits
- Implements exponential backoff for failed requests
- Includes a base delay between queries to prevent abuse detection

## Customization

You can adjust these parameters in the script:
- `MAX_RETRIES`: How many times to retry a failed search
- `BASE_DELAY`: Minimum delay between queries (in seconds)
- Output file names

## Security Note

- Your GitHub token is read from `_github_token.txt` - keep this file secure
- The script does not modify any repositories, only searches public code

## Example Search Queries

Good candidates for search URLs to include in your text files:
- API keys
- Passwords in config files
- Sensitive environment variables
- Private key patterns
- Hardcoded credentials