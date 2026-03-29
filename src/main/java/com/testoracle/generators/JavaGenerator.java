package com.testoracle.generators;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Java Test Code Generator
 * Takes validation rules from Bob AI and generates Java test code
 */
public class JavaGenerator {
    
    /**
     * Generate Java test code from validation rules
     * 
     * @param endpoint API endpoint (e.g., "/users")
     * @param method HTTP method (e.g., "GET")
     * @param validationRules List of validation rules from Bob AI
     * @return Generated Java test code as String
     */
    public String generateTestCode(
        String endpoint,
        String method,
        List<ValidationRule> validationRules
    ) {
        String testMethodName = generateTestMethodName(endpoint, method);
        List<String> assertions = generateAssertions(validationRules);
        
        return buildTestCode(testMethodName, endpoint, method, assertions);
    }
    
    /**
     * Generate test method name from endpoint and HTTP method
     */
    private String generateTestMethodName(String endpoint, String method) {
        String cleanEndpoint = endpoint
            .trim()
            .replaceAll("^/|/$", "")
            .replaceAll("[^a-zA-Z0-9]", "_");
        return "test_" + method.toLowerCase() + "_" + cleanEndpoint;
    }
    
    /**
     * Generate Java assertions from validation rules
     */
    private List<String> generateAssertions(List<ValidationRule> validationRules) {
        return validationRules.stream()
            .map(this::generateAssertion)
            .collect(Collectors.toList());
    }
    
    /**
     * Generate assertion based on validation rule type
     */
    private String generateAssertion(ValidationRule rule) {
        switch (rule.getType()) {
            case "NOT_NULL":
                return generateNotNullAssertion(rule);
            case "NOT_EMPTY":
                return generateNotEmptyAssertion(rule);
            case "FORMAT":
                return generateFormatAssertion(rule);
            case "POSITIVE":
                return generatePositiveAssertion(rule);
            case "NON_NEGATIVE":
                return generateNonNegativeAssertion(rule);
            case "ENUM":
                return generateEnumAssertion(rule);
            case "TYPE_CHECK":
                return generateTypeCheckAssertion(rule);
            case "PRESENCE":
                return generatePresenceAssertion(rule);
            case "RANGE":
                return generateRangeAssertion(rule);
            case "LENGTH":
                return generateLengthAssertion(rule);
            case "UNIQUE":
                return generateUniqueAssertion(rule);
            default:
                return generateGenericAssertion(rule);
        }
    }
    
    /**
     * Generate NOT_NULL assertion
     */
    private String generateNotNullAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertNotNull(response.get(\"%s\"), \"%s should not be null\");",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate NOT_EMPTY assertion
     */
    private String generateNotEmptyAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertFalse(response.get(\"%s\").toString().isEmpty(), \"%s should not be empty\");",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate FORMAT assertion (e.g., email, UUID, ISO date)
     */
    private String generateFormatAssertion(ValidationRule rule) {
        String pattern;
        String desc = rule.getDescription().toLowerCase();
        
        if (desc.contains("email")) {
            pattern = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$";
        } else if (desc.contains("uuid")) {
            pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$";
        } else if (desc.contains("iso 8601")) {
            pattern = "^\\\\d{4}-\\\\d{2}-\\\\d{2}T\\\\d{2}:\\\\d{2}:\\\\d{2}";
        } else {
            pattern = ".*";
        }
        
        return String.format(
            "        // %s\n" +
            "        assertTrue(\n" +
            "            response.get(\"%s\").toString().matches(\"%s\"),\n" +
            "            \"%s should match expected format\"\n" +
            "        );",
            rule.getDescription(),
            rule.getFieldName(),
            pattern,
            rule.getFieldName()
        );
    }
    
    /**
     * Generate POSITIVE assertion (value > 0)
     */
    private String generatePositiveAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertTrue(\n" +
            "            Integer.parseInt(response.get(\"%s\").toString()) > 0,\n" +
            "            \"%s should be positive\"\n" +
            "        );",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate NON_NEGATIVE assertion (value >= 0)
     */
    private String generateNonNegativeAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertTrue(\n" +
            "            Integer.parseInt(response.get(\"%s\").toString()) >= 0,\n" +
            "            \"%s should be non-negative\"\n" +
            "        );",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate ENUM assertion
     */
    private String generateEnumAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        List<String> allowedValues = Arrays.asList(\"active\", \"inactive\", \"pending\"); // TODO: Define actual enum values\n" +
            "        assertTrue(\n" +
            "            allowedValues.contains(response.get(\"%s\").toString()),\n" +
            "            \"%s should be one of allowed values\"\n" +
            "        );",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate TYPE_CHECK assertion
     */
    private String generateTypeCheckAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertNotNull(response.get(\"%s\"));",
            rule.getDescription(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate PRESENCE assertion
     */
    private String generatePresenceAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertTrue(response.containsKey(\"%s\"), \"%s should be present in response\");",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate RANGE assertion
     */
    private String generateRangeAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        int value = Integer.parseInt(response.get(\"%s\").toString());\n" +
            "        assertTrue(value >= 0 && value <= 1000, \"%s should be within valid range\"); // TODO: Define actual range",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate LENGTH assertion
     */
    private String generateLengthAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertTrue(\n" +
            "            response.get(\"%s\").toString().length() <= 254, // TODO: Define actual max length\n" +
            "            \"%s should not exceed maximum length\"\n" +
            "        );",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate UNIQUE assertion
     */
    private String generateUniqueAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        // Note: Uniqueness validation requires database or collection check\n" +
            "        assertNotNull(response.get(\"%s\"));",
            rule.getDescription(),
            rule.getFieldName()
        );
    }
    
    /**
     * Generate generic assertion for unknown types
     */
    private String generateGenericAssertion(ValidationRule rule) {
        return String.format(
            "        // %s\n" +
            "        assertNotNull(response.get(\"%s\"), \"%s validation\");",
            rule.getDescription(),
            rule.getFieldName(),
            rule.getFieldName()
        );
    }
    
    /**
     * Build complete Java test code
     */
    private String buildTestCode(
        String testMethodName,
        String endpoint,
        String method,
        List<String> assertions
    ) {
        String assertionsCode = String.join("\n\n", assertions);
        String className = toCamelCase(testMethodName) + "Test";
        
        return String.format(
            "import org.junit.jupiter.api.Test;\n" +
            "import static org.junit.jupiter.api.Assertions.*;\n" +
            "import io.restassured.RestAssured;\n" +
            "import io.restassured.http.ContentType;\n" +
            "import io.restassured.response.Response;\n" +
            "import java.util.Arrays;\n" +
            "import java.util.List;\n" +
            "import java.util.Map;\n\n" +
            "/**\n" +
            " * AI-Generated Test for %s %s\n" +
            " * Generated by Bob AI-Powered Test Oracle\n" +
            " */\n" +
            "public class %s {\n\n" +
            "    @Test\n" +
            "    public void %s() {\n" +
            "        // Execute API call\n" +
            "        Response response = RestAssured.given()\n" +
            "            .contentType(ContentType.JSON)\n" +
            "            .when()\n" +
            "            .%s(\"%s\")\n" +
            "            .then()\n" +
            "            .statusCode(200)\n" +
            "            .extract()\n" +
            "            .response();\n\n" +
            "        Map<String, Object> responseBody = response.jsonPath().getMap(\"$\");\n\n" +
            "        // AI-Generated Assertions\n" +
            "%s\n" +
            "    }\n" +
            "}\n",
            method,
            endpoint,
            className,
            testMethodName,
            method.toLowerCase(),
            endpoint,
            assertionsCode
        );
    }
    
    /**
     * Convert snake_case to CamelCase
     */
    private String toCamelCase(String input) {
        String[] parts = input.split("_");
        StringBuilder result = new StringBuilder();
        for (String part : parts) {
            if (!part.isEmpty()) {
                result.append(Character.toUpperCase(part.charAt(0)))
                      .append(part.substring(1).toLowerCase());
            }
        }
        return result.toString();
    }
}

/**
 * Data class representing a validation rule from Bob AI
 */
class ValidationRule {
    private String type;        // e.g., "NOT_NULL", "FORMAT", "POSITIVE"
    private String priority;    // e.g., "HIGH", "MEDIUM", "LOW"
    private String description; // Human-readable description
    private String fieldName;   // Field to validate
    
    public ValidationRule(String type, String priority, String description, String fieldName) {
        this.type = type;
        this.priority = priority;
        this.description = description;
        this.fieldName = fieldName;
    }
    
    public String getType() { return type; }
    public String getPriority() { return priority; }
    public String getDescription() { return description; }
    public String getFieldName() { return fieldName; }
}

// Made with Bob
