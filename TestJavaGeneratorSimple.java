import com.testoracle.generators.JavaGenerator;
import com.testoracle.generators.ValidationRule;
import java.util.Arrays;
import java.util.List;

/**
 * Simple standalone test for JavaGenerator
 * Can be run without full test framework
 */
public class TestJavaGeneratorSimple {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(80));
        System.out.println("Testing Java Generator");
        System.out.println("=".repeat(80));
        
        JavaGenerator generator = new JavaGenerator();
        
        // Create sample validation rules
        List<ValidationRule> rules = Arrays.asList(
            new ValidationRule("NOT_NULL", "HIGH", "ID must be present and non-null", "id"),
            new ValidationRule("FORMAT", "HIGH", "Validate RFC 5322 email format with regex", "email"),
            new ValidationRule("POSITIVE", "MEDIUM", "Age must be positive (> 0)", "age"),
            new ValidationRule("ENUM", "HIGH", "Status must be one of allowed values", "status")
        );
        
        // Generate test code
        System.out.println("\n📝 Generating test code for GET /users endpoint...");
        String testCode = generator.generateTestCode("/users", "GET", rules);
        
        // Display generated code
        System.out.println("\n✅ Generated Test Code:");
        System.out.println("-".repeat(80));
        System.out.println(testCode);
        System.out.println("-".repeat(80));
        
        // Validate key elements
        String[][] checks = {
            {"import org.junit.jupiter.api.Test", "JUnit import"},
            {"public class", "Test class"},
            {"public void test_get_users()", "Test method"},
            {".get(\"/users\")", "GET request"},
            {"assertNotNull", "NOT_NULL assertion"},
            {"matches(", "FORMAT assertion"},
            {"> 0", "POSITIVE assertion"},
            {"allowedValues", "ENUM assertion"}
        };
        
        System.out.println("\n🔍 Validation Checks:");
        boolean allPassed = true;
        for (String[] check : checks) {
            String checkStr = check[0];
            String description = check[1];
            if (testCode.contains(checkStr)) {
                System.out.println("  ✓ " + description + ": FOUND");
            } else {
                System.out.println("  ✗ " + description + ": MISSING");
                allPassed = false;
            }
        }
        
        if (allPassed) {
            System.out.println("\n🎉 All checks passed! Java generator is working correctly.");
        } else {
            System.out.println("\n❌ Some checks failed. Please review the generated code.");
        }
    }
}

// Made with Bob
