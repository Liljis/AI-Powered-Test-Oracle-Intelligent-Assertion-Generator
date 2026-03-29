#!/usr/bin/env python3
"""
AI-Powered Test Oracle CLI
Usage:
  python3 ai_oracle_cli.py <curl_command>
  python3 ai_oracle_cli.py <curl_command> --fields <json_fields>
  python3 ai_oracle_cli.py <curl_command> --generate <kotlin|java|python|all>

Examples:
  python3 ai_oracle_cli.py 'curl -X GET "https://api.example.com/users"'
  python3 ai_oracle_cli.py 'curl -X PUT "https://api.example.com/users/ID"' --fields '{"id":"string","name":"string","email":"string"}'
  python3 ai_oracle_cli.py 'curl -X GET "https://api.example.com/users"' --generate kotlin
  python3 ai_oracle_cli.py 'curl -X GET "https://api.example.com/users"' --generate all
"""

import sys
import re
import json
import urllib.request
import os

def parse_curl_command(curl_cmd):
    """Extract endpoint and method from curl command"""
    # Extract method - check both -X and --request
    method_match = re.search(r'-X\s+(\w+)', curl_cmd)
    if not method_match:
        method_match = re.search(r'--request\s+(\w+)', curl_cmd)
    method = method_match.group(1) if method_match else 'GET'
    
    # Extract URL - handle quoted URLs
    url_match = re.search(r'--url\s+["\']?([^"\']+)["\']?', curl_cmd)
    if not url_match:
        url_match = re.search(r'curl\s+(?:-X\s+\w+\s+)?["\']?([^"\']+)["\']?', curl_cmd)
    
    if not url_match:
        return None, None
    
    url = url_match.group(1).strip('"\'')
    
    # Extract path from URL
    path_match = re.search(r'https?://[^/]+(/[^\s?"\']*)', url)
    endpoint = path_match.group(1) if path_match else '/'
    
    return endpoint, method

def get_ai_validations(endpoint, method, response_fields=None):
    """Get AI-powered validations from Bob AI with all scenarios"""
    request_data = {
        'endpoint': endpoint,
        'method': method
    }
    
    # Add response fields if provided
    if response_fields:
        fields_list = []
        for field_name, field_type in response_fields.items():
            fields_list.append({
                'name': field_name,
                'type': field_type
            })
        request_data['fields'] = fields_list
    
    data = json.dumps(request_data).encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:5001/bob_generate_all_scenarios',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))

def print_validations(result, endpoint, method):
    """Print AI validations in README Quick Start format"""
    print()
    print('🤖 AI-Powered Test Oracle - Intelligent Assertion Generator')
    print('=' * 80)
    print(f'Endpoint: {method} {endpoint}')
    print(f'Source: {result.get("source", "Bob AI + ML Model")}')
    print('=' * 80)
    print()
    
    scenarios = result.get('scenarios', {})
    
    # Success Cases - Show only the main success test in README format
    success_cases = scenarios.get('success_cases', [])
    if success_cases:
        main_case = success_cases[0]
        print('✅ SUCCESS TEST CASE')
        print('─' * 80)
        print(f'Description: {main_case["description"]}')
        print()
        print(main_case['test_code'])
        print()
        print('─' * 80)
        print()
    
    # Show validation insights from Bob AI
    if 'field_predictions' in result:
        print('🧠 AI-GENERATED FIELD VALIDATIONS')
        print('─' * 80)
        fields = result['field_predictions']
        for field in fields[:7]:  # Show top 7 fields
            print(f"\n✓ Field: {field['name']} ({field['type']})")
            if 'validations' in field:
                for validation in field['validations'][:3]:  # Top 3 validations per field
                    print(f"  • {validation}")
        print()
        print('─' * 80)
        print()
    
    # Failure Cases - Compact summary
    failure_cases = scenarios.get('failure_cases', [])
    if failure_cases:
        print('❌ FAILURE TEST CASES')
        print('─' * 80)
        for i, case in enumerate(failure_cases, 1):
            print(f'{i}. {case["name"]} (Status: {case["status_code"]})')
            print(f'   {case["description"]}')
        print()
        print('─' * 80)
        print()
    
    # Edge Cases - Compact summary
    edge_cases = scenarios.get('edge_cases', [])
    if edge_cases:
        print('⚠️  EDGE TEST CASES')
        print('─' * 80)
        for i, case in enumerate(edge_cases, 1):
            print(f'{i}. {case["name"]} (Status: {case["status_code"]})')
            print(f'   {case["description"]}')
        print()
        print('─' * 80)
        print()
    
    # Summary
    print('📊 SUMMARY')
    print('─' * 80)
    print(f'Total test cases generated: {result.get("total_tests", 0)}')
    print(f'  ✓ Success cases: {len(success_cases)}')
    print(f'  ✗ Failure cases: {len(failure_cases)}')
    print(f'  ⚠  Edge cases: {len(edge_cases)}')
    print()
    print('💡 Key Benefits:')
    print('  • No hardcoded values - all assertions from AI model')
    print('  • Semantic field understanding')
    print('  • Business logic validation')
    print('  • Comprehensive test coverage')
    print('=' * 80)
    print()

def generate_test_code(endpoint, method, language):
    """Generate test code in specified language"""
    request_data = {
        'endpoint': endpoint,
        'method': method,
        'language': language
    }
    
    data = json.dumps(request_data).encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:5001/generate_test_code',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def save_test_file(test_code, language, endpoint, method):
    """Save generated test code to appropriate file"""
    # Create tests directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    # Generate filename based on endpoint and method
    clean_endpoint = endpoint.replace('/', '_').strip('_')
    test_name = f"{method.lower()}_{clean_endpoint}"
    
    # Determine file extension and path
    if language == 'kotlin':
        filename = f"tests/{test_name.title().replace('_', '')}Test.kt"
    elif language == 'java':
        filename = f"tests/{test_name.title().replace('_', '')}Test.java"
    else:  # python
        filename = f"tests/test_{test_name}.py"
    
    # Write test code to file
    with open(filename, 'w') as f:
        f.write(test_code)
    
    return filename

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 ai_oracle_cli.py "<curl_command>" [--generate <kotlin|java|python|all>]')
        print()
        print('Examples:')
        print('  python3 ai_oracle_cli.py "curl --request GET --url https://api.example.com/users"')
        print('  python3 ai_oracle_cli.py "curl -X GET https://api.example.com/users" --generate kotlin')
        print('  python3 ai_oracle_cli.py "curl -X GET https://api.example.com/users" --generate all')
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    generate_language = None
    
    # Check for --generate flag
    if '--generate' in args:
        generate_idx = args.index('--generate')
        if generate_idx + 1 < len(args):
            generate_language = args[generate_idx + 1].lower()
            # Remove --generate and its value from args
            args = args[:generate_idx] + args[generate_idx + 2:]
        else:
            print('Error: --generate flag requires a language argument (kotlin, java, python, or all)')
            sys.exit(1)
    
    curl_cmd = ' '.join(args)
    endpoint, method = parse_curl_command(curl_cmd)
    
    if not endpoint:
        print('Error: Could not parse curl command')
        sys.exit(1)
    
    try:
        # If --generate flag is provided, generate test code
        if generate_language:
            if generate_language not in ['kotlin', 'java', 'python', 'all']:
                print(f'Error: Invalid language "{generate_language}". Must be kotlin, java, python, or all')
                sys.exit(1)
            
            print(f'\n🔧 Generating test code for {method} {endpoint}...\n')
            
            languages = ['kotlin', 'java', 'python'] if generate_language == 'all' else [generate_language]
            
            for lang in languages:
                try:
                    print(f'Generating {lang.upper()} test...')
                    result = generate_test_code(endpoint, method, lang)
                    
                    if 'error' in result:
                        print(f'  ❌ Error: {result["error"]}')
                        continue
                    
                    # Save test code to file
                    filename = save_test_file(result['test_code'], lang, endpoint, method)
                    print(f'  ✅ Test file created: {filename}')
                    print(f'     Validations: {result.get("validation_rules_count", 0)}')
                    
                except Exception as e:
                    print(f'  ❌ Error generating {lang} test: {e}')
            
            print('\n✨ Test generation complete!')
        else:
            # Default behavior: show validation rules
            result = get_ai_validations(endpoint, method)
            print_validations(result, endpoint, method)
            
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

# Made with Bob
