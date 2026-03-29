package com.testoracle.ai.bob

/**
 * Simplified question handlers for Bob AI (Roo Code)
 * No external credentials required - uses intelligent rule-based analysis
 */
class BobAIQuestions(private val connection: BobAIConnection) {

    /**
     * Ask Bob what a field means semantically
     */
    fun askFieldMeaning(
        fieldName: String,
        fieldType: String,
        apiType: String = "REST",
        sampleValue: Any? = null
    ): FieldMeaningResponse {
        val context = mapOf(
            "field_name" to fieldName,
            "field_type" to fieldType,
            "api_type" to apiType,
            "sample_value" to (sampleValue?.toString() ?: "")
        )
        
        val prompt = "What does the field \"$fieldName\" (type: $fieldType) mean in a $apiType API context?"
        val response = connection.askBob(prompt, context)
        
        return FieldMeaningResponse(
            fieldName = fieldName,
            meaning = extractMeaning(response.answer),
            useCases = extractUseCases(response.answer),
            patterns = extractPatterns(response.answer),
            confidence = response.confidence,
            rawResponse = response.answer
        )
    }

    /**
     * Ask Bob what validations should be applied to a field
     */
    fun askValidationRules(
        fieldName: String,
        fieldType: String,
        apiType: String = "REST",
        sampleValue: Any? = null,
        schema: String? = null
    ): ValidationRulesResponse {
        val context = mutableMapOf(
            "field_name" to fieldName,
            "field_type" to fieldType,
            "api_type" to apiType
        )
        
        sampleValue?.let { context["sample_value"] = it.toString() }
        schema?.let { context["schema"] = it }
        
        val prompt = "What validation rules should be checked for field \"$fieldName\" (type: $fieldType)?"
        val response = connection.askBob(prompt, context)
        
        return ValidationRulesResponse(
            fieldName = fieldName,
            rules = parseValidationRules(response.answer),
            priority = categorizePriority(response.answer),
            confidence = response.confidence,
            rawResponse = response.answer
        )
    }

    /**
     * Ask Bob about business logic constraints
     */
    fun askBusinessLogic(
        fieldName: String,
        relatedFields: List<String> = emptyList(),
        operation: String = "read",
        apiType: String = "REST"
    ): BusinessLogicResponse {
        val context = mapOf(
            "field" to fieldName,
            "related_fields" to relatedFields.joinToString(", "),
            "operation" to operation,
            "api_type" to apiType
        )
        
        val prompt = "What business logic constraints should be validated for field \"$fieldName\" in a $operation operation?"
        val response = connection.askBob(prompt, context)
        
        return BusinessLogicResponse(
            fieldName = fieldName,
            constraints = parseConstraints(response.answer),
            relationships = parseRelationships(response.answer),
            stateTransitions = parseStateTransitions(response.answer),
            confidence = response.confidence,
            rawResponse = response.answer
        )
    }

    /**
     * Ask Bob about GraphQL-specific validations
     */
    fun askGraphQLValidations(
        fieldName: String,
        schemaType: String,
        isRequired: Boolean,
        isArray: Boolean = false
    ): GraphQLValidationResponse {
        val context = mapOf(
            "field" to fieldName,
            "schema_type" to schemaType,
            "required" to isRequired,
            "is_array" to isArray
        )
        
        val prompt = "What GraphQL-specific validations should be performed for field \"$fieldName\" (type: $schemaType)?"
        val response = connection.askBob(prompt, context)
        
        return GraphQLValidationResponse(
            fieldName = fieldName,
            schemaValidations = parseSchemaValidations(response.answer),
            scalarValidations = parseScalarValidations(response.answer),
            arrayValidations = if (isArray) parseArrayValidations(response.answer) else emptyList(),
            confidence = response.confidence,
            rawResponse = response.answer
        )
    }

    /**
     * Ask Bob about REST API-specific validations
     */
    fun askRESTValidations(
        endpoint: String,
        method: String,
        statusCode: Int = 200,
        responseFields: List<String> = emptyList()
    ): RESTValidationResponse {
        val context = mapOf(
            "endpoint" to endpoint,
            "method" to method,
            "status_code" to statusCode,
            "response_fields" to responseFields.joinToString(", ")
        )
        
        val prompt = "What REST API-specific validations should be performed for $method $endpoint?"
        val response = connection.askBob(prompt, context)
        
        return RESTValidationResponse(
            endpoint = endpoint,
            method = method,
            statusCodeValidations = parseStatusCodeValidations(response.answer),
            headerValidations = parseHeaderValidations(response.answer),
            structureValidations = parseStructureValidations(response.answer),
            confidence = response.confidence,
            rawResponse = response.answer
        )
    }

    // Parsing helper methods
    private fun extractMeaning(answer: String): String {
        val lines = answer.lines()
        return lines.firstOrNull { 
            it.contains("meaning", ignoreCase = true) || 
            it.contains("stores", ignoreCase = true) 
        }?.trim() ?: lines.firstOrNull()?.trim() ?: answer.take(200)
    }

    private fun extractUseCases(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("use case", ignoreCase = true) || 
                it.contains("used for", ignoreCase = true) ||
                (it.trim().startsWith("-") && it.contains("use", ignoreCase = true))
            }
            .map { it.trim().removePrefix("-").trim() }
            .filter { it.isNotEmpty() }
    }

    private fun extractPatterns(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("pattern", ignoreCase = true) || 
                it.contains("format", ignoreCase = true) 
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseValidationRules(answer: String): List<ValidationRule> {
        val rules = mutableListOf<ValidationRule>()
        val lines = answer.lines()
        
        lines.forEach { line ->
            val lowerLine = line.lowercase()
            when {
                lowerLine.contains("not empty") || lowerLine.contains("not null") -> {
                    rules.add(ValidationRule("NOT_EMPTY", "Field must not be empty", "HIGH"))
                }
                lowerLine.contains("format") && lowerLine.contains("email") -> {
                    rules.add(ValidationRule("EMAIL_FORMAT", "Must be valid email format", "HIGH"))
                }
                lowerLine.contains("format") && lowerLine.contains("uuid") -> {
                    rules.add(ValidationRule("UUID_FORMAT", "Must be valid UUID format", "HIGH"))
                }
                lowerLine.contains("format validation") -> {
                    rules.add(ValidationRule("FORMAT", line.trim(), "HIGH"))
                }
                lowerLine.contains("length check") || lowerLine.contains("maximum") -> {
                    rules.add(ValidationRule("LENGTH", line.trim(), "MEDIUM"))
                }
                lowerLine.contains("positive") -> {
                    rules.add(ValidationRule("POSITIVE", "Must be positive value", "MEDIUM"))
                }
                lowerLine.contains("valid domain") -> {
                    rules.add(ValidationRule("DOMAIN", "Must have valid domain", "MEDIUM"))
                }
                lowerLine.contains("uniqueness") -> {
                    rules.add(ValidationRule("UNIQUE", "Must be unique", "HIGH"))
                }
            }
        }
        
        return rules.ifEmpty { 
            listOf(ValidationRule("BASIC", "Validate field type and presence", "LOW")) 
        }
    }

    private fun categorizePriority(answer: String): Map<String, List<String>> {
        val high = mutableListOf<String>()
        val medium = mutableListOf<String>()
        val low = mutableListOf<String>()
        
        answer.lines().forEach { line ->
            when {
                line.contains("HIGH PRIORITY", ignoreCase = true) -> {
                    // Collect lines after HIGH PRIORITY marker
                    val nextLines = answer.lines()
                        .dropWhile { !it.contains("HIGH PRIORITY", ignoreCase = true) }
                        .drop(1)
                        .takeWhile { !it.contains("MEDIUM PRIORITY", ignoreCase = true) && !it.contains("LOW PRIORITY", ignoreCase = true) }
                    high.addAll(nextLines.filter { it.trim().isNotEmpty() })
                }
                line.contains("MEDIUM PRIORITY", ignoreCase = true) -> {
                    val nextLines = answer.lines()
                        .dropWhile { !it.contains("MEDIUM PRIORITY", ignoreCase = true) }
                        .drop(1)
                        .takeWhile { !it.contains("LOW PRIORITY", ignoreCase = true) }
                    medium.addAll(nextLines.filter { it.trim().isNotEmpty() })
                }
                line.contains("LOW PRIORITY", ignoreCase = true) -> {
                    val nextLines = answer.lines()
                        .dropWhile { !it.contains("LOW PRIORITY", ignoreCase = true) }
                        .drop(1)
                    low.addAll(nextLines.filter { it.trim().isNotEmpty() })
                }
            }
        }
        
        return mapOf(
            "HIGH" to high.ifEmpty { listOf("Type validation", "Required field check") },
            "MEDIUM" to medium.ifEmpty { listOf("Format validation", "Range check") },
            "LOW" to low.ifEmpty { listOf("Optional metadata validation") }
        )
    }

    private fun parseConstraints(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("must", ignoreCase = true) || 
                it.contains("should", ignoreCase = true) ||
                it.contains("constraint", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseRelationships(answer: String): List<FieldRelationship> {
        return answer.lines()
            .filter { 
                it.contains("related", ignoreCase = true) || 
                it.contains("depends", ignoreCase = true) ||
                it.contains("reference", ignoreCase = true)
            }
            .map { FieldRelationship(it.trim(), "DEPENDENCY") }
    }

    private fun parseStateTransitions(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("state", ignoreCase = true) || 
                it.contains("transition", ignoreCase = true) ||
                it.contains("workflow", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseSchemaValidations(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("schema", ignoreCase = true) ||
                it.contains("type", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseScalarValidations(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("scalar", ignoreCase = true) || 
                it.contains("custom type", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseArrayValidations(answer: String): List<String> {
        return answer.lines()
            .filter {
                it.contains("array", ignoreCase = true) ||
                it.contains("list", ignoreCase = true) ||
                it.contains("collection", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }
}

// Response data classes

/**
 * Response containing field meaning analysis
 */
data class FieldMeaningResponse(
    val fieldName: String,
    val meaning: String,
    val useCases: List<String>,
    val patterns: List<String>,
    val confidence: Double,
    val rawResponse: String
)

/**
 * Response containing validation rules
 */
data class ValidationRulesResponse(
    val fieldName: String,
    val rules: List<ValidationRule>,
    val priority: Map<String, List<String>>,
    val confidence: Double,
    val rawResponse: String
) {
    fun getHighPriorityRules(): List<ValidationRule> =
        rules.filter { it.priority == "HIGH" }
    
    fun getMediumPriorityRules(): List<ValidationRule> =
        rules.filter { it.priority == "MEDIUM" }
}

/**
 * Individual validation rule
 */
data class ValidationRule(
    val type: String,
    val description: String,
    val priority: String
)

/**
 * Response containing business logic analysis
 */
data class BusinessLogicResponse(
    val fieldName: String,
    val constraints: List<String>,
    val relationships: List<FieldRelationship>,
    val stateTransitions: List<String>,
    val confidence: Double,
    val rawResponse: String
)

/**
 * Field relationship information
 */
data class FieldRelationship(
    val description: String,
    val type: String
)

/**
 * Response containing GraphQL-specific validations
 */
data class GraphQLValidationResponse(
    val fieldName: String,
    val schemaValidations: List<String>,
    val scalarValidations: List<String>,
    val arrayValidations: List<String>,
    val confidence: Double,
    val rawResponse: String
)

/**
 * Response containing REST API-specific validations
 */
data class RESTValidationResponse(
    val endpoint: String,
    val method: String,
    val statusCodeValidations: List<String>,
    val headerValidations: List<String>,
    val structureValidations: List<String>,
    val confidence: Double,
    val rawResponse: String
)

    private fun parseStatusCodeValidations(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("status", ignoreCase = true) ||
                it.contains("code", ignoreCase = true) ||
                it.matches(Regex(".*\\d{3}.*"))
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseHeaderValidations(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("header", ignoreCase = true) ||
                it.contains("content-type", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    private fun parseStructureValidations(answer: String): List<String> {
        return answer.lines()
            .filter { 
                it.contains("structure", ignoreCase = true) ||
                it.contains("format", ignoreCase = true) ||
                it.contains("response", ignoreCase = true)
            }
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }
