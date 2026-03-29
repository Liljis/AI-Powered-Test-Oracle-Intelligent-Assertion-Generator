package com.testoracle.generators

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.DisplayName

/**
 * Test suite for KotlinGenerator
 * Validates that the generator produces correct Kotlin test code
 */
class KotlinGeneratorTest {
    
    private val generator = KotlinGenerator()
    
    @Test
    @DisplayName("Should generate test code with NOT_NULL validation")
    fun testGenerateNotNullValidation() {
        val rules = listOf(
            ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("assertNotNull"))
        assertTrue(testCode.contains("response.id"))
        assertTrue(testCode.contains("ID must be present and non-null"))
    }
    
    @Test
    @DisplayName("Should generate test code with FORMAT validation")
    fun testGenerateFormatValidation() {
        val rules = listOf(
            ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("matches"))
        assertTrue(testCode.contains("Regex"))
        assertTrue(testCode.contains("email"))
    }
    
    @Test
    @DisplayName("Should generate test code with POSITIVE validation")
    fun testGeneratePositiveValidation() {
        val rules = listOf(
            ValidationRule("POSITIVE", "MEDIUM", "If numeric, must be positive (> 0)", "age")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("> 0"))
        assertTrue(testCode.contains("age"))
    }
    
    @Test
    @DisplayName("Should generate test code with multiple validations")
    fun testGenerateMultipleValidations() {
        val rules = listOf(
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id"),
            ValidationRule("FORMAT", "HIGH", "Validate email format", "email"),
            ValidationRule("POSITIVE", "MEDIUM", "Age must be positive", "age")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("assertNotNull"))
        assertTrue(testCode.contains("matches"))
        assertTrue(testCode.contains("> 0"))
        assertTrue(testCode.contains("id"))
        assertTrue(testCode.contains("email"))
        assertTrue(testCode.contains("age"))
    }
    
    @Test
    @DisplayName("Should generate proper test class structure")
    fun testGenerateTestClassStructure() {
        val rules = listOf(
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("import org.junit.jupiter.api.Test"))
        assertTrue(testCode.contains("class"))
        assertTrue(testCode.contains("Test"))
        assertTrue(testCode.contains("fun `test_get_users`()"))
        assertTrue(testCode.contains("given()"))
        assertTrue(testCode.contains(".get(\"/users\")"))
    }
    
    @Test
    @DisplayName("Should handle different HTTP methods")
    fun testDifferentHttpMethods() {
        val rules = listOf(
            ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id")
        )
        
        val getCode = generator.generateTestCode("/users", "GET", rules)
        val postCode = generator.generateTestCode("/users", "POST", rules)
        
        assertTrue(getCode.contains(".get(\"/users\")"))
        assertTrue(postCode.contains(".post(\"/users\")"))
    }
    
    @Test
    @DisplayName("Should generate ENUM validation")
    fun testGenerateEnumValidation() {
        val rules = listOf(
            ValidationRule("ENUM", "HIGH", "Must be one of allowed status values", "status")
        )
        
        val testCode = generator.generateTestCode("/users", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains("allowedValues"))
        assertTrue(testCode.contains("status"))
    }
    
    @Test
    @DisplayName("Should generate NON_NEGATIVE validation")
    fun testGenerateNonNegativeValidation() {
        val rules = listOf(
            ValidationRule("NON_NEGATIVE", "HIGH", "Must be >= 0", "count")
        )
        
        val testCode = generator.generateTestCode("/products", "GET", rules)
        
        assertNotNull(testCode)
        assertTrue(testCode.contains(">= 0"))
        assertTrue(testCode.contains("count"))
    }
}

// Made with Bob
