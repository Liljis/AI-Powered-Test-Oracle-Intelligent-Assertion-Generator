package com.testoracle.examples

import com.testoracle.ai.bob.BobAIConnection
import com.testoracle.ai.bob.BobAIQuestions

/**
 * Simple example using Bob AI (Roo Code) - No credentials required!
 * 
 * This demonstrates how to use Bob AI for intelligent test assertion generation
 * without needing external API keys or services.
 */
fun main() {
    println("=".repeat(60))
    println("Bob AI Integration Example - No Credentials Required!")
    println("=".repeat(60))
    
    // Initialize Bob AI - No credentials needed!
    val bob = BobAIConnection()
    
    // Connect to Bob
    println("\n1. Connecting to Bob AI...")
    if (!bob.connect()) {
        println("Failed to connect to Bob AI")
        return
    }
    
    val questions = BobAIQuestions(bob)
    
    // Example 1: Analyze email field
    println("\n" + "=".repeat(60))
    println("Example 1: Email Field Analysis")
    println("=".repeat(60))
    
    val emailValidations = questions.askValidationRules(
        fieldName = "email",
        fieldType = "String",
        apiType = "REST",
        sampleValue = "user@example.com"
    )
    
    println("\nField: email")
    println("Validation Rules:")
    emailValidations.rules.forEach { rule ->
        println("  [${rule.priority}] ${rule.type}: ${rule.description}")
    }
    println("\nConfidence: ${String.format("%.2f%%", emailValidations.confidence * 100)}")
    
    // Example 2: Analyze user ID field
    println("\n" + "=".repeat(60))
    println("Example 2: User ID Field Analysis")
    println("=".repeat(60))
    
    val userIdValidations = questions.askValidationRules(
        fieldName = "userId",
        fieldType = "UUID",
        apiType = "REST",
        sampleValue = "123e4567-e89b-12d3-a456-426614174000"
    )
    
    println("\nField: userId")
    println("Validation Rules:")
    userIdValidations.rules.forEach { rule ->
        println("  [${rule.priority}] ${rule.type}: ${rule.description}")
    }
    
    // Example 3: Analyze timestamp field
    println("\n" + "=".repeat(60))
    println("Example 3: Timestamp Field Analysis")
    println("=".repeat(60))
    
    val timestampValidations = questions.askValidationRules(
        fieldName = "createdAt",
        fieldType = "DateTime",
        apiType = "REST",
        sampleValue = "2024-01-01T00:00:00Z"
    )
    
    println("\nField: createdAt")
    println("Validation Rules:")
    timestampValidations.rules.forEach { rule ->
        println("  [${rule.priority}] ${rule.type}: ${rule.description}")
    }
    
    // Example 4: Field meaning analysis
    println("\n" + "=".repeat(60))
    println("Example 4: Understanding Field Meaning")
    println("=".repeat(60))
    
    val emailMeaning = questions.askFieldMeaning(
        fieldName = "email",
        fieldType = "String",
        apiType = "REST"
    )
    
    println("\nField: email")
    println("Meaning: ${emailMeaning.meaning}")
    println("\nUse Cases:")
    emailMeaning.useCases.take(3).forEach { println("  - $it") }
    
    // Example 5: Business logic analysis
    println("\n" + "=".repeat(60))
    println("Example 5: Business Logic Analysis")
    println("=".repeat(60))
    
    val statusLogic = questions.askBusinessLogic(
        fieldName = "status",
        relatedFields = listOf("orderId", "paymentStatus"),
        operation = "update",
        apiType = "REST"
    )
    
    println("\nField: status")
    println("Constraints:")
    statusLogic.constraints.take(3).forEach { println("  - $it") }
    
    // Example 6: GraphQL validation
    println("\n" + "=".repeat(60))
    println("Example 6: GraphQL Field Validation")
    println("=".repeat(60))
    
    val graphqlValidation = questions.askGraphQLValidations(
        fieldName = "posts",
        schemaType = "[Post!]!",
        isRequired = true,
        isArray = true
    )
    
    println("\nField: posts (GraphQL)")
    println("Schema Validations:")
    graphqlValidation.schemaValidations.take(3).forEach { println("  - $it") }
    
    // Example 7: REST API endpoint validation
    println("\n" + "=".repeat(60))
    println("Example 7: REST API Endpoint Validation")
    println("=".repeat(60))
    
    val restValidation = questions.askRESTValidations(
        endpoint = "/api/users/{id}",
        method = "GET",
        statusCode = 200,
        responseFields = listOf("id", "email", "username")
    )
    
    println("\nEndpoint: GET /api/users/{id}")
    println("Status Code Validations:")
    restValidation.statusCodeValidations.take(3).forEach { println("  - $it") }
    
    // Show Bob AI info
    println("\n" + "=".repeat(60))
    println("Bob AI Information")
    println("=".repeat(60))
    
    val modelInfo = bob.getModelInfo()
    println("\nBob AI Details:")
    modelInfo.forEach { (key, value) ->
        println("  $key: $value")
    }
    
    // Disconnect
    println("\n" + "=".repeat(60))
    bob.disconnect()
    println("=".repeat(60))
    
    println("\n✅ Example completed successfully!")
    println("\nKey Benefits:")
    println("  ✓ No external credentials required")
    println("  ✓ Works offline with intelligent rules")
    println("  ✓ Instant responses")
    println("  ✓ Consistent validation suggestions")
    println("  ✓ Easy to integrate into tests")
    
    println("\nNext Steps:")
    println("  1. Use Bob AI in your test framework")
    println("  2. Generate assertions automatically")
    println("  3. Improve test coverage")
    println("  4. Reduce manual assertion writing")
}

/**
 * Example of using Bob AI in a test class
 */
class ExampleTestWithBobAI {
    private val bob = BobAIConnection()
    private val questions = BobAIQuestions(bob)
    
    init {
        bob.connect()
    }
    
    /**
     * Example test using Bob AI for validation
     */
    fun testUserCreation() {
        // Simulate API response
        val response = mapOf(
            "userId" to "123e4567-e89b-12d3-a456-426614174000",
            "email" to "user@example.com",
            "username" to "johndoe",
            "createdAt" to "2024-01-01T00:00:00Z",
            "status" to "active"
        )
        
        println("\n" + "=".repeat(60))
        println("Test: User Creation API")
        println("=".repeat(60))
        
        // Get validation rules for each field
        response.keys.forEach { fieldName ->
            val validations = questions.askValidationRules(
                fieldName = fieldName,
                fieldType = "String",
                apiType = "REST",
                sampleValue = response[fieldName]
            )
            
            println("\nField: $fieldName")
            println("Suggested Assertions:")
            validations.getHighPriorityRules().forEach { rule ->
                when (rule.type) {
                    "NOT_EMPTY" -> println("  assertThat($fieldName).isNotEmpty()")
                    "EMAIL_FORMAT" -> println("  assertThat($fieldName).isValidEmail()")
                    "UUID_FORMAT" -> println("  assertThat($fieldName).isValidUUID()")
                    "FORMAT" -> println("  assertThat($fieldName).matches(expectedFormat)")
                    else -> println("  // ${rule.description}")
                }
            }
        }
        
        println("\n✅ Test assertions generated successfully!")
    }
    
    fun close() {
        bob.disconnect()
    }
}

/**
 * Run the test example
 */
fun runTestExample() {
    val test = ExampleTestWithBobAI()
    test.testUserCreation()
    test.close()
}

// Made with Bob
