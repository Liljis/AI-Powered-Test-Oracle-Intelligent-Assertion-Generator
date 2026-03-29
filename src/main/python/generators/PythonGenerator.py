"""
Python Test Code Generator
Takes validation rules from Bob AI and generates Python test code
"""

from typing import List, Dict
import re


class PythonGenerator:
    """
    Python Test Code Generator
    Generates pytest test code from validation rules
    """
    
    def generate_test_code(
        self,
        endpoint: str,
        method: str,
        validation_rules: List['ValidationRule']
    ) -> str:
        """
        Generate Python test code from validation rules
        
        Args:
            endpoint: API endpoint (e.g., "/users")
            method: HTTP method (e.g., "GET")
            validation_rules: List of validation rules from Bob AI
            
        Returns:
            Generated Python test code as string
        """
        test_function_name = self._generate_test_function_name(endpoint, method)
        assertions = self._generate_assertions(validation_rules)
        
        return self._build_test_code(test_function_name, endpoint, method, assertions)
    
    def _generate_test_function_name(self, endpoint: str, method: str) -> str:
        """Generate test function name from endpoint and HTTP method"""
        clean_endpoint = re.sub(r'[^a-zA-Z0-9]', '_', endpoint.strip('/'))
        return f"test_{method.lower()}_{clean_endpoint}"
    
    def _generate_assertions(self, validation_rules: List['ValidationRule']) -> List[str]:
        """Generate Python assertions from validation rules"""
        return [self._generate_assertion(rule) for rule in validation_rules]
    
    def _generate_assertion(self, rule: 'ValidationRule') -> str:
        """Generate assertion based on validation rule type"""
        assertion_map = {
            'NOT_NULL': self._generate_not_null_assertion,
            'NOT_EMPTY': self._generate_not_empty_assertion,
            'FORMAT': self._generate_format_assertion,
            'POSITIVE': self._generate_positive_assertion,
            'NON_NEGATIVE': self._generate_non_negative_assertion,
            'ENUM': self._generate_enum_assertion,
            'TYPE_CHECK': self._generate_type_check_assertion,
            'PRESENCE': self._generate_presence_assertion,
            'RANGE': self._generate_range_assertion,
            'LENGTH': self._generate_length_assertion,
            'UNIQUE': self._generate_unique_assertion,
        }
        
        generator = assertion_map.get(rule.type, self._generate_generic_assertion)
        return generator(rule)
    
    def _generate_not_null_assertion(self, rule: 'ValidationRule') -> str:
        """Generate NOT_NULL assertion"""
        return f"""    # {rule.description}
    assert response['{rule.field_name}'] is not None, "{rule.field_name} should not be null" """
    
    def _generate_not_empty_assertion(self, rule: 'ValidationRule') -> str:
        """Generate NOT_EMPTY assertion"""
        return f"""    # {rule.description}
    assert len(response['{rule.field_name}']) > 0, "{rule.field_name} should not be empty" """
    
    def _generate_format_assertion(self, rule: 'ValidationRule') -> str:
        """Generate FORMAT assertion (e.g., email, UUID, ISO date)"""
        desc_lower = rule.description.lower()
        
        if 'email' in desc_lower:
            pattern = r'^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        elif 'uuid' in desc_lower:
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        elif 'iso 8601' in desc_lower:
            pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        else:
            pattern = r'.*'
        
        return f"""    # {rule.description}
    import re
    assert re.match(r'{pattern}', str(response['{rule.field_name}'])), \\
        "{rule.field_name} should match expected format" """
    
    def _generate_positive_assertion(self, rule: 'ValidationRule') -> str:
        """Generate POSITIVE assertion (value > 0)"""
        return f"""    # {rule.description}
    assert response['{rule.field_name}'] > 0, "{rule.field_name} should be positive" """
    
    def _generate_non_negative_assertion(self, rule: 'ValidationRule') -> str:
        """Generate NON_NEGATIVE assertion (value >= 0)"""
        return f"""    # {rule.description}
    assert response['{rule.field_name}'] >= 0, "{rule.field_name} should be non-negative" """
    
    def _generate_enum_assertion(self, rule: 'ValidationRule') -> str:
        """Generate ENUM assertion"""
        return f"""    # {rule.description}
    allowed_values = ['active', 'inactive', 'pending']  # TODO: Define actual enum values
    assert response['{rule.field_name}'] in allowed_values, \\
        "{rule.field_name} should be one of allowed values" """
    
    def _generate_type_check_assertion(self, rule: 'ValidationRule') -> str:
        """Generate TYPE_CHECK assertion"""
        return f"""    # {rule.description}
    assert response['{rule.field_name}'] is not None"""
    
    def _generate_presence_assertion(self, rule: 'ValidationRule') -> str:
        """Generate PRESENCE assertion"""
        return f"""    # {rule.description}
    assert '{rule.field_name}' in response, "{rule.field_name} should be present in response" """
    
    def _generate_range_assertion(self, rule: 'ValidationRule') -> str:
        """Generate RANGE assertion"""
        return f"""    # {rule.description}
    assert 0 <= response['{rule.field_name}'] <= 1000, \\
        "{rule.field_name} should be within valid range"  # TODO: Define actual range"""
    
    def _generate_length_assertion(self, rule: 'ValidationRule') -> str:
        """Generate LENGTH assertion"""
        return f"""    # {rule.description}
    assert len(str(response['{rule.field_name}'])) <= 254, \\
        "{rule.field_name} should not exceed maximum length"  # TODO: Define actual max length"""
    
    def _generate_unique_assertion(self, rule: 'ValidationRule') -> str:
        """Generate UNIQUE assertion"""
        return f"""    # {rule.description}
    # Note: Uniqueness validation requires database or collection check
    assert response['{rule.field_name}'] is not None"""
    
    def _generate_generic_assertion(self, rule: 'ValidationRule') -> str:
        """Generate generic assertion for unknown types"""
        return f"""    # {rule.description}
    assert response['{rule.field_name}'] is not None, "{rule.field_name} validation" """
    
    def _build_test_code(
        self,
        test_function_name: str,
        endpoint: str,
        method: str,
        assertions: List[str]
    ) -> str:
        """Build complete Python test code"""
        assertions_code = '\n\n'.join(assertions)
        
        return f'''"""
AI-Generated Test for {method} {endpoint}
Generated by Bob AI-Powered Test Oracle
"""

import pytest
import requests
import re
from typing import Dict, Any


def {test_function_name}():
    """Test {method} {endpoint} with AI-generated assertions"""
    # Execute API call
    response = requests.{method.lower()}(
        "http://localhost:8080{endpoint}",
        headers={{"Content-Type": "application/json"}}
    )
    
    # Verify status code
    assert response.status_code == 200, f"Expected status 200, got {{response.status_code}}"
    
    # Parse response
    response_data = response.json()
    
    # AI-Generated Assertions
{assertions_code}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


class ValidationRule:
    """
    Data class representing a validation rule from Bob AI
    """
    
    def __init__(self, type: str, priority: str, description: str, field_name: str):
        """
        Initialize validation rule
        
        Args:
            type: Validation type (e.g., "NOT_NULL", "FORMAT", "POSITIVE")
            priority: Priority level (e.g., "HIGH", "MEDIUM", "LOW")
            description: Human-readable description
            field_name: Field to validate
        """
        self.type = type
        self.priority = priority
        self.description = description
        self.field_name = field_name
    
    def __repr__(self):
        return f"ValidationRule(type={self.type}, field={self.field_name})"


# Example usage
if __name__ == "__main__":
    # Example validation rules
    rules = [
        ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id"),
        ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email"),
        ValidationRule("POSITIVE", "MEDIUM", "If numeric, must be positive (> 0)", "age"),
    ]
    
    generator = PythonGenerator()
    test_code = generator.generate_test_code("/users", "GET", rules)
    print(test_code)

# Made with Bob
