package com.testoracle.generators

/**
 * Kotlin Test Code Generator
 * Takes validation rules from Bob AI and generates Kotlin test code
 */
class KotlinGenerator {
    
    /**
     * Generate Kotlin test code from validation rules
     * 
     * @param endpoint API endpoint (e.g., "/users")
     * @param method HTTP method (e.g., "GET")
     * @param validationRules List of validation rules from Bob AI
     * @return Generated Kotlin test code as String
     */
    fun generateTestCode(
        endpoint: String,
        method: String,
        validationRules: List<ValidationRule>
    ): String {
        val testMethodName = generateTestMethodName(endpoint, method)
        val assertions = generateAssertions(validationRules)
        
        return buildTestCode(testMethodName, endpoint, method, assertions)
    }
    
    /**
     * Generate test method name from endpoint and HTTP method
     */
    private fun generateTestMethodName(endpoint: String, method: String): String {
        val cleanEndpoint = endpoint
            .trim('/')
            .replace(Regex("[^a-zA-Z0-9]"), "_")
        return "test_${method.lowercase()}_${cleanEndpoint}"
    }
    
    /**
     * Generate Kotlin assertions from validation rules
     */
    private fun generateAssertions(validationRules: List<ValidationRule>): List<String> {
        return validationRules.map { rule ->
            when (rule.type) {
                "NOT_NULL" -> generateNotNullAssertion(rule)
                "NOT_EMPTY" -> generateNotEmptyAssertion(rule)
                "FORMAT" -> generateFormatAssertion(rule)
                "POSITIVE" -> generatePositiveAssertion(rule)
                "NON_NEGATIVE" -> generateNonNegativeAssertion(rule)
                "ENUM" -> generateEnumAssertion(rule)
                "TYPE_CHECK" -> generateTypeCheckAssertion(rule)
                "PRESENCE" -> generatePresenceAssertion(rule)
                "RANGE" -> generateRangeAssertion(rule)
                "LENGTH" -> generateLengthAssertion(rule)
                "UNIQUE" -> generateUniqueAssertion(rule)
                else -> generateGenericAssertion(rule)
            }
        }
    }
    
    /**
     * Generate NOT_NULL assertion
     */
    private fun generateNotNullAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertNotNull(response.${rule.fieldName}, "${rule.fieldName} should not be null")
        """.trimIndent()
    }
    
    /**
     * Generate NOT_EMPTY assertion
     */
    private fun generateNotEmptyAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(response.${rule.fieldName}.isNotEmpty(), "${rule.fieldName} should not be empty")
        """.trimIndent()
    }
    
    /**
     * Generate FORMAT assertion (e.g., email, UUID, ISO date)
     */
    private fun generateFormatAssertion(rule: ValidationRule): String {
        val pattern = when {
            rule.description.contains("email", ignoreCase = true) -> 
                "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
            rule.description.contains("UUID", ignoreCase = true) -> 
                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            rule.description.contains("ISO 8601", ignoreCase = true) -> 
                "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"
            else -> ".*"
        }
        
        return """
        // ${rule.description}
        assertTrue(
            response.${rule.fieldName}.matches(Regex("$pattern")),
            "${rule.fieldName} should match expected format"
        )
        """.trimIndent()
    }
    
    /**
     * Generate POSITIVE assertion (value > 0)
     */
    private fun generatePositiveAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(response.${rule.fieldName} > 0, "${rule.fieldName} should be positive")
        """.trimIndent()
    }
    
    /**
     * Generate NON_NEGATIVE assertion (value >= 0)
     */
    private fun generateNonNegativeAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(response.${rule.fieldName} >= 0, "${rule.fieldName} should be non-negative")
        """.trimIndent()
    }
    
    /**
     * Generate ENUM assertion
     */
    private fun generateEnumAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        val allowedValues = listOf("active", "inactive", "pending") // TODO: Define actual enum values
        assertTrue(
            response.${rule.fieldName} in allowedValues,
            "${rule.fieldName} should be one of allowed values"
        )
        """.trimIndent()
    }
    
    /**
     * Generate TYPE_CHECK assertion
     */
    private fun generateTypeCheckAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertNotNull(response.${rule.fieldName})
        """.trimIndent()
    }
    
    /**
     * Generate PRESENCE assertion
     */
    private fun generatePresenceAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(response.containsKey("${rule.fieldName}"), "${rule.fieldName} should be present in response")
        """.trimIndent()
    }
    
    /**
     * Generate RANGE assertion
     */
    private fun generateRangeAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(
            response.${rule.fieldName} in 0..1000, // TODO: Define actual range
            "${rule.fieldName} should be within valid range"
        )
        """.trimIndent()
    }
    
    /**
     * Generate LENGTH assertion
     */
    private fun generateLengthAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertTrue(
            response.${rule.fieldName}.length <= 254, // TODO: Define actual max length
            "${rule.fieldName} should not exceed maximum length"
        )
        """.trimIndent()
    }
    
    /**
     * Generate UNIQUE assertion
     */
    private fun generateUniqueAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        // Note: Uniqueness validation requires database or collection check
        assertNotNull(response.${rule.fieldName})
        """.trimIndent()
    }
    
    /**
     * Generate generic assertion for unknown types
     */
    private fun generateGenericAssertion(rule: ValidationRule): String {
        return """
        // ${rule.description}
        assertNotNull(response.${rule.fieldName}, "${rule.fieldName} validation")
        """.trimIndent()
    }
    
    /**
     * Build complete Kotlin test code
     */
    private fun buildTestCode(
        testMethodName: String,
        endpoint: String,
        method: String,
        assertions: List<String>
    ): String {
        val assertionsCode = assertions.joinToString("\n\n        ")
        
        return """
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import io.restassured.RestAssured.*
import io.restassured.http.ContentType

/**
 * AI-Generated Test for $method $endpoint
 * Generated by Bob AI-Powered Test Oracle
 */
class ${testMethodName.split("_").joinToString("") { it.capitalize() }}Test {
    
    @Test
    fun `$testMethodName`() {
        // Execute API call
        val response = given()
            .contentType(ContentType.JSON)
            .`when`()
            .${method.lowercase()}("$endpoint")
            .then()
            .statusCode(200)
            .extract()
            .response()
        
        // AI-Generated Assertions
        $assertionsCode
    }
}
""".trimIndent()
    }
}

/**
 * Data class representing a validation rule from Bob AI
 */
data class ValidationRule(
    val type: String,           // e.g., "NOT_NULL", "FORMAT", "POSITIVE"
    val priority: String,       // e.g., "HIGH", "MEDIUM", "LOW"
    val description: String,    // Human-readable description
    val fieldName: String       // Field to validate
)

// Made with Bob
