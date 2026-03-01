"""
AI-Powered Test Oracle: Data Fetching from Test Pipeline
Fetches API and GraphQL test response data from Instana test pipeline
Data Source: http://reports-nfs.qe-auto-results.fyre.ibm.com/instana/reports/
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
BASE_URL = "http://reports-nfs.qe-auto-results.fyre.ibm.com/instana/reports/"
DATA_DIR = Path("/Users/jisnyvarghese/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd")

OUTPUT_JSON = DATA_DIR / "test_responses.json"
OUTPUT_CSV = DATA_DIR / "test_responses.csv"

print(f"✓ Configuration set")
print(f"  Base URL: {BASE_URL}")
print(f"  Data directory: {DATA_DIR}")


def fetch_url(url, timeout=30):
    """Fetch content from URL with error handling"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None


def parse_directory_listing(html_content, base_url):
    """Parse directory listing HTML to extract file/folder links"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href not in ['../', '../']:
            full_url = urljoin(base_url, href)
            links.append({
                'name': href.rstrip('/'),
                'url': full_url,
                'is_directory': href.endswith('/')
            })
    
    return links


def should_explore_directory(dir_name, current_depth, path_parts):
    """Determine if a directory should be explored based on the path pattern"""
    dir_lower = dir_name.lower()
    
    # Level 0: At root level, only explore 'preview' directories
    if current_depth == 0:
        return 'preview' in dir_lower and '+' in dir_lower
    
    # Level 1: Explore 'online' directories
    if current_depth == 1:
        return dir_lower == 'online'
    
    # Level 2: Explore 'e2e' directories
    if current_depth == 2:
        return dir_lower == 'e2e'
    
    # Level 3: Explore date directories (format: YYYYMMDD-HHMMSS)
    if current_depth == 3:
        return re.match(r'\d{8}-\d{6}', dir_name) is not None
    
    # Level 4: Explore 'api' directories
    if current_depth == 4:
        return dir_lower == 'api'
    
    # Level 5: Explore stan-api-fast and stan-api-graphql directories
    if current_depth == 5:
        return 'stan-api-fast' in dir_lower or 'stan-api-graphql' in dir_lower
    
    return False


def classify_api_type(path):
    """Classify if the path contains REST API or GraphQL tests"""
    path_lower = path.lower()
    if 'stan-api-graphql' in path_lower or 'graphql' in path_lower:
        return 'GraphQL'
    elif 'stan-api-fast' in path_lower or 'api' in path_lower:
        return 'REST'
    return 'Unknown'


def explore_directory(url, max_depth=7, current_depth=0, path_parts=None):
    """Recursively explore directory structure following specific path patterns"""
    if path_parts is None:
        path_parts = []
    
    if current_depth >= max_depth:
        return []
    
    indent = '  ' * current_depth
    print(f"{indent}📁 Exploring (depth {current_depth}): {url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]}")
    
    response = fetch_url(url)
    if not response:
        return []
    
    links = parse_directory_listing(response.text, url)
    all_files = []
    
    for link in links:
        if link['is_directory']:
            # Check if we should explore this directory
            if should_explore_directory(link['name'], current_depth, path_parts):
                new_path_parts = path_parts + [link['name']]
                sub_files = explore_directory(link['url'], max_depth, current_depth + 1, new_path_parts)
                all_files.extend(sub_files)
        else:
            # Only collect XML files in api test directories
            if link['name'].endswith('.xml'):
                api_type = classify_api_type(link['url'])
                print(f"{indent}  📄 Found [{api_type}]: {link['name']}")
                link['api_type'] = api_type
                link['path_parts'] = path_parts
                all_files.append(link)
    
    return all_files


def fetch_test_responses(file_list, max_files=100):
    """Fetch content from test response files"""
    test_data = []
    
    total_files = min(len(file_list), max_files)
    print(f"\n⏳ Fetching {total_files} test response files...\n")
    
    for i, file_info in enumerate(file_list[:max_files]):
        print(f"  [{i+1}/{total_files}] Fetching: {file_info['name']}")
        
        response = fetch_url(file_info['url'])
        if not response:
            continue
        
        content_type = response.headers.get('Content-Type', '')
        
        data_entry = {
            'filename': file_info['name'],
            'url': file_info['url'],
            'api_type': file_info.get('api_type', 'Unknown'),
            'content_type': content_type,
            'size_bytes': len(response.content),
            'fetched_at': datetime.now().isoformat(),
            'path_parts': file_info.get('path_parts', [])
        }
        
        # Parse XML content
        try:
            data_entry['content'] = response.text
            data_entry['format'] = 'xml'
        except Exception as e:
            data_entry['content'] = response.text
            data_entry['format'] = 'text'
            data_entry['parse_error'] = str(e)
        
        test_data.append(data_entry)
    
    print(f"\n✓ Fetched {len(test_data)} test response files")
    return test_data


def analyze_test_responses(responses):
    """Analyze fetched test responses"""
    if not responses:
        print("⚠️ No responses to analyze")
        return
    
    print("\n📊 Test Response Analysis:\n")
    
    # Format distribution
    formats = {}
    for resp in responses:
        fmt = resp.get('format', 'unknown')
        formats[fmt] = formats.get(fmt, 0) + 1
    
    print("Format Distribution:")
    for fmt, count in formats.items():
        print(f"  {fmt}: {count} files")
    
    # Size statistics
    sizes = [resp['size_bytes'] for resp in responses]
    print(f"\nSize Statistics:")
    print(f"  Total size: {sum(sizes):,} bytes ({sum(sizes)/1024/1024:.2f} MB)")
    print(f"  Average size: {sum(sizes)/len(sizes):,.0f} bytes")
    print(f"  Min size: {min(sizes):,} bytes")
    print(f"  Max size: {max(sizes):,} bytes")
    
    # API type distribution
    api_types = {}
    for resp in responses:
        api_type = resp.get('api_type', 'Unknown')
        api_types[api_type] = api_types.get(api_type, 0) + 1
    
    print(f"\nAPI Type Distribution:")
    for api_type, count in api_types.items():
        print(f"  {api_type}: {count} files")


def save_test_data(responses, json_path, csv_path):
    """Save test response data to JSON and CSV files"""
    if not responses:
        print("⚠️ No data to save")
        return None
    
    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved JSON data to: {json_path}")
    
    # Create CSV-friendly version
    csv_data = []
    for resp in responses:
        csv_row = {
            'filename': resp['filename'],
            'url': resp['url'],
            'api_type': resp.get('api_type', 'Unknown'),
            'format': resp.get('format', 'unknown'),
            'content_type': resp.get('content_type', ''),
            'size_bytes': resp['size_bytes'],
            'fetched_at': resp['fetched_at'],
            'has_content': bool(resp.get('content')),
            'parse_error': resp.get('parse_error', '')
        }
        csv_data.append(csv_row)
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved CSV metadata to: {csv_path}")
    
    return df


def extract_api_graphql_data(responses):
    """Separate and structure REST API and GraphQL responses"""
    rest_api_data = []
    graphql_data = []
    
    for resp in responses:
        api_type = resp.get('api_type', 'Unknown')
        
        if api_type == 'GraphQL':
            graphql_data.append({
                'filename': resp['filename'],
                'url': resp['url'],
                'type': 'GraphQL',
                'content': resp.get('content', ''),
                'size': resp['size_bytes']
            })
        elif api_type == 'REST':
            rest_api_data.append({
                'filename': resp['filename'],
                'url': resp['url'],
                'type': 'REST',
                'content': resp.get('content', ''),
                'size': resp['size_bytes']
            })
    
    return rest_api_data, graphql_data


def main():
    """Main execution function"""
    print("\n🔍 Starting directory exploration...\n")
    print("Following path pattern:")
    print("  preview+X.X.X/ → online/ → e2e/ → YYYYMMDD-HHMMSS/ → api/ → stan-api-*/\n")
    
    # Explore directory structure
    discovered_files = explore_directory(BASE_URL, max_depth=7)
    print(f"\n✓ Discovery complete: Found {len(discovered_files)} test response files")
    
    if not discovered_files:
        print("⚠️ No files discovered. The directory might be empty or require authentication.")
        return
    
    # Fetch test responses
    test_responses = fetch_test_responses(discovered_files, max_files=100)
    
    if not test_responses:
        print("⚠️ No data fetched")
        return
    
    # Analyze responses
    analyze_test_responses(test_responses)
    
    # Save data
    df_summary = save_test_data(test_responses, OUTPUT_JSON, OUTPUT_CSV)
    print(f"\n📁 Data saved successfully!")
    print(f"  JSON: {OUTPUT_JSON}")
    print(f"  CSV: {OUTPUT_CSV}")
    
    # Extract and save API-specific data
    rest_data, graphql_data = extract_api_graphql_data(test_responses)
    
    print(f"\n🔍 API Type Classification:")
    print(f"  REST API responses: {len(rest_data)}")
    print(f"  GraphQL responses: {len(graphql_data)}")
    
    if rest_data:
        rest_file = DATA_DIR / "rest_api_responses.json"
        with open(rest_file, 'w') as f:
            json.dump(rest_data, f, indent=2)
        print(f"  ✓ REST API data saved to: {rest_file}")
    
    if graphql_data:
        graphql_file = DATA_DIR / "graphql_responses.json"
        with open(graphql_file, 'w') as f:
            json.dump(graphql_data, f, indent=2)
        print(f"  ✓ GraphQL data saved to: {graphql_file}")
    
    # Display sample
    if test_responses:
        print("\n📋 Sample Test Response Data:\n")
        sample = test_responses[0]
        print(f"Filename: {sample['filename']}")
        print(f"API Type: {sample.get('api_type', 'Unknown')}")
        print(f"Format: {sample.get('format', 'unknown')}")
        print(f"Size: {sample['size_bytes']:,} bytes")
        print(f"\nContent Preview (first 500 chars):")
        
        content = sample.get('content', '')
        print(str(content)[:500] + "...")
    
    print("\n✅ Data fetching complete! Data is ready for AI assertion generation.")


if __name__ == "__main__":
    main()

# Made with Bob
