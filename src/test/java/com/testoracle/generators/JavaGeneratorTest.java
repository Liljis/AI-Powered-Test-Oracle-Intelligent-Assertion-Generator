package com.testoracle.generators;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;

/**
 * Test suite for JavaGenerator
 * Validates that the generator produces correct Java test code
 */
public class JavaGeneratorTest {
    
    private final JavaGenerator generator = new JavaGenerator();
    
    @Test
    @DisplayName("Should generate test code with NOT_NULL validation")
    public void testGenerateNotNullValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("assertNotNull"));
        assertTrue(testCode.contains("response.get(\"id\")"));
        assertTrue(testCode.contains("ID must be present and non-null"));
    }
    
    @Test
    @DisplayName("Should generate test code with FORMAT validation")
    public void testGenerateFormatValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("matches"));
        assertTrue(testCode.contains("email"));
    }
    
    @Test
    @DisplayName("Should generate test code with POSITIVE validation")
    public void testGeneratePositiveValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("POSITIVE", "MEDIUM", "If numeric, must be positive (> 0)", "age")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("> 0"));
        assertTrue(testCode.contains("age"));
    }
    
    @Test
    @DisplayName("Should generate test code with multiple validations")
    public void testGenerateMultipleValidations() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id"),
            new ValidationRule("FORMAT", "HIGH", "Validate email format", "email"),
            new ValidationRule("POSITIVE", "MEDIUM", "Age must be positive", "age")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("assertNotNull"));
        assertTrue(testCode.contains("matches"));
        assertTrue(testCode.contains("> 0"));
        assertTrue(testCode.contains("id"));
        assertTrue(testCode.contains("email"));
        assertTrue(testCode.contains("age"));
    }
    
    @Test
    @DisplayName("Should generate proper test class structure")
    public void testGenerateTestClassStructure() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("import org.junit.jupiter.api.Test"));
        assertTrue(testCode.contains("public class"));
        assertTrue(testCode.contains("Test"));
        assertTrue(testCode.contains("public void test_get_users()"));
        assertTrue(testCode.contains("RestAssured.given()"));
        assertTrue(testCode.contains(".get(\"/users\")"));
    }
    
    @Test
    @DisplayName("Should handle different HTTP methods")
    public void testDifferentHttpMethods() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        );
        
        String getCode = generator.generateTestCode("/users", "GET", rules);
        String postCode = generator.generateTestCode("/users", "POST", rules);
        
        assertTrue(getCode.contains(".get(\"/users\")"));
        assertTrue(postCode.contains(".post(\"/users\")"));
    }
    
    @Test
    @DisplayName("Should generate ENUM validation")
    public void testGenerateEnumValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("ENUM", "HIGH", "Must be one of allowed status values", "status")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("allowedValues"));
        assertTrue(testCode.contains("Arrays.asList"));
        assertTrue(testCode.contains("status"));
    }
    
    @Test
    @DisplayName("Should generate NON_NEGATIVE validation")
    public void testGenerateNonNegativeValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NON_NEGATIVE", "HIGH", "Must be >= 0", "count")
        );
        
        String testCode = generator.generateTestCode("/products", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains(">= 0"));
        assertTrue(testCode.contains("count"));
    }
    
    @Test
    @DisplayName("Should generate PRESENCE validation")
    public void testGeneratePresenceValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("PRESENCE", "HIGH", "Verify field exists in response", "username")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("containsKey"));
        assertTrue(testCode.contains("username"));
    }
    
    @Test
    @DisplayName("Should generate LENGTH validation")
    public void testGenerateLengthValidation() {
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("LENGTH", "MEDIUM", "Maximum 254 characters per RFC 5321", "email")
        );
        
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        assertNotNull(testCode);
        assertTrue(testCode.contains("length()"));
        assertTrue(testCode.contains("<= 254"));
    }
}

// Made with Bob
