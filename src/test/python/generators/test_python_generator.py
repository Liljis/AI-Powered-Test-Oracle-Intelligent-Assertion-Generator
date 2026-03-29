"""
Test suite for PythonGenerator
Validates that the generator produces correct Python test code
"""

import pytest
import sys
import os

# Add parent directory to path to import PythonGenerator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../main/python'))

from generators.PythonGenerator import PythonGenerator, ValidationRule


class TestPythonGenerator:
    """Test cases for PythonGenerator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = PythonGenerator()
    
    def test_generate_not_null_validation(self):
        """Should generate test code with NOT_NULL validation"""
        rules = [
            ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "assert response['id'] is not None" in test_code
        assert "ID must be present and non-null" in test_code
    
    def test_generate_format_validation(self):
        """Should generate test code with FORMAT validation"""
        rules = [
            ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "re.match" in test_code
        assert "email" in test_code
    
    def test_generate_positive_validation(self):
        """Should generate test code with POSITIVE validation"""
        rules = [
            ValidationRule("POSITIVE", "MEDIUM", "If numeric, must be positive (> 0)", "age")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "> 0" in test_code
        assert "age" in test_code
    
    def test_generate_multiple_validations(self):
        """Should generate test code with multiple validations"""
        rules = [
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id"),
            ValidationRule("FORMAT", "HIGH", "Validate email format", "email"),
            ValidationRule("POSITIVE", "MEDIUM", "Age must be positive", "age")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "is not None" in test_code
        assert "re.match" in test_code
        assert "> 0" in test_code
        assert "id" in test_code
        assert "email" in test_code
        assert "age" in test_code
    
    def test_generate_test_function_structure(self):
        """Should generate proper test function structure"""
        rules = [
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "import pytest" in test_code
        assert "import requests" in test_code
        assert "def test_get_users():" in test_code
        assert "requests.get" in test_code
        assert 'http://localhost:8080/users' in test_code
    
    def test_different_http_methods(self):
        """Should handle different HTTP methods"""
        rules = [
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        ]
        
        get_code = self.generator.generate_test_code("/users", "GET", rules)
        post_code = self.generator.generate_test_code("/users", "POST", rules)
        
        assert "requests.get" in get_code
        assert "requests.post" in post_code
    
    def test_generate_enum_validation(self):
        """Should generate ENUM validation"""
        rules = [
            ValidationRule("ENUM", "HIGH", "Must be one of allowed status values", "status")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "allowed_values" in test_code
        assert "in allowed_values" in test_code
        assert "status" in test_code
    
    def test_generate_non_negative_validation(self):
        """Should generate NON_NEGATIVE validation"""
        rules = [
            ValidationRule("NON_NEGATIVE", "HIGH", "Must be >= 0", "count")
        ]
        
        test_code = self.generator.generate_test_code("/products", "GET", rules)
        
        assert test_code is not None
        assert ">= 0" in test_code
        assert "count" in test_code
    
    def test_generate_presence_validation(self):
        """Should generate PRESENCE validation"""
        rules = [
            ValidationRule("PRESENCE", "HIGH", "Verify field exists in response", "username")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "'username' in response" in test_code
    
    def test_generate_length_validation(self):
        """Should generate LENGTH validation"""
        rules = [
            ValidationRule("LENGTH", "MEDIUM", "Maximum 254 characters per RFC 5321", "email")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "len(str(response['email']))" in test_code
        assert "<= 254" in test_code
    
    def test_generate_not_empty_validation(self):
        """Should generate NOT_EMPTY validation"""
        rules = [
            ValidationRule("NOT_EMPTY", "HIGH", "Email must not be null or empty", "email")
        ]
        
        test_code = self.generator.generate_test_code("/users", "GET", rules)
        
        assert test_code is not None
        assert "len(response['email']) > 0" in test_code
    
    def test_generate_range_validation(self):
        """Should generate RANGE validation"""
        rules = [
            ValidationRule("RANGE", "MEDIUM", "Check reasonable price range", "price")
        ]
        
        test_code = self.generator.generate_test_code("/products", "GET", rules)
        
        assert test_code is not None
        assert "0 <= response['price'] <= 1000" in test_code
    
    def test_validation_rule_repr(self):
        """Should have proper string representation"""
        rule = ValidationRule("NOT_NULL", "HIGH", "Test description", "test_field")
        
        repr_str = repr(rule)
        
        assert "ValidationRule" in repr_str
        assert "NOT_NULL" in repr_str
        assert "test_field" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
