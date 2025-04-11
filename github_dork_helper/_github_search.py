import os
import re
import requests
import time
import socket
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote_plus

# Configuration (unchanged)
GITHUB_TOKEN_FILE = "_github_token.txt"
HITS_MINIMAL = "_hits.txt"
HITS_VERBOSE = "_hits_verbose.txt"
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds
NETWORK_ERROR_DELAY = 30  # Longer delay for network issues

# ANSI color codes (unchanged)
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Add YELLOW for warnings
YELLOW = '\033[93m'

# Read all GitHub tokens (unchanged)
def get_github_tokens():
    with open(GITHUB_TOKEN_FILE, "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    return tokens

GITHUB_TOKENS = get_github_tokens()
current_token_index = 0

def get_current_token():
    global current_token_index
    return GITHUB_TOKENS[current_token_index]

def rotate_token():
    global current_token_index
    current_token_index = (current_token_index + 1) % len(GITHUB_TOKENS)
    print(f"{RED}[!] Rotating to token {current_token_index + 1}/{len(GITHUB_TOKENS)}{RESET}")
    return get_current_token()

def get_headers():
    return {
        "Authorization": f"Bearer {get_current_token()}",
        "Accept": "application/vnd.github.v3+json",
    }

def get_search_urls_from_files():
    """Collect ALL GitHub search URLs from all .txt files except the token file."""
    urls = set()
    for filename in os.listdir("."):
        if filename.endswith(".txt") and filename != GITHUB_TOKEN_FILE:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("https://github.com/search?q="):
                        urls.add(line)
    return sorted(urls)

def extract_github_search_query(url):
    """
    Extract and clean the `q` parameter from a GitHub search URL.
    Fixes encoding issues like 'in:url%22107...' to 'in:url:107...'.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    raw_query = query_params.get("q", [""])[0]
    
    decoded_query = unquote_plus(raw_query)
    
    decoded_query = re.sub(r'in:url"?([^\s"]+)"?', r'in:url:\1', decoded_query)
    
    return decoded_query

def log_hit_verbose(query, total_count, results):
    """Log detailed results to verbose file."""
    with open(HITS_VERBOSE, "a") as f:
        f.write(f"\n=== HIT ===\nQuery: {query}\nResults: {total_count}\n")
        for item in results:
            f.write(f"- {item['html_url']}\n")
        f.write(f"Time: {datetime.now()}\n")

def log_hit_minimal(url):
    """Log only the original search URL to minimal file."""
    with open(HITS_MINIMAL, "a") as f:
        f.write(f"{url}\n")

def check_rate_limit():
    """Check remaining rate limit and reset time."""
    try:
        resp = requests.get("https://api.github.com/rate_limit", headers=get_headers(), timeout=10)
        if resp.status_code == 401:
            rotate_token()
            return check_rate_limit()
        resp.raise_for_status()
        data = resp.json()
        core = data["resources"]["core"]
        search = data["resources"]["search"]
        return (
            search["remaining"],  # Search-specific remaining calls
            search["reset"],      # Search reset time
            core["remaining"],    # Core remaining calls (for non-search API)
        )
    except requests.exceptions.Timeout:
        print(f"{YELLOW}[!] Timeout while checking rate limit{RESET}")
        return 0, time.time() + 60, 0
    except requests.exceptions.ConnectionError:
        print(f"{YELLOW}[!] Connection error while checking rate limit{RESET}")
        return 0, time.time() + 60, 0
    except Exception as e:
        print(f"{RED}[!] Rate limit check failed: {e}{RESET}")
        return 0, time.time() + 60, 0  # Fallback values

def is_network_error(e):
    """Check if the exception is a network-related error."""
    network_errors = (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        socket.gaierror,  # For DNS resolution errors
    )
    return isinstance(e, network_errors)

def github_search(url, retry=0):
    """Execute GitHub search using the exact URL query."""
    if retry >= MAX_RETRIES:
        print(f"{RED}[!] Max retries reached for: {url}{RESET}")
        return None

    try:
        query = extract_github_search_query(url)
        if not query:
            return None

        api_url = "https://api.github.com/search/code"
        response = requests.get(api_url, headers=get_headers(), params={"q": query}, timeout=10)
        
        # Handle authentication errors
        if response.status_code == 401:
            rotate_token()
            return github_search(url, retry + 1)
        
        # Handle rate limits
        if response.status_code == 403:
            # Check if it's an abuse rate limit
            if 'Retry-After' in response.headers:
                sleep_time = int(response.headers['Retry-After'])
            else:
                # Standard rate limit
                remaining, reset_time, _ = check_rate_limit()
                sleep_time = max(reset_time - time.time(), 0) + 5
            
            print(f"{RED}[!] Rate limit triggered. Sleeping {sleep_time}s...{RESET}")
            time.sleep(sleep_time)
            return github_search(url, retry + 1)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        if is_network_error(e):
            print(f"{YELLOW}[!] Network error searching '{query}': {e}{RESET}")
            sleep_time = NETWORK_ERROR_DELAY * (retry + 1)
            print(f"{YELLOW}[!] Waiting {sleep_time}s before retry...{RESET}")
            time.sleep(sleep_time)
        else:
            print(f"{RED}[!] Error searching '{query}': {e}{RESET}")
            time.sleep(BASE_DELAY * (retry + 1))  # Exponential backoff
        
        return github_search(url, retry + 1)
    except Exception as e:
        print(f"{RED}[!] Unexpected error searching '{query}': {e}{RESET}")
        time.sleep(BASE_DELAY * (retry + 1))
        return github_search(url, retry + 1)

if __name__ == "__main__":
    if not GITHUB_TOKENS:
        print(f"{RED}[!] No tokens found in {GITHUB_TOKEN_FILE}{RESET}")
        exit(1)
        
    print(f"[*] Starting scan with {len(GITHUB_TOKENS)} tokens available")
    
    # Clear output files
    open(HITS_MINIMAL, "w").close()
    open(HITS_VERBOSE, "w").close()

    search_urls = get_search_urls_from_files()
    print(f"[*] Found {len(search_urls)} unique search URLs.")

    for url in search_urls:
        try:
            remaining, reset_time, _ = check_rate_limit()
            
            # Pre-emptive rate limit handling
            if remaining <= 1:
                sleep_time = max(reset_time - time.time(), 0) + 5
                print(f"{RED}[!] Approaching rate limit. Sleeping {sleep_time:.1f}s...{RESET}")
                time.sleep(sleep_time)

            query = extract_github_search_query(url)
            print(f"[>] Executing: {query}")
            result = github_search(url)
            
            if result and "total_count" in result and result["total_count"] > 0:
                print(f"{GREEN}[+] Found {result['total_count']} results!{RESET}")
                log_hit_verbose(query, result["total_count"], result["items"])
                log_hit_minimal(url)
            else:
                print(f"[-] No results.")
            
            time.sleep(BASE_DELAY)  # Default delay between queries
        
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[!] Script interrupted by user. Exiting gracefully...{RESET}")
            break
        except Exception as e:
            print(f"{RED}[!] Fatal error processing URL {url}: {e}{RESET}")
            print(f"{YELLOW}[!] Continuing with next URL...{RESET}")
            time.sleep(BASE_DELAY)
            continue

    print("[*] Scan complete.")
