> Task :checkKotlinGradlePluginConfigurationErrors
> Task :processResources NO-SOURCE

> Task :compileKotlin
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:295:58 Parameter 'fieldType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:295:77 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:354:55 Parameter 'fieldType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:354:74 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:394:45 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:394:61 Parameter 'fieldType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:394:80 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:415:43 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:415:59 Parameter 'fieldType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:415:78 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:439:41 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:439:57 Parameter 'fieldType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:439:76 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:460:44 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:460:79 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:481:44 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:481:79 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:497:44 Parameter 'prompt' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/ai/bob/BobAIConnection.kt:497:98 Parameter 'apiType' is never used
w: file:///Users/meenakshisuresh/backend/e2e-tests/a-i-powered-test-oracle-intelligent-assertion-generator-21a31ccd/src/main/kotlin/com/testoracle/generators/KotlinGenerator.kt:225:57 'capitalize(): String' is deprecated. Use replaceFirstChar instead.

> Task :compileJava
> Task :classes

> Task :run
============================================================
Bob AI Integration Example - No Credentials Required!
============================================================

1. Connecting to Bob AI...
✓ Connected to Bob AI with trained ML model

============================================================
Example 1: Email Field Analysis
============================================================

Field: email
Validation Rules:
  [HIGH] EMAIL_FORMAT: Must be valid email format
  [MEDIUM] DOMAIN: Must have valid domain
  [MEDIUM] LENGTH: 4. Maximum 254 characters per RFC 5321

Confidence: 85.00%

============================================================
Example 2: User ID Field Analysis
============================================================

Field: userId
Validation Rules:
  [MEDIUM] POSITIVE: Must be positive value

============================================================
Example 3: Timestamp Field Analysis
============================================================

Field: createdAt
Validation Rules:
  [LOW] BASIC: Validate field type and presence

============================================================
Example 4: Understanding Field Meaning
============================================================

Field: email
Meaning: Validation Rules (ML Model Predictions):

Use Cases:

============================================================
Example 5: Business Logic Analysis
============================================================
  Model server returned 400: {"confidence":0.0,"error":"field_name is required and must be a non-empty string","rules":[]}


Field: status
Constraints:
  - 3. Not Null: Check if field should be nullable
  - 5. Length/Size: Check appropriate size constraints

============================================================
Example 6: GraphQL Field Validation
============================================================
  Model server returned 400: {"confidence":0.0,"error":"field_name is required and must be a non-empty string","rules":[]}


Field: posts (GraphQL)
Schema Validations:
  - 1. Type Validation: Verify field matches expected type ()

============================================================
Example 7: REST API Endpoint Validation
============================================================
  Model server returned 400: {"confidence":0.0,"error":"field_name is required and must be a non-empty string","rules":[]}


Endpoint: GET /api/users/{id}
Status Code Validations:

============================================================
Bob AI Information
============================================================

Bob AI Details:
  name: Bob AI (Roo Code)
  type: VS Code AI Assistant
  connected: true
  requires_credentials: false

============================================================
✓ Disconnected from Bob AI
============================================================

✅ Example completed successfully!

Key Benefits:
  ✓ No external credentials required
  ✓ Works offline with intelligent rules
  ✓ Instant responses
  ✓ Consistent validation suggestions
  ✓ Easy to integrate into tests

Next Steps:
  1. Use Bob AI in your test framework
  2. Generate assertions automatically
  3. Improve test coverage
  4. Reduce manual assertion writing

BUILD SUCCESSFUL in 8s
4 actionable tasks: 4 executed
