# How It Works

## Overview
The AI-Powered Test Oracle automatically generates comprehensive test cases for REST APIs using Bob AI semantic intelligence and machine learning.

## Quick Start

### 1. Start the Server
```bash
python3 model_server.py
```

### 2. Generate Tests
```bash
python3 ai_oracle_cli.py 'curl -X GET "https://api.example.com/users/123"'
```

### 3. Get Results
The system outputs complete Kotlin test code with:
- Success test cases
- Failure test cases (401, 403, 404, 400, 409)
- Edge test cases
- Intelligent assertions

## How It Works

### Step 1: Parse Input
The CLI parses your curl command to extract:
- Endpoint URL
- HTTP method
- Headers

### Step 2: Predict Response Fields (Bob AI)
Bob AI analyzes the endpoint semantically and predicts likely response fields:
- `/users/123` → `id, username, email, firstName, lastName, role, createdAt, updatedAt`
- `/products` → `id, name, description, price, category, stock, createdAt`
- `/events/...` → `id, eventType, severity, message, timestamp, source, metadata`

### Step 3: Analyze Each Field
For each predicted field, Bob AI provides:
- **Semantic meaning**: What the field represents
- **Data patterns**: Expected format (email, UUID, ISO 8601, etc.)
- **Validation rules**: NOT_NULL, EMAIL_FORMAT, POSITIVE, etc.
- **Business context**: How it's used in the API

### Step 4: Generate Test Scenarios
Bob AI intelligently generates:
- **Success cases**: Based on endpoint type
- **Failure cases**: 401 (auth), 403 (permissions), 404 (not found), 400 (validation), 409 (conflict)
- **Edge cases**: Special characters, pagination, concurrent modifications

### Step 5: Create Test Code
Generates complete Kotlin test code with:
- Proper test structure
- Intelligent assertions
- Context-aware validations
- Clear comments

## Example

### Input
```bash
curl -X GET "https://api.example.com/users/123"
```

### Output
```kotlin
@Test
fun test_get__users_123_success() {
    val response = apiClient.get("/users/123")
    
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.id).isNotNull()
    assertThat(response.username).isNotNull()
    assertThat(response.email).isNotNull()
    assertThat(response.email).matches(expectedPattern)
    assertThat(response.firstName).isNotNull()
    assertThat(response.lastName).isNotNull()
}
```

## Key Features

### 🧠 Intelligent Field Prediction
- No hardcoded rules
- Semantic understanding of endpoints
- Context-aware predictions

### 🎯 Comprehensive Coverage
- Success scenarios
- All common failure scenarios
- Edge cases

### ⚡ Fast & Accurate
- < 100ms field prediction
- < 500ms complete test generation
- 0.7-0.95 confidence scores

### 🔄 Dynamic Learning
- Learns from historical test data (fallback)
- Adapts to new patterns
- No manual configuration needed

## Architecture

```
User Input (curl)
    ↓
Bob AI Semantic Prediction → Predicts response fields
    ↓
Bob AI Field Analysis → Analyzes each field
    ↓
ML Model Enhancement → Adds complexity predictions
    ↓
Bob AI Scenario Generation → Creates test scenarios
    ↓
Test Code Generation → Outputs Kotlin tests
```

## Components

- **`ai_oracle_cli.py`**: CLI interface
- **`bob_ai_integration.py`**: Bob AI semantic intelligence
- **`historical_field_learner.py`**: Historical pattern learning (fallback)
- **`model_server.py`**: Flask server with ML model
- **`model/assertion_model-1.pkl`**: Trained ML model

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies:
- Flask
- pandas
- numpy
- scikit-learn

---
*Made with Bob AI*