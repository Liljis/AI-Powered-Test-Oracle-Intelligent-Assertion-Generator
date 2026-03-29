"""
Historical Field Learner
Learns response field patterns from historical test data to predict fields for new endpoints
"""

import json
import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import xml.etree.ElementTree as ET


class HistoricalFieldLearner:
    """
    Learns from historical test data to predict response fields for endpoints
    """
    
    def __init__(self, historical_data_path='assets/test_responses.json'):
        self.historical_data_path = historical_data_path
        self.endpoint_field_map = defaultdict(lambda: defaultdict(int))  # endpoint_pattern -> {field: count}
        self.api_type_fields = defaultdict(lambda: defaultdict(int))  # api_type -> {field: count}
        self.resource_type_fields = defaultdict(lambda: defaultdict(int))  # resource_type -> {field: count}
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load and analyze historical test data"""
        try:
            with open(self.historical_data_path, 'r') as f:
                data = json.load(f)
            
            for record in data:
                self._analyze_test_record(record)
            
            print(f"✓ Loaded historical data: {len(self.endpoint_field_map)} endpoint patterns")
        except Exception as e:
            print(f"Warning: Could not load historical data: {e}")
    
    def _analyze_test_record(self, record: Dict):
        """Analyze a single test record to extract field patterns"""
        api_type = record.get('api_type', 'REST')
        content = record.get('content', '')
        
        # Extract fields from XML test results
        if content and content.strip().startswith('<?xml'):
            fields = self._extract_fields_from_xml(content)
            
            # Infer endpoint pattern from filename
            filename = record.get('filename', '')
            endpoint_pattern = self._infer_endpoint_pattern(filename)
            
            # Infer resource type
            resource_type = self._infer_resource_type(filename, endpoint_pattern)
            
            # Store field associations
            for field in fields:
                if endpoint_pattern:
                    self.endpoint_field_map[endpoint_pattern][field] += 1
                self.api_type_fields[api_type][field] += 1
                if resource_type:
                    self.resource_type_fields[resource_type][field] += 1
    
    def _extract_fields_from_xml(self, xml_content: str) -> Set[str]:
        """Extract field names from XML test results"""
        fields = set()
        
        try:
            root = ET.fromstring(xml_content)
            
            # Look for assertion patterns in test cases
            for testcase in root.findall('.//testcase'):
                name = testcase.get('name', '')
                
                # Extract field names from test names
                # Common patterns: "test_get_user_id", "validate_email_format", etc.
                field_patterns = [
                    r'test_\w+_(\w+)',  # test_get_field
                    r'validate_(\w+)',  # validate_field
                    r'assert_(\w+)',    # assert_field
                    r'check_(\w+)',     # check_field
                ]
                
                for pattern in field_patterns:
                    matches = re.findall(pattern, name, re.IGNORECASE)
                    fields.update(matches)
                
                # Look for field references in failure messages
                for failure in testcase.findall('.//failure'):
                    message = failure.get('message', '')
                    # Extract quoted field names
                    quoted_fields = re.findall(r'["\'](\w+)["\']', message)
                    fields.update(quoted_fields)
        
        except Exception as e:
            pass  # Silently skip malformed XML
        
        return fields
    
    def _infer_endpoint_pattern(self, filename: str) -> str:
        """Infer endpoint pattern from test filename"""
        # Remove file extension and test prefixes
        name = filename.replace('TEST-', '').replace('.xml', '')
        
        # Extract meaningful parts
        parts = name.split('.')
        if len(parts) > 2:
            # e.g., "com.instana.e2e.ActionHistoryTest" -> "ActionHistory"
            return parts[-1].replace('Test', '')
        
        return name
    
    def _infer_resource_type(self, filename: str, endpoint_pattern: str) -> str:
        """Infer resource type from filename and pattern"""
        text = (filename + ' ' + endpoint_pattern).lower()
        
        # Common resource types
        resource_types = {
            'user': ['user', 'account', 'profile'],
            'token': ['token', 'auth', 'credential'],
            'application': ['application', 'app', 'service'],
            'monitoring': ['monitoring', 'metric', 'trace', 'span'],
            'alert': ['alert', 'notification', 'channel'],
            'event': ['event', 'action', 'history'],
            'catalog': ['catalog', 'inventory', 'list'],
            'settings': ['settings', 'config', 'preference']
        }
        
        for resource_type, keywords in resource_types.items():
            if any(keyword in text for keyword in keywords):
                return resource_type
        
        return 'generic'
    
    def predict_fields(self, endpoint: str, method: str, api_type: str = 'REST') -> List[Dict[str, str]]:
        """
        Predict response fields for an endpoint based on historical data
        """
        predicted_fields = defaultdict(int)
        
        # Extract endpoint characteristics
        endpoint_lower = endpoint.lower()
        resource_type = self._detect_resource_type_from_endpoint(endpoint_lower)
        
        # Score fields from different sources
        
        # 1. Exact endpoint pattern match (HIGHEST weight - most specific)
        endpoint_pattern = self._extract_endpoint_pattern(endpoint)
        if endpoint_pattern in self.endpoint_field_map:
            for field, count in self.endpoint_field_map[endpoint_pattern].items():
                predicted_fields[field] += count * 10  # Highest priority for exact matches
        
        # 2. Resource type match (HIGH weight - learned from historical data)
        if resource_type in self.resource_type_fields:
            for field, count in self.resource_type_fields[resource_type].items():
                predicted_fields[field] += count * 5  # High priority for resource-specific learned data
        
        # 3. API type match (MEDIUM weight - general patterns)
        if api_type in self.api_type_fields:
            for field, count in self.api_type_fields[api_type].items():
                predicted_fields[field] += count * 2  # Medium priority for API-level patterns
        
        # 4. Method-filtered fields (LOW weight - only as fallback)
        # This now uses learned data primarily, with minimal fallback
        common_fields = self._get_common_fields_for_method(method, resource_type)
        for field in common_fields:
            # Only add small weight if field not already scored from historical data
            if field not in predicted_fields:
                predicted_fields[field] += 1  # Minimal weight for fallback fields
        
        # Sort by score and return top fields
        sorted_fields = sorted(predicted_fields.items(), key=lambda x: x[1], reverse=True)
        
        # Convert to field list with types
        result = []
        for field_name, score in sorted_fields[:10]:  # Top 10 fields
            field_type = self._infer_field_type(field_name)
            result.append({
                'name': field_name,
                'type': field_type,
                'confidence': min(score / 10.0, 1.0)  # Normalize to 0-1
            })
        
        return result
    
    def _detect_resource_type_from_endpoint(self, endpoint: str) -> str:
        """Detect resource type from endpoint path"""
        resource_keywords = {
            'token': ['token', 'auth', 'credential', 'oauth', 'jwt'],
            'user': ['user', 'account', 'profile', 'member', 'person'],
            'application': ['application', 'app', 'service', 'microservice'],
            'monitoring': ['monitoring', 'metric', 'trace', 'topology', 'span', 'infrastructure'],
            'alert': ['alert', 'notification', 'channel', 'alerting', 'alarm'],
            'event': ['event', 'action', 'history', 'activity', 'audit', 'specification'],
            'catalog': ['catalog', 'inventory', 'repository'],
            'settings': ['settings', 'config', 'preference', 'configuration'],
            'product': ['product', 'item', 'goods', 'merchandise'],
            'order': ['order', 'purchase', 'transaction', 'checkout']
        }
        
        # Check each resource type in priority order
        for resource_type, keywords in resource_keywords.items():
            if any(keyword in endpoint for keyword in keywords):
                return resource_type
        
        return 'generic'
    
    def _extract_endpoint_pattern(self, endpoint: str) -> str:
        """Extract pattern from endpoint for matching"""
        # Remove IDs and parameters
        pattern = re.sub(r'/\{[^}]+\}', '/{id}', endpoint)
        pattern = re.sub(r'/[0-9a-f-]{20,}', '/{id}', pattern)
        pattern = re.sub(r'/\d+', '/{id}', pattern)
        
        # Extract last meaningful part
        parts = [p for p in pattern.split('/') if p and p != '{id}']
        if parts:
            return parts[-1]
        
        return 'generic'
    
    def _get_common_fields_for_method(self, method: str, resource_type: str = 'generic') -> List[str]:
        """
        Get common fields based on HTTP method and resource type from LEARNED historical data
        Only uses minimal fallback if no historical data exists
        """
        # Try to get fields from learned historical data first
        learned_fields = []
        
        if resource_type in self.resource_type_fields:
            # Use learned fields for this resource type
            learned_fields = list(self.resource_type_fields[resource_type].keys())
        
        # If we have learned fields, filter them based on HTTP method
        if learned_fields:
            if method == 'POST':
                # Creation - exclude update-related fields
                return [f for f in learned_fields if 'updated' not in f.lower() and 'resolved' not in f.lower()]
            elif method in ['PUT', 'PATCH']:
                # Update - exclude creation-related fields (except id)
                return [f for f in learned_fields if 'created' not in f.lower() or f.lower() == 'id']
            elif method == 'DELETE':
                # Deletion - only id and status-related fields
                return [f for f in learned_fields if f.lower() in ['id', 'status', 'deletedat']]
            else:  # GET
                # Retrieval - all learned fields
                return learned_fields
        
        # Minimal fallback only if NO historical data exists
        # This ensures the system is truly dynamic and learns from data
        print(f"⚠ No historical data for resource type '{resource_type}', using minimal fallback")
        if method == 'POST':
            return ['id', 'createdAt']
        elif method in ['PUT', 'PATCH']:
            return ['id', 'updatedAt']
        elif method == 'DELETE':
            return ['id', 'status']
        else:  # GET
            return ['id', 'name']
    
    def _infer_field_type(self, field_name: str) -> str:
        """Infer field type from field name"""
        field_lower = field_name.lower()
        
        # Type inference rules
        if any(x in field_lower for x in ['id', 'uuid']):
            return 'String'
        elif any(x in field_lower for x in ['email', 'name', 'title', 'description']):
            return 'String'
        elif any(x in field_lower for x in ['count', 'total', 'number']):
            return 'Integer'
        elif any(x in field_lower for x in ['price', 'amount', 'cost']):
            return 'Double'
        elif any(x in field_lower for x in ['active', 'enabled', 'deleted']):
            return 'Boolean'
        elif any(x in field_lower for x in ['created', 'updated', 'deleted', 'timestamp', 'date', 'time']):
            return 'String'  # ISO 8601 timestamp
        elif any(x in field_lower for x in ['list', 'array', 'items', 'tags']):
            return 'Array'
        elif any(x in field_lower for x in ['config', 'settings', 'metadata', 'data']):
            return 'Object'
        else:
            return 'String'  # Default
    
    def get_statistics(self) -> Dict:
        """Get statistics about learned patterns"""
        return {
            'endpoint_patterns': len(self.endpoint_field_map),
            'api_types': len(self.api_type_fields),
            'resource_types': len(self.resource_type_fields),
            'total_unique_fields': len(set(
                field for fields in self.endpoint_field_map.values() for field in fields
            ))
        }


# Singleton instance
_learner = None

def get_field_learner() -> HistoricalFieldLearner:
    """Get singleton field learner instance"""
    global _learner
    if _learner is None:
        _learner = HistoricalFieldLearner()
    return _learner

# Made with Bob
