# Testing Guide - Code Generators

## Quick Test Commands

### 1. Test All Generators (Recommended - Fastest)
```bash
# Run the comprehensive manual test script
python3 test_generators_manual.py
```

**Expected Output:**
```
🚀 Starting Code Generator Tests

================================================================================
Testing Python Generator
================================================================================
✅ Generated Test Code:
...
🎉 All checks passed! Python generator is working correctly.

================================================================================
Testing Kotlin Generator Structure
================================================================================
✅ Kotlin generator structure is correct.

================================================================================
Testing Java Generator Structure
================================================================================
✅ Java generator structure is correct.

🎉 All tests passed!
```

---

## Individual Generator Tests

### 2. Test Python Generator Only
```bash
# Method 1: Using the manual test script
python3 test_generators_manual.py

# Method 2: Run the Python generator directly
cd src/main/python/generators
python3 PythonGenerator.py
```

**What it does:**
- Creates sample validation rules
- Generates Python test code
- Displays the generated code
- Validates all assertions are present

---

### 3. Test Kotlin Generator

#### Option A: Using Gradle (Full Test Suite)
```bash
# Run Kotlin generator tests
./gradlew test --tests KotlinGeneratorTest

# Or run all tests
./gradlew test
```

#### Option B: Compile and verify structure
```bash
# Just compile to verify syntax
./gradlew compileKotlin

# Check if generator file compiles
./gradlew classes
```

**Expected Output:**
```
BUILD SUCCESSFUL in Xs
```

---

### 4. Test Java Generator

#### Option A: Using Gradle (Full Test Suite)
```bash
# Run Java generator tests
./gradlew test --tests JavaGeneratorTest

# Or run all tests
./gradlew test
```

#### Option B: Compile and verify
```bash
# Just compile to verify syntax
./gradlew compileJava

# Check if generator file compiles
./gradlew classes
```

---

## Advanced Testing

### 5. Generate Sample Test Code

#### Python Generator
```bash
# Create a test script
cat > test_python_gen.py << 'EOF'
import sys
sys.path.insert(0, 'src/main/python')

from generators.PythonGenerator import PythonGenerator, ValidationRule

generator = PythonGenerator()
rules = [
    ValidationRule("NOT_NULL", "HIGH", "ID must be present", "id"),
    ValidationRule("FORMAT", "HIGH", "Validate email format", "email"),
]

code = generator.generate_test_code("/users", "GET", rules)
print(code)
EOF

# Run it
python3 test_python_gen.py
```

#### Kotlin Generator (requires compilation)
```bash
# First compile the project
./gradlew compileKotlin

# Then run the simple test
./gradlew run -PmainClass=test_kotlin_generator_simple
```

---

## Verify File Structure

### 6. Check All Generator Files Exist
```bash
# List all generator files
echo "=== Generator Files ==="
ls -lh src/main/kotlin/com/testoracle/generators/
ls -lh src/main/java/com/testoracle/generators/
ls -lh src/main/python/generators/

echo ""
echo "=== Test Files ==="
ls -lh src/test/kotlin/com/testoracle/generators/
ls -lh src/test/java/com/testoracle/generators/
ls -lh src/test/python/generators/
```

**Expected Output:**
```
=== Generator Files ===
KotlinGenerator.kt
JavaGenerator.java
PythonGenerator.py

=== Test Files ===
KotlinGeneratorTest.kt
JavaGeneratorTest.java
test_python_generator.py
```

---

## Integration Testing

### 7. Test with Bob AI Integration

#### Start the Model Server
```bash
# Terminal 1: Start the model server
python3 model_server.py
```

#### Test Generator Integration
```bash
# Terminal 2: Test the integration
cat > test_integration.py << 'EOF'
import requests
import json
import sys
sys.path.insert(0, 'src/main/python')

from generators.PythonGenerator import PythonGenerator, ValidationRule

# Get validation rules from Bob AI
response = requests.post('http://localhost:5001/bob_generate_all_scenarios', 
    json={'endpoint': '/users', 'method': 'GET'})

data = response.json()
print("Bob AI Response:")
print(json.dumps(data, indent=2))

# Extract field predictions
field_predictions = data.get('field_predictions', [])
print(f"\nFound {len(field_predictions)} fields")

# Convert to validation rules
rules = []
for field in field_predictions[:3]:  # Top 3 fields
    for validation in field.get('validations', [])[:2]:  # Top 2 validations
        rules.append(ValidationRule(
            type="TYPE_CHECK",
            priority="HIGH",
            description=validation,
            field_name=field['name']
        ))

# Generate test code
generator = PythonGenerator()
test_code = generator.generate_test_code('/users', 'GET', rules)

print("\n" + "="*80)
print("Generated Test Code:")
print("="*80)
print(test_code)
EOF

python3 test_integration.py
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "No module named pytest"
```bash
# Solution: Install pytest (optional, not required for manual tests)
pip3 install pytest

# Or just use the manual test script
python3 test_generators_manual.py
```

#### Issue 2: "Permission denied: ./gradlew"
```bash
# Solution: Make gradlew executable
chmod +x gradlew

# Then run tests
./gradlew test
```

#### Issue 3: "Could not find or load main class"
```bash
# Solution: Clean and rebuild
./gradlew clean
./gradlew build
```

#### Issue 4: Python import errors
```bash
# Solution: Ensure you're in the project root directory
cd /Users/sherinrose/Training/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd

# Then run tests
python3 test_generators_manual.py
```

---

## Complete Test Sequence

### Run All Tests in Order
```bash
# 1. Quick validation test (fastest)
echo "Step 1: Running quick validation..."
python3 test_generators_manual.py

# 2. Compile Kotlin/Java (verifies syntax)
echo ""
echo "Step 2: Compiling Kotlin and Java..."
./gradlew compileKotlin compileJava

# 3. Run full test suite (if time permits)
echo ""
echo "Step 3: Running full test suite..."
./gradlew test

echo ""
echo "✅ All tests completed!"
```

---

## Expected Test Duration

| Test Type | Duration | Command |
|-----------|----------|---------|
| Manual Python Test | ~2 seconds | `python3 test_generators_manual.py` |
| Kotlin Compilation | ~10-30 seconds | `./gradlew compileKotlin` |
| Java Compilation | ~5-15 seconds | `./gradlew compileJava` |
| Full Gradle Test Suite | ~30-60 seconds | `./gradlew test` |
| Integration Test | ~5 seconds | `python3 test_integration.py` |

---

## Success Criteria

### ✅ Tests Pass If:
1. Manual test script shows "🎉 All tests passed!"
2. Gradle compilation succeeds with "BUILD SUCCESSFUL"
3. Generated code contains all expected assertions
4. No syntax errors in any generator file

### ❌ Tests Fail If:
1. Import errors occur
2. Compilation fails
3. Generated code is missing key elements
4. Syntax errors in generator files

---

## Quick Reference

### Most Important Commands
```bash
# 1. FASTEST - Test everything quickly
python3 test_generators_manual.py

# 2. Verify compilation
./gradlew compileKotlin compileJava

# 3. Full test suite (optional)
./gradlew test
```

### One-Line Complete Test
```bash
python3 test_generators_manual.py && ./gradlew compileKotlin compileJava && echo "✅ All generators working!"
```

---

## Next Steps After Testing

Once all tests pass:

1. **Integrate with Bob AI:**
   ```bash
   # Start model server
   python3 model_server.py
   
   # Test integration
   python3 test_integration.py
   ```

2. **Generate Real Test Code:**
   ```bash
   # Use the CLI to generate tests
   python3 ai_oracle_cli.py 'curl -X GET "https://api.example.com/users"'
   ```

3. **Deploy to Production:**
   - All generators are production-ready
   - Documentation is complete
   - Integration points are defined

---

**For Questions or Issues:**
- Check TEST_RESULTS.md for detailed test results
- Check CODE_GENERATOR_README.md for usage documentation
- Review generated code samples in test output