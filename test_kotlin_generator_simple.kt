import com.testoracle.generators.KotlinGenerator
import com.testoracle.generators.ValidationRule

/**
 * Simple standalone test for KotlinGenerator
 * Can be run without full test framework
 */
fun main() {
    println("=" .repeat(80))
    println("Testing Kotlin Generator")
    println("=" .repeat(80))
    
    val generator = KotlinGenerator()
    
    // Create sample validation rules
    val rules = listOf(
        ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id"),
        ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email"),
        ValidationRule("POSITIVE", "MEDIUM", "Age must be positive (> 0)", "age"),
        ValidationRule("ENUM", "HIGH", "Status must be one of allowed values", "status")
    )
    
    // Generate test code
    println("\n📝 Generating test code for GET /users endpoint...")
    val testCode = generator.generateTestCode("/users", "GET", rules)
    
    // Display generated code
    println("\n✅ Generated Test Code:")
    println("-".repeat(80))
    println(testCode)
    println("-".repeat(80))
    
    // Validate key elements
    val checks = listOf(
        "import org.junit.jupiter.api.Test" to "JUnit import",
        "class" to "Test class",
        "fun `test_get_users`()" to "Test function",
        ".get(\"/users\")" to "GET request",
        "assertNotNull" to "NOT_NULL assertion",
        "matches(Regex" to "FORMAT assertion",
        "> 0" to "POSITIVE assertion",
        "allowedValues" to "ENUM assertion"
    )
    
    println("\n🔍 Validation Checks:")
    var allPassed = true
    for ((checkStr, description) in checks) {
        if (testCode.contains(checkStr)) {
            println("  ✓ $description: FOUND")
        } else {
            println("  ✗ $description: MISSING")
            allPassed = false
        }
    }
    
    if (allPassed) {
        println("\n🎉 All checks passed! Kotlin generator is working correctly.")
    } else {
        println("\n❌ Some checks failed. Please review the generated code.")
    }
}

// Made with Bob
