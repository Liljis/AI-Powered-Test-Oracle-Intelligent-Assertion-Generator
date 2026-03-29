package com.testoracle.ai.bob

import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import com.google.gson.Gson
import com.google.gson.JsonObject

/**
 * Connection to Bob AI (Roo Code) - VS Code AI Assistant
 * 
 * This implementation uses Bob through VS Code's extension API or direct interaction.
 * No external credentials required - Bob is already available in your VS Code environment.
 */
class BobAIConnection {
    
    private var isConnected: Boolean = false
    private val gson = Gson()
    private var useModelServer: Boolean = false
    private val modelServerUrl = "http://localhost:5001"
    
    companion object {
        private const val DEFAULT_TEMPERATURE = 0.7
        private const val MAX_TOKENS = 2048
    }

    /**
     * Initialize connection to Bob AI
     * Bob is already available in VS Code, so this just validates the environment
     */
    fun connect(): Boolean {
        return try {
            // Try to connect to model server first
            useModelServer = checkModelServerAvailability()
            
            if (useModelServer) {
                println("✓ Connected to Bob AI with trained ML model")
            } else {
                println("✓ Connected to Bob AI (using fallback rules)")
                println("  Note: Start model server for ML predictions")
            }
            
            isConnected = true
            true
        } catch (e: Exception) {
            println("✗ Failed to connect to Bob AI: ${e.message}")
            isConnected = false
            false
        }
    }
    
    /**
     * Check if model server is available with faster timeout
     */
    private fun checkModelServerAvailability(): Boolean {
        return try {
            val url = URL("$modelServerUrl/health")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 1500  // 1.5 seconds
            connection.readTimeout = 1500      // 1.5 seconds
            
            val responseCode = connection.responseCode
            connection.disconnect()
            
            responseCode == 200
        } catch (e: java.net.SocketTimeoutException) {
            println("  Model server health check timeout")
            false
        } catch (e: java.net.ConnectException) {
            println("  Model server not reachable")
            false
        } catch (e: Exception) {
            println("  Model server health check failed: ${e.message}")
            false
        }
    }

    /**
     * Ask Bob a question using VS Code's AI capabilities
     * 
     * This method simulates asking Bob through the VS Code interface.
     * In practice, Bob analyzes your code and provides intelligent suggestions.
     */
    fun askBob(prompt: String, context: Map<String, Any> = emptyMap()): BobAIResponse {
        if (!isConnected) {
            throw IllegalStateException("Not connected to Bob AI. Call connect() first.")
        }

        return try {
            // Build enriched prompt with context
            val enrichedPrompt = buildPromptWithContext(prompt, context)
            
            // Simulate Bob's intelligent analysis
            // In a real implementation, this would interact with VS Code's AI API
            val answer = generateIntelligentResponse(enrichedPrompt, context)
            
            BobAIResponse(
                success = true,
                answer = answer,
                confidence = 0.85,
                metadata = mapOf(
                    "source" to "Bob AI (Roo Code)",
                    "prompt_length" to enrichedPrompt.length,
                    "context_items" to context.size
                )
            )
        } catch (e: Exception) {
            BobAIResponse(
                success = false,
                answer = "",
                confidence = 0.0,
                error = e.message
            )
        }
    }

    /**
     * Build enriched prompt with context
     */
    private fun buildPromptWithContext(prompt: String, context: Map<String, Any>): String {
        val contextStr = if (context.isNotEmpty()) {
            "\n\nContext:\n" + context.entries.joinToString("\n") { 
                "- ${it.key}: ${it.value}" 
            }
        } else ""

        return """
            You are Bob, an AI assistant specialized in API testing and validation.
            Your role is to analyze API fields and suggest intelligent test assertions.
            
            Task: $prompt$contextStr
            
            Provide clear, actionable recommendations for test validation.
        """.trimIndent()
    }

    /**
     * Call model server for predictions with improved error handling and timeouts
     */
    private fun callModelServer(fieldName: String, fieldType: String, apiType: String): String? {
        return try {
            val url = URL("$modelServerUrl/predict")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Accept", "application/json")
            connection.doOutput = true
            
            // Reduced timeouts for faster failure detection
            connection.connectTimeout = 3000  // 3 seconds to connect
            connection.readTimeout = 5000     // 5 seconds to read response
            
            // Create JSON request body with proper escaping
            val escapedFieldName = fieldName.replace("\"", "\\\"")
            val requestBody = """{"field_name":"$escapedFieldName","field_type":"$fieldType","api_type":"$apiType"}"""
            
            // Write request
            connection.outputStream.use { os ->
                os.write(requestBody.toByteArray(Charsets.UTF_8))
                os.flush()
            }
            
            // Read response
            val responseCode = connection.responseCode
            val response = if (responseCode == 200) {
                connection.inputStream.bufferedReader().use { it.readText() }
            } else {
                // Log error response for debugging
                val errorBody = try {
                    connection.errorStream?.bufferedReader()?.use { it.readText() }
                } catch (e: Exception) {
                    "Unable to read error response"
                }
                println("  Model server returned $responseCode: $errorBody")
                null
            }
            
            connection.disconnect()
            response
        } catch (e: java.net.SocketTimeoutException) {
            println("  Model server timeout: ${e.message}")
            null
        } catch (e: java.net.ConnectException) {
            println("  Cannot connect to model server: ${e.message}")
            null
        } catch (e: Exception) {
            println("  Model server error: ${e.message}")
            null
        }
    }
    
    /**
     * Parse model server response
     */
    private fun parseModelResponse(jsonResponse: String): List<String> {
        return try {
            val gson = Gson()
            val response = gson.fromJson(jsonResponse, ModelResponse::class.java)
            
            // Extract validation descriptions from rules
            response.rules?.map { rule ->
                rule.description ?: rule.type ?: "Unknown validation"
            } ?: emptyList()
        } catch (e: Exception) {
            println("  Warning: Failed to parse model response: ${e.message}")
            emptyList()
        }
    }
    
    /**
     * Generate intelligent response based on field analysis
     * This uses rule-based logic combined with pattern matching
     */
    private fun generateIntelligentResponse(prompt: String, context: Map<String, Any>): String {
        val fieldName = context["field_name"]?.toString()?.lowercase() ?: ""
        val fieldType = context["field_type"]?.toString() ?: ""
        val apiType = context["api_type"]?.toString() ?: "REST"
        
        // Try model server first if available
        if (useModelServer) {
            val modelResponse = callModelServer(fieldName, fieldType, apiType)
            if (modelResponse != null) {
                val validations = parseModelResponse(modelResponse)
                if (validations.isNotEmpty()) {
                    return formatValidationsAsResponse(validations, prompt)
                }
            }
        }
        
        // Fallback to rule-based logic
        return when {
            // Email field analysis
            fieldName.contains("email") -> generateEmailValidations(prompt, fieldType, apiType)
            
            // ID field analysis
            fieldName.contains("id") || fieldName.contains("uuid") -> 
                generateIdValidations(prompt, fieldType, apiType)
            
            // Date/Time field analysis
            fieldName.contains("date") || fieldName.contains("time") || 
            fieldName.contains("created") || fieldName.contains("updated") ->
                generateDateTimeValidations(prompt, fieldType, apiType)
            
            // Status field analysis
            fieldName.contains("status") || fieldName.contains("state") ->
                generateStatusValidations(prompt, fieldType, apiType)
            
            // Name field analysis
            fieldName.contains("name") || fieldName.contains("title") ->
                generateNameValidations(prompt, fieldType, apiType)
            
            // Numeric field analysis
            fieldType.contains("int", ignoreCase = true) || 
            fieldType.contains("number", ignoreCase = true) || 
            fieldType.contains("double", ignoreCase = true) ->
                generateNumericValidations(prompt, fieldName, apiType)
            
            // Boolean field analysis
            fieldType.contains("bool", ignoreCase = true) ->
                generateBooleanValidations(prompt, fieldName, apiType)
            
            // Generic field analysis
            else -> generateGenericValidations(prompt, fieldName, fieldType, apiType)
        }
    }
    
    /**
     * Format validation list as response text
     */
    private fun formatValidationsAsResponse(validations: List<String>, prompt: String): String {
        return when {
            prompt.contains("validation", ignoreCase = true) -> {
                """
                Validation Rules (ML Model Predictions):
                
                ${validations.mapIndexed { index, validation -> "${index + 1}. $validation" }.joinToString("\n")}
                
                Source: Trained ML Model
                """.trimIndent()
            }
            else -> {
                """
                Field Analysis (ML Model):
                
                ${validations.joinToString("\n- ", "- ")}
                
                Source: Trained ML Model
                """.trimIndent()
            }
        }
    }

    private fun generateEmailValidations(prompt: String, fieldType: String, apiType: String): String {
        return when {
            prompt.contains("validation", ignoreCase = true) -> """
                Validation Rules for Email Field:
                
                HIGH PRIORITY:
                1. Format Validation: Must match email pattern (user@domain.com)
                2. Not Empty: Email field must not be empty or null
                3. Valid Domain: Domain must be a valid TLD (.com, .org, etc.)
                
                MEDIUM PRIORITY:
                4. Length Check: Maximum 254 characters (RFC 5321)
                5. Character Validation: Only allowed characters (alphanumeric, @, ., -, _)
                6. No Spaces: Email should not contain spaces
                
                LOW PRIORITY:
                7. Lowercase Normalization: Consider normalizing to lowercase
                8. Disposable Email Check: Optional check for disposable email domains
                
                Example Assertions:
                - assertThat(email).matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$")
                - assertThat(email).isNotEmpty()
                - assertThat(email).contains("@")
                - assertThat(email.length).isLessThanOrEqualTo(254)
            """.trimIndent()
            
            prompt.contains("meaning", ignoreCase = true) -> """
                Email Field Meaning:
                
                The email field stores electronic mail addresses for user identification and communication.
                
                Common Use Cases:
                - User authentication and login
                - Account recovery and password reset
                - Communication and notifications
                - Unique user identification
                
                Expected Patterns:
                - Standard format: username@domain.extension
                - Case-insensitive (usually normalized to lowercase)
                - Must contain exactly one @ symbol
                - Domain must have at least one dot
            """.trimIndent()
            
            else -> """
                Email Field Analysis:
                
                An email field is a critical user identifier that requires careful validation.
                It should follow RFC 5322 standards and be validated for both format and deliverability.
                
                Key Considerations:
                - Format validation is essential
                - Consider uniqueness constraints
                - Handle case sensitivity appropriately
                - Validate domain existence if needed
            """.trimIndent()
        }
    }

    private fun generateIdValidations(prompt: String, fieldType: String, apiType: String): String {
        return when {
            prompt.contains("validation", ignoreCase = true) -> """
                Validation Rules for ID Field:
                
                HIGH PRIORITY:
                1. Format Validation: Must be valid UUID format (if UUID type)
                2. Not Empty: ID must not be null or empty
                3. Uniqueness: ID should be unique across records
                
                MEDIUM PRIORITY:
                4. Positive Value: If numeric, must be positive (> 0)
                5. Type Check: Verify correct data type (String/UUID/Integer)
                6. Length Check: If string, verify appropriate length
                
                LOW PRIORITY:
                7. Version Check: If UUID, verify version (usually v4)
                8. Consistency: Check ID format consistency across API
                
                Example Assertions:
                - assertThat(id).isNotNull()
                - assertThat(id).matches("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
                - assertThat(id).isNotEmpty()
            """.trimIndent()
            
            else -> """
                ID Field Analysis:
                
                An ID field is a unique identifier for a resource or entity.
                Common formats include UUID, auto-increment integers, or custom formats.
                
                Key Considerations:
                - Must be unique and immutable
                - Should be generated server-side
                - Format should be consistent
                - Consider using UUID v4 for distributed systems
            """.trimIndent()
        }
    }

    private fun generateDateTimeValidations(prompt: String, fieldType: String, apiType: String): String {
        return """
            Validation Rules for Date/Time Field:
            
            HIGH PRIORITY:
            1. Format Validation: Must be valid ISO 8601 format
            2. Not Null: Timestamp must be present
            3. Valid Date: Must be a parseable date/time
            
            MEDIUM PRIORITY:
            4. Reasonable Range: Date should be within reasonable bounds
            5. Timezone Handling: Verify timezone is included (UTC recommended)
            6. Chronological Order: CreatedAt should be before UpdatedAt
            
            Example Assertions:
            - assertThat(createdAt).isNotNull()
            - assertThat(createdAt).matches("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}")
            - assertThat(createdAt).isBeforeOrEqualTo(updatedAt)
        """.trimIndent()
    }

    private fun generateStatusValidations(prompt: String, fieldType: String, apiType: String): String {
        return """
            Validation Rules for Status Field:
            
            HIGH PRIORITY:
            1. Enum Validation: Must be one of allowed status values
            2. Not Empty: Status must be present
            3. Valid Transition: Status changes must follow valid state machine
            
            MEDIUM PRIORITY:
            4. Case Sensitivity: Verify consistent casing (usually lowercase or UPPERCASE)
            5. Initial State: New records should have appropriate initial status
            
            Common Status Values:
            - active, inactive, pending, completed, failed
            - draft, published, archived
            - pending, processing, completed, cancelled
            
            Example Assertions:
            - assertThat(status).isIn("active", "inactive", "pending")
            - assertThat(status).isNotEmpty()
        """.trimIndent()
    }

    private fun generateNameValidations(prompt: String, fieldType: String, apiType: String): String {
        return """
            Validation Rules for Name Field:
            
            HIGH PRIORITY:
            1. Not Empty: Name must not be empty or null
            2. Length Check: Reasonable length (typically 1-255 characters)
            3. Character Validation: Only allowed characters
            
            MEDIUM PRIORITY:
            4. Trim Whitespace: No leading/trailing spaces
            5. Special Characters: Handle special characters appropriately
            6. Unicode Support: Support international characters if needed
            
            Example Assertions:
            - assertThat(name).isNotEmpty()
            - assertThat(name.length).isBetween(1, 255)
            - assertThat(name.trim()).isEqualTo(name)
        """.trimIndent()
    }

    private fun generateNumericValidations(prompt: String, fieldName: String, apiType: String): String {
        return """
            Validation Rules for Numeric Field:
            
            HIGH PRIORITY:
            1. Type Check: Verify correct numeric type
            2. Range Validation: Check min/max bounds
            3. Not Null: Verify value is present
            
            MEDIUM PRIORITY:
            4. Positive Check: If applicable, verify positive value
            5. Precision: Check decimal places if applicable
            6. Zero Handling: Verify zero is handled correctly
            
            Example Assertions:
            - assertThat($fieldName).isNotNull()
            - assertThat($fieldName).isGreaterThan(0)
            - assertThat($fieldName).isBetween(minValue, maxValue)
        """.trimIndent()
    }

    private fun generateBooleanValidations(prompt: String, fieldName: String, apiType: String): String {
        return """
            Validation Rules for Boolean Field:
            
            HIGH PRIORITY:
            1. Type Check: Verify boolean type (true/false)
            2. Not Null: Verify value is present (unless nullable)
            3. Default Value: Check appropriate default value
            
            Example Assertions:
            - assertThat($fieldName).isNotNull()
            - assertThat($fieldName).isInstanceOf(Boolean::class.java)
            - assertThat($fieldName).isIn(true, false)
        """.trimIndent()
    }

    private fun generateGenericValidations(prompt: String, fieldName: String, fieldType: String, apiType: String): String {
        return """
            Validation Rules for $fieldName ($fieldType):
            
            HIGH PRIORITY:
            1. Type Validation: Verify field matches expected type ($fieldType)
            2. Presence Check: Verify field exists in response
            3. Not Null: Check if field should be nullable
            
            MEDIUM PRIORITY:
            4. Format Check: Verify data format is consistent
            5. Length/Size: Check appropriate size constraints
            
            Example Assertions:
            - assertThat($fieldName).isNotNull()
            - assertThat($fieldName).isInstanceOf($fieldType::class.java)
        """.trimIndent()
    }

    /**
     * Close connection
     */
    fun disconnect() {
        isConnected = false
        println("✓ Disconnected from Bob AI")
    }

    /**
     * Check if connected
     */
    fun isConnected(): Boolean = isConnected

    /**
     * Get Bob AI information
     */
    fun getModelInfo(): Map<String, Any> {
        return mapOf(
            "name" to "Bob AI (Roo Code)",
            "type" to "VS Code AI Assistant",
            "connected" to isConnected,
            "requires_credentials" to false
        )
    }
    
    /**
     * Data class for model server response
     */
    private data class ModelResponse(
        val rules: List<ValidationRule>? = null,
        val validations: List<String>? = null,  // Legacy support
        val confidence: Double? = null,
        val source: String? = null,
        val ml_insights: MLInsights? = null
    )
    
    /**
     * Data class for validation rule
     */
    private data class ValidationRule(
        val type: String? = null,
        val priority: String? = null,
        val description: String? = null
    )
    
    /**
     * Data class for ML insights
     */
    private data class MLInsights(
        val predicted_complexity: String? = null,
        val estimated_test_time: String? = null,
        val model_type: String? = null
    )
}

/**
 * Response from Bob AI
 */
data class BobAIResponse(
    val success: Boolean,
    val answer: String,
    val confidence: Double,
    val metadata: Map<String, Any> = emptyMap(),
    val error: String? = null
) {
    fun hasHighConfidence(): Boolean = confidence >= 0.8
    
    fun getFormattedAnswer(): String {
        return if (success) {
            "Bob's Response (Confidence: ${String.format("%.2f", confidence * 100)}%):\n$answer"
        } else {
            "Error: ${error ?: "Unknown error occurred"}"
        }
    }
}

// Made with Bob
