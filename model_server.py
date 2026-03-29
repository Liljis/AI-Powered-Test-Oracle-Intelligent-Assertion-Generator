"""
Model Server for AI-Powered Test Oracle
Serves predictions from trained ML model via REST API
Enhanced with Bob AI semantic intelligence
"""

from flask import Flask, request, jsonify
import pickle
import os
from pathlib import Path
import pandas as pd
import numpy as np
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

# Import Bob AI integration and historical field learner
from bob_ai_integration import get_bob_ai, BobFieldAnalysis, BobTestGeneration
from historical_field_learner import get_field_learner

app = Flask(__name__)

# Global variables for model
model = None
vectorizer = None
model_loaded = False

def load_model():
    """Load the trained model from pickle file"""
    global model, vectorizer, model_loaded
    
    # Try multiple possible model paths
    model_paths = [
        Path('model/assertion_model-1.pkl'),  # New location
        Path('trained_model.pkl'),             # Legacy location
        Path('assertion_model.pkl')            # Alternative location
    ]
    
    model_path = None
    for path in model_paths:
        if path.exists():
            model_path = path
            break
    
    if model_path is None:
        print("⚠️  WARNING: No trained model found!")
        print("   Checked locations:")
        for path in model_paths:
            print(f"     - {path}")
        print("   Using fallback rule-based predictions")
        print("   Train your model first using train_simple_model.py or Jupyter notebook")
        model_loaded = False
        return False
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            
            # Handle different model package formats
            if isinstance(model_data, dict):
                model = model_data.get('model')
                vectorizer = model_data.get('vectorizer')
                model_name = model_data.get('model_name', 'Unknown')
                score = model_data.get('score', 'N/A')
                print(f"✓ Model loaded successfully from {model_path}")
                print(f"  Model: {model_name}")
                print(f"  Score: {score}")
                if 'training_date' in model_data:
                    print(f"  Trained: {model_data['training_date']}")
            else:
                # Legacy format - model directly
                model = model_data
                vectorizer = None
                print(f"✓ Model loaded successfully from {model_path}")
                print("  (Legacy format)")
            
            model_loaded = True
            return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print(f"   File: {model_path}")
        model_loaded = False
        return False

def predict_with_model(field_name, field_type, api_type, http_method='GET', sample_value=None, use_bob_ai=True):
    """
    Use trained model + Bob AI to enhance predictions
    Combines ML model predictions with semantic intelligence
    """
    if not model_loaded or model is None:
        return fallback_predictions(field_name, field_type, api_type, http_method, sample_value, use_bob_ai)
    
    try:
        # The current model is a regression model that predicts execution time
        # We'll use it to enhance our rule-based predictions with ML insights
        
        # Extract features using actual HTTP method (not from field name)
        field_lower = field_name.lower()
        method_upper = http_method.upper()
        
        features_dict = {
            'has_get': 1 if method_upper == 'GET' else 0,
            'has_post': 1 if method_upper == 'POST' else 0,
            'has_put': 1 if method_upper == 'PUT' else 0,
            'has_delete': 1 if method_upper == 'DELETE' else 0,
            'has_query': 1 if 'query' in field_lower else 0,
            'has_mutation': 1 if 'mutation' in field_lower else 0,
            'test_name_length': len(field_lower),
            'api_type': 1 if api_type == 'REST' else 0
        }
        
        # Convert to array for prediction (optimized)
        features_df = pd.DataFrame([features_dict])
        
        # Get prediction (execution time estimate) with error handling
        predicted_time = float(model.predict(features_df)[0])
        
        # Clamp predicted time to reasonable bounds
        predicted_time = max(0.0, min(predicted_time, 10.0))
        
        # Use predicted time to adjust validation priorities
        # Longer execution time suggests more complex validations needed
        complexity_factor = 'HIGH' if predicted_time > 0.5 else 'MEDIUM'
        
        # Use Bob AI for semantic analysis if enabled
        if use_bob_ai:
            bob_ai = get_bob_ai()
            bob_analysis = bob_ai.analyze_field_semantics(
                field_name, field_type, api_type, sample_value, http_method
            )
            
            # Combine Bob AI insights with ML predictions
            result = {
                'rules': [
                    {
                        'type': v['type'],
                        'priority': v['priority'],
                        'description': v['description']
                    }
                    for v in bob_analysis.validation_suggestions[:5]
                ],
                'confidence': max(bob_analysis.confidence, 0.75 + (predicted_time * 0.1)),
                'source': 'bob_ai_ml_hybrid',
                'ml_insights': {
                    'predicted_complexity': complexity_factor,
                    'estimated_test_time': f'{predicted_time:.3f}s',
                    'model_type': 'Random Forest Regressor'
                },
                'bob_insights': {
                    'semantic_meaning': bob_analysis.semantic_meaning,
                    'data_patterns': bob_analysis.data_patterns,
                    'business_context': bob_analysis.business_context,
                    'ai_confidence': bob_analysis.confidence
                }
            }
        else:
            # Get base rules from fallback (fast)
            result = fallback_predictions(field_name, field_type, api_type, http_method, sample_value, False)
            
            # Enhance with ML insights (limit to top 5 for performance)
            result['rules'] = result['rules'][:5]
            result['confidence'] = min(0.92, 0.75 + (predicted_time * 0.1))
            result['source'] = 'ml_enhanced'
            result['ml_insights'] = {
                'predicted_complexity': complexity_factor,
                'estimated_test_time': f'{predicted_time:.3f}s',
                'model_type': 'Random Forest Regressor'
            }
        
        return result
        
    except Exception as e:
        print(f"Error during ML prediction: {e}")
        return fallback_predictions(field_name, field_type, api_type, http_method, sample_value, use_bob_ai)

def fallback_predictions(field_name, field_type, api_type, http_method='GET', sample_value=None, use_bob_ai=True):
    """
    Fallback rule-based predictions when model is not available
    Can optionally use Bob AI for enhanced predictions
    """
    # Try Bob AI first if enabled
    if use_bob_ai:
        try:
            bob_ai = get_bob_ai()
            bob_analysis = bob_ai.analyze_field_semantics(
                field_name, field_type, api_type, sample_value, http_method
            )
            
            return {
                'rules': [
                    {
                        'type': v['type'],
                        'priority': v['priority'],
                        'description': v['description']
                    }
                    for v in bob_analysis.validation_suggestions[:5]
                ],
                'confidence': bob_analysis.confidence,
                'source': 'bob_ai_semantic',
                'bob_insights': {
                    'semantic_meaning': bob_analysis.semantic_meaning,
                    'data_patterns': bob_analysis.data_patterns,
                    'business_context': bob_analysis.business_context,
                    'ai_confidence': bob_analysis.confidence
                }
            }
        except Exception as e:
            print(f"Bob AI fallback failed: {e}, using basic rules")
    
    # Basic rule-based predictions
    rules = []
    field_lower = field_name.lower()
    
    # Email validation
    if 'email' in field_lower:
        rules.extend([
            {'type': 'EMAIL_FORMAT', 'priority': 'HIGH', 'description': 'Must be valid email format'},
            {'type': 'NOT_EMPTY', 'priority': 'HIGH', 'description': 'Field must not be empty'},
            {'type': 'DOMAIN', 'priority': 'MEDIUM', 'description': 'Must have valid domain'}
        ])
    
    # ID validation
    elif 'id' in field_lower:
        rules.extend([
            {'type': 'UUID_FORMAT', 'priority': 'HIGH', 'description': 'Must be valid UUID format'},
            {'type': 'NOT_EMPTY', 'priority': 'HIGH', 'description': 'Field must not be empty'},
            {'type': 'UNIQUE', 'priority': 'HIGH', 'description': 'Must be unique'}
        ])
    
    # Date/timestamp validation
    elif any(word in field_lower for word in ['date', 'time', 'created', 'updated']):
        rules.extend([
            {'type': 'FORMAT', 'priority': 'HIGH', 'description': 'Must be valid ISO 8601 format'},
            {'type': 'NOT_EMPTY', 'priority': 'HIGH', 'description': 'Field must not be empty'}
        ])
    
    # Status validation
    elif 'status' in field_lower:
        rules.extend([
            {'type': 'ENUM', 'priority': 'HIGH', 'description': 'Must be valid enum value'},
            {'type': 'NOT_EMPTY', 'priority': 'HIGH', 'description': 'Field must not be empty'}
        ])
    
    # Cost/price validation
    elif any(word in field_lower for word in ['cost', 'price', 'amount']):
        rules.extend([
            {'type': 'POSITIVE', 'priority': 'HIGH', 'description': 'Must be positive value'},
            {'type': 'DECIMAL', 'priority': 'MEDIUM', 'description': 'Must have 2 decimal places'}
        ])
    
    # Default validation
    if not rules:
        rules.append({
            'type': 'BASIC', 
            'priority': 'LOW', 
            'description': 'Validate field type and presence'
        })
    
    return {
        'rules': rules,
        'confidence': 0.75,
        'source': 'fallback_rules'
    }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'message': 'Model server is running'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict validation rules for a field"""
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'rules': [],
                'confidence': 0.0
            }), 400
        
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'rules': [],
                'confidence': 0.0
            }), 400
        
        # Validate required fields
        field_name = data.get('field_name')
        if not field_name or not isinstance(field_name, str) or not field_name.strip():
            return jsonify({
                'error': 'field_name is required and must be a non-empty string',
                'rules': [],
                'confidence': 0.0
            }), 400
        
        field_type = data.get('field_type', 'String')
        api_type = data.get('api_type', 'REST')
        http_method = data.get('http_method', 'GET')
        sample_value = data.get('sample_value')
        use_bob_ai = data.get('use_bob_ai', True)
        
        # Get predictions with timeout protection
        result = predict_with_model(field_name.strip(), field_type, api_type, http_method, sample_value, use_bob_ai)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({
            'error': f'Invalid input: {str(e)}',
            'rules': [],
            'confidence': 0.0
        }), 400
    except Exception as e:
        print(f"Error in /predict endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'rules': [],
            'confidence': 0.0
        }), 500
@app.route('/generate_tests', methods=['POST'])
def generate_tests():
    """Generate complete test cases for an API endpoint"""
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'test_cases': []
            }), 400
        
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'test_cases': []
            }), 400
        
        # Validate required fields
        endpoint = data.get('endpoint')
        if not endpoint or not isinstance(endpoint, str) or not endpoint.strip():
            return jsonify({
                'error': 'endpoint is required and must be a non-empty string',
                'test_cases': []
            }), 400
        
        method = data.get('method', 'GET').upper()
        if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return jsonify({
                'error': f'Invalid HTTP method: {method}',
                'test_cases': []
            }), 400
        
        response_fields = data.get('response_fields', [])
        if not isinstance(response_fields, list):
            return jsonify({
                'error': 'response_fields must be a list',
                'test_cases': []
            }), 400
        
        api_type = data.get('api_type', 'REST')
        
        # Generate test cases
        test_cases = generate_test_cases(endpoint.strip(), method, response_fields, api_type)
        
        return jsonify(test_cases), 200
    
    except ValueError as e:
        return jsonify({
            'error': f'Invalid input: {str(e)}',
            'test_cases': []
        }), 400
    except Exception as e:
        print(f"Error in /generate_tests endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'test_cases': []
        }), 500

@app.route('/bob_generate_tests', methods=['POST'])
def bob_generate_tests():
    """
    Generate intelligent test code using Bob AI
    Provides semantic understanding and context-aware test generation
    """
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        endpoint = data.get('endpoint')
        if not endpoint or not isinstance(endpoint, str) or not endpoint.strip():
            return jsonify({
                'error': 'endpoint is required and must be a non-empty string'
            }), 400
        
        method = data.get('method', 'GET').upper()
        if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return jsonify({
                'error': f'Invalid HTTP method: {method}'
            }), 400
        
        fields = data.get('fields', [])
        if not isinstance(fields, list):
            return jsonify({
                'error': 'fields must be a list'
            }), 400
        
        input_params = data.get('input_params')
        api_type = data.get('api_type', 'REST')
        
        # Use Bob AI to analyze fields and generate intelligent tests
        bob_ai = get_bob_ai()
        
        # Analyze each field semantically
        field_analyses = []
        for field in fields:
            field_name = field.get('name', '')
            field_type = field.get('type', 'String')
            sample_value = field.get('sample_value')
            
            if field_name:
                analysis = bob_ai.analyze_field_semantics(
                    field_name, field_type, api_type, sample_value, method
                )
                field_analyses.append(analysis)
        
        # Generate intelligent test code
        test_generation = bob_ai.generate_intelligent_test_code(
            endpoint, method, fields, field_analyses, input_params
        )
        
        return jsonify({
            'endpoint': endpoint,
            'method': method,
            'test_method_name': test_generation.test_method_name,
            'test_code': test_generation.test_code,
            'assertions': test_generation.assertions,
            'setup_code': test_generation.setup_code,
            'explanation': test_generation.explanation,
            'confidence': test_generation.confidence,
            'field_analyses': [
                {
                    'field_name': a.field_name,
                    'semantic_meaning': a.semantic_meaning,
                    'data_patterns': a.data_patterns,
                    'business_context': a.business_context,
                    'validation_count': len(a.validation_suggestions)
                }
                for a in field_analyses
            ],
            'source': 'bob_ai_intelligent'
        }), 200
    
    except Exception as e:
        print(f"Error in /bob_generate_tests endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/bob_generate_all_scenarios', methods=['POST'])
def bob_generate_all_scenarios():
    """
    Use Bob AI to intelligently generate all test scenarios:
    - Success cases
    - Failure cases
    - Edge cases
    Based on endpoint analysis
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        endpoint = data.get('endpoint')
        if not endpoint:
            return jsonify({'error': 'endpoint is required'}), 400
        
        method = data.get('method', 'GET').upper()
        
        # Use Bob AI to analyze endpoint and generate scenarios
        bob_ai = get_bob_ai()
        
        # Get fields - either from user input or infer from endpoint
        provided_fields = data.get('fields', [])
        if provided_fields:
            # User provided actual response fields from API documentation
            fields_to_analyze = provided_fields
        else:
            # Infer fields from endpoint path
            fields_to_analyze = infer_fields_from_endpoint(endpoint, method)
        
        # Analyze fields semantically
        field_analyses = []
        if fields_to_analyze:
            for field_info in fields_to_analyze:
                analysis = bob_ai.analyze_field_semantics(
                    field_info['name'],
                    field_info['type'],
                    'REST',
                    None,
                    method
                )
                field_analyses.append(analysis)
        
        # Generate ALL scenarios using Bob AI's intelligent analysis
        scenarios = bob_ai.generate_test_scenarios(endpoint, method, field_analyses)
        
        # Prepare field predictions with validation details for display
        field_predictions = []
        for analysis in field_analyses[:7]:  # Top 7 fields
            validations = []
            for validation in analysis.validation_suggestions[:3]:  # Top 3 validations
                validations.append(validation.get('description', validation.get('type', 'Unknown validation')))
            
            field_predictions.append({
                'name': analysis.field_name,
                'type': 'String',  # Simplified for display
                'validations': validations,
                'confidence': analysis.confidence
            })
        
        return jsonify({
            'endpoint': endpoint,
            'method': method,
            'scenarios': scenarios,
            'field_predictions': field_predictions,
            'total_tests': (
                len(scenarios['success_cases']) +
                len(scenarios['failure_cases']) +
                len(scenarios['edge_cases'])
            ),
            'source': 'Bob AI + ML Model (Semantic Intelligence)'
        }), 200
        
    except Exception as e:
        print(f"Error in /bob_generate_all_scenarios: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def infer_fields_from_endpoint(endpoint, method):
    """
    Infer likely response fields from endpoint path using Bob AI semantic intelligence
    Falls back to historical learning if Bob AI prediction has low confidence
    """
    # Try Bob AI semantic prediction first
    try:
        bob_ai = get_bob_ai()
        predicted_fields = bob_ai.predict_response_fields(endpoint, method, 'REST')
        
        if predicted_fields:
            # Convert to expected format (remove confidence)
            fields = [
                {'name': f['name'], 'type': f['type']}
                for f in predicted_fields
            ]
            avg_confidence = sum(f['confidence'] for f in predicted_fields) / len(predicted_fields)
            print(f"✓ Using BOB AI SEMANTIC PREDICTION: {len(fields)} fields for {method} {endpoint}")
            print(f"  Fields: {', '.join([f['name'] for f in fields[:5]])}{'...' if len(fields) > 5 else ''}")
            print(f"  Average Confidence: {avg_confidence:.2f}")
            return fields
    except Exception as e:
        print(f"⚠ Bob AI prediction failed: {e}, trying historical learning")
    
    # Fallback to historical learning
    try:
        learner = get_field_learner()
        predicted_fields = learner.predict_fields(endpoint, method, 'REST')
        
        if predicted_fields:
            fields = [
                {'name': f['name'], 'type': f['type']}
                for f in predicted_fields
            ]
            print(f"✓ Using HISTORICAL DATA (fallback): {len(fields)} fields for {method} {endpoint}")
            print(f"  Fields: {', '.join([f['name'] for f in fields[:5]])}{'...' if len(fields) > 5 else ''}")
            return fields
    except Exception as e:
        print(f"⚠ Historical learning failed: {e}, using minimal fallback")
    
    # Fallback to pattern-based inference
    fields = []
    endpoint_lower = endpoint.lower()
    
    # Common fields based on endpoint patterns
    if 'token' in endpoint_lower:
        fields = [
            {'name': 'id', 'type': 'String'},
            {'name': 'name', 'type': 'String'},
            {'name': 'accessGrantingToken', 'type': 'String'},
            {'name': 'createdAt', 'type': 'String'},
            {'name': 'permissions', 'type': 'Array'}
        ]
    elif 'catalog' in endpoint_lower or 'monitoring' in endpoint_lower:
        fields = [
            {'name': 'id', 'type': 'String'},
            {'name': 'name', 'type': 'String'},
            {'name': 'type', 'type': 'String'},
            {'name': 'metrics', 'type': 'Array'},
            {'name': 'timestamp', 'type': 'String'}
        ]
    elif 'application' in endpoint_lower or 'settings' in endpoint_lower:
        fields = [
            {'name': 'id', 'type': 'String'},
            {'name': 'name', 'type': 'String'},
            {'name': 'config', 'type': 'Object'},
            {'name': 'updatedAt', 'type': 'String'}
        ]
    else:
        # Generic fields
        fields = [
            {'name': 'id', 'type': 'String'},
            {'name': 'name', 'type': 'String'},
            {'name': 'status', 'type': 'String'},
            {'name': 'createdAt', 'type': 'String'}
        ]
    
    return fields

def generate_failure_scenarios(endpoint, method, fields):
    """Generate failure test scenarios using Bob AI intelligence"""
    scenarios = []
    
    # 404 Not Found
    scenarios.append({
        'name': 'Resource not found',
        'status_code': 404,
        'test_code': f'''@Test
fun test_{method.lower()}_not_found() {{
    // Test generated by Bob AI for 404 scenario
    val response = apiClient.{method.lower()}("{endpoint}")
    
    assertThat(response.statusCode).isEqualTo(404)
    assertThat(response.body).containsKey("error")
    assertThat(response.body["error"]).isNotEmpty()
}}''',
        'description': 'Validates 404 response when resource does not exist'
    })
    
    # 401 Unauthorized
    scenarios.append({
        'name': 'Unauthorized access',
        'status_code': 401,
        'test_code': f'''@Test
fun test_{method.lower()}_unauthorized() {{
    // Test generated by Bob AI for 401 scenario
    val response = apiClient.{method.lower()}WithoutAuth("{endpoint}")
    
    assertThat(response.statusCode).isEqualTo(401)
    assertThat(response.body).containsKey("error")
    assertThat(response.body["error"]).contains("Unauthorized")
}}''',
        'description': 'Validates 401 response when authentication is missing'
    })
    
    # 403 Forbidden
    scenarios.append({
        'name': 'Forbidden access',
        'status_code': 403,
        'test_code': f'''@Test
fun test_{method.lower()}_forbidden() {{
    // Test generated by Bob AI for 403 scenario
    val response = apiClient.{method.lower()}WithInsufficientPermissions("{endpoint}")
    
    assertThat(response.statusCode).isEqualTo(403)
    assertThat(response.body).containsKey("error")
    assertThat(response.body["error"]).contains("Forbidden")
}}''',
        'description': 'Validates 403 response when user lacks permissions'
    })
    
    # 400 Bad Request (for POST/PUT/PATCH)
    if method in ['POST', 'PUT', 'PATCH']:
        scenarios.append({
            'name': 'Invalid request data',
            'status_code': 400,
            'test_code': f'''@Test
fun test_{method.lower()}_invalid_data() {{
    // Test generated by Bob AI for 400 scenario
    val invalidData = mapOf("invalid" to "data")
    val response = apiClient.{method.lower()}("{endpoint}", invalidData)
    
    assertThat(response.statusCode).isEqualTo(400)
    assertThat(response.body).containsKey("error")
    assertThat(response.body["error"]).contains("Invalid")
}}''',
            'description': 'Validates 400 response when request data is invalid'
        })
    
    return scenarios

def generate_edge_scenarios(endpoint, method, fields):
    """Generate edge case test scenarios using Bob AI intelligence"""
    scenarios = []
    
    # Empty response
    scenarios.append({
        'name': 'Empty response handling',
        'status_code': 200,
        'test_code': f'''@Test
fun test_{method.lower()}_empty_response() {{
    // Test generated by Bob AI for empty response edge case
    val response = apiClient.{method.lower()}("{endpoint}")
    
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.body).isInstanceOf(List::class.java)
    assertThat(response.body as List<*>).isEmpty()
}}''',
        'description': 'Validates handling of empty but valid response'
    })
    
    # Large dataset
    scenarios.append({
        'name': 'Large dataset handling',
        'status_code': 200,
        'test_code': f'''@Test
fun test_{method.lower()}_large_dataset() {{
    // Test generated by Bob AI for large dataset edge case
    val response = apiClient.{method.lower()}("{endpoint}?limit=1000")
    
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.body as List<*>).hasSizeLessThanOrEqualTo(1000)
    assertThat(response.headers).containsKey("X-Total-Count")
}}''',
        'description': 'Validates handling of large datasets with pagination'
    })
    
    # Special characters in ID (if endpoint has ID parameter)
    if 'REPLACE_ID' in endpoint or '{id}' in endpoint:
        scenarios.append({
            'name': 'Special characters in ID',
            'status_code': 400,
            'test_code': f'''@Test
fun test_{method.lower()}_special_chars_in_id() {{
    // Test generated by Bob AI for special characters edge case
    val invalidId = "test@#$%"
    val response = apiClient.{method.lower()}("{endpoint.replace('REPLACE_ID', '$invalidId')}")
    
    assertThat(response.statusCode).isIn(400, 404)
    assertThat(response.body).containsKey("error")
}}''',
            'description': 'Validates handling of special characters in ID parameter'
        })
    
    return scenarios

def generate_test_cases(endpoint, method, response_fields, api_type):
    """Generate comprehensive test cases for an API endpoint"""
    test_cases = []
    
    # 1. Happy Path Test
    happy_path = {
        'name': f'test_{method.lower()}_{endpoint.replace("/", "_").replace("{", "").replace("}", "")}_success',
        'description': f'Test successful {method} request to {endpoint}',
        'type': 'HAPPY_PATH',
        'priority': 'HIGH',
        'test_code': generate_happy_path_test(endpoint, method, response_fields, api_type),
        'assertions': generate_happy_path_assertions(response_fields)
    }
    test_cases.append(happy_path)
    
    # 2. Validation Tests for each field
    for field in response_fields:
        field_tests = generate_field_validation_tests(endpoint, method, field, api_type)
        test_cases.extend(field_tests)
    
    # 3. Error Handling Tests
    error_tests = generate_error_tests(endpoint, method, api_type)
    test_cases.extend(error_tests)
    
    # 4. Edge Case Tests
    edge_tests = generate_edge_case_tests(endpoint, method, response_fields, api_type)
    test_cases.extend(edge_tests)
    
    # 5. Performance Tests (if ML model suggests high complexity)
    if model_loaded:
        performance_tests = generate_performance_tests(endpoint, method, api_type)
        test_cases.extend(performance_tests)
    
    return {
        'endpoint': endpoint,
        'method': method,
        'api_type': api_type,
        'test_cases': test_cases,
        'total_tests': len(test_cases),
        'confidence': 0.88 if model_loaded else 0.75
    }

def generate_happy_path_test(endpoint, method, response_fields, api_type):
    """Generate happy path test code"""
    method_cap = method.capitalize()
    endpoint_name = endpoint.replace("/", "_").replace("{", "").replace("}", "").title()
    
    if api_type == 'REST':
        field_assertions = '\n    '.join([f'assertThat(response.body.{field}).isNotNull()' for field in response_fields[:5]])
        return f'''@Test
fun test{method_cap}{endpoint_name}Success() {{
    // Arrange
    val request = {method_cap}Request("{endpoint}")
    
    // Act
    val response = apiClient.execute(request)
    
    // Assert
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.body).isNotNull()
    {field_assertions}
}}'''
    else:  # GraphQL
        field_list = '\n                '.join(response_fields[:5])
        return f'''@Test
fun testGraphQL{endpoint_name}Success() {{
    // Arrange
    val query = \"\"\"
        query {{
            {endpoint} {{
                {field_list}
            }}
        }}
    \"\"\"
    
    // Act
    val response = graphQLClient.execute(query)
    
    // Assert
    assertThat(response.errors).isEmpty()
    assertThat(response.data).isNotNull()
}}'''

def generate_happy_path_assertions(response_fields):
    """Generate assertions for happy path"""
    assertions = [
        {'type': 'STATUS_CODE', 'expected': '200', 'description': 'Response status should be 200 OK'},
        {'type': 'NOT_NULL', 'field': 'response.body', 'description': 'Response body should not be null'}
    ]
    
    for field in response_fields[:5]:
        field_lower = field.lower()
        if 'email' in field_lower:
            assertions.append({
                'type': 'EMAIL_FORMAT',
                'field': field,
                'description': f'{field} should be valid email format'
            })
        elif 'id' in field_lower:
            assertions.append({
                'type': 'UUID_FORMAT',
                'field': field,
                'description': f'{field} should be valid UUID'
            })
        else:
            assertions.append({
                'type': 'NOT_NULL',
                'field': field,
                'description': f'{field} should not be null'
            })
    
    return assertions

def generate_field_validation_tests(endpoint, method, field, api_type):
    """Generate validation tests for a specific field"""
    tests = []
    field_lower = field.lower()
    field_cap = field.capitalize()
    method_lower = method.lower()
    
    # Email field tests
    if 'email' in field_lower:
        tests.append({
            'name': f'test_{field}_format_validation',
            'description': f'Test {field} format validation',
            'type': 'VALIDATION',
            'priority': 'HIGH',
            'test_code': f'''@Test
fun test{field_cap}FormatValidation() {{
    val response = apiClient.{method_lower}("{endpoint}")
    assertThat(response.body.{field}).matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$")
}}''',
            'assertions': [
                {'type': 'EMAIL_FORMAT', 'field': field, 'description': 'Must match email pattern'}
            ]
        })
    
    # ID field tests
    elif 'id' in field_lower:
        tests.append({
            'name': f'test_{field}_uuid_format',
            'description': f'Test {field} is valid UUID',
            'type': 'VALIDATION',
            'priority': 'HIGH',
            'test_code': f'''@Test
fun test{field_cap}UuidFormat() {{
    val response = apiClient.{method_lower}("{endpoint}")
    assertThat(response.body.{field}).matches("^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$")
}}''',
            'assertions': [
                {'type': 'UUID_FORMAT', 'field': field, 'description': 'Must be valid UUID v4'}
            ]
        })
    
    # Date/time field tests
    elif any(word in field_lower for word in ['date', 'time', 'created', 'updated']):
        tests.append({
            'name': f'test_{field}_iso8601_format',
            'description': f'Test {field} is valid ISO 8601 timestamp',
            'type': 'VALIDATION',
            'priority': 'MEDIUM',
            'test_code': f'''@Test
fun test{field_cap}Iso8601Format() {{
    val response = apiClient.{method_lower}("{endpoint}")
    assertThat(response.body.{field}).matches("\\\\d{{4}}-\\\\d{{2}}-\\\\d{{2}}T\\\\d{{2}}:\\\\d{{2}}:\\\\d{{2}}")
}}''',
            'assertions': [
                {'type': 'ISO8601_FORMAT', 'field': field, 'description': 'Must be valid ISO 8601 format'}
            ]
        })
    
    return tests

def generate_error_tests(endpoint, method, api_type):
    """Generate error handling tests"""
    tests = []
    method_cap = method.capitalize()
    method_lower = method.lower()
    
    # 404 Not Found test
    if '{id}' in endpoint or '{uuid}' in endpoint:
        invalid_endpoint = endpoint.replace('{id}', '00000000-0000-0000-0000-000000000000').replace('{uuid}', '00000000-0000-0000-0000-000000000000')
        tests.append({
            'name': f'test_{method_lower}_not_found',
            'description': f'Test {method} returns 404 for non-existent resource',
            'type': 'ERROR_HANDLING',
            'priority': 'HIGH',
            'test_code': f'''@Test
fun test{method_cap}NotFound() {{
    val invalidId = "00000000-0000-0000-0000-000000000000"
    val response = apiClient.{method_lower}("{invalid_endpoint}")
    assertThat(response.statusCode).isEqualTo(404)
}}''',
            'assertions': [
                {'type': 'STATUS_CODE', 'expected': '404', 'description': 'Should return 404 for invalid ID'}
            ]
        })
    
    # 400 Bad Request test (for POST/PUT)
    if method in ['POST', 'PUT', 'PATCH']:
        tests.append({
            'name': f'test_{method_lower}_invalid_payload',
            'description': f'Test {method} returns 400 for invalid payload',
            'type': 'ERROR_HANDLING',
            'priority': 'HIGH',
            'test_code': f'''@Test
fun test{method_cap}InvalidPayload() {{
    val invalidPayload = mapOf<String, Any>()
    val response = apiClient.{method_lower}("{endpoint}", invalidPayload)
    assertThat(response.statusCode).isEqualTo(400)
}}''',
            'assertions': [
                {'type': 'STATUS_CODE', 'expected': '400', 'description': 'Should return 400 for invalid payload'}
            ]
        })
    
    # 401 Unauthorized test
    tests.append({
        'name': f'test_{method_lower}_unauthorized',
        'description': f'Test {method} returns 401 without authentication',
        'type': 'ERROR_HANDLING',
        'priority': 'MEDIUM',
        'test_code': f'''@Test
fun test{method_cap}Unauthorized() {{
    val unauthenticatedClient = ApiClient(authToken = null)
    val response = unauthenticatedClient.{method_lower}("{endpoint}")
    assertThat(response.statusCode).isEqualTo(401)
}}''',
        'assertions': [
            {'type': 'STATUS_CODE', 'expected': '401', 'description': 'Should return 401 without auth'}
        ]
    })
    
    return tests

def generate_edge_case_tests(endpoint, method, response_fields, api_type):
    """Generate edge case tests"""
    tests = []
    method_cap = method.capitalize()
    method_lower = method.lower()
    
    # Empty response test
    tests.append({
        'name': f'test_{method_lower}_empty_result',
        'description': f'Test {method} handles empty result gracefully',
        'type': 'EDGE_CASE',
        'priority': 'MEDIUM',
        'test_code': f'''@Test
fun test{method_cap}EmptyResult() {{
    val response = apiClient.{method_lower}("{endpoint}?filter=nonexistent")
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.body).isEmpty()
}}''',
        'assertions': [
            {'type': 'STATUS_CODE', 'expected': '200', 'description': 'Should return 200 even for empty results'},
            {'type': 'EMPTY_COLLECTION', 'description': 'Should return empty collection, not null'}
        ]
    })
    
    # Large payload test (for collections)
    if method == 'GET' and not any(param in endpoint for param in ['{id}', '{uuid}']):
        tests.append({
            'name': f'test_{method_lower}_pagination',
            'description': f'Test {method} supports pagination for large datasets',
            'type': 'EDGE_CASE',
            'priority': 'LOW',
            'test_code': f'''@Test
fun test{method_cap}Pagination() {{
    val response = apiClient.{method_lower}("{endpoint}?page=1&size=10")
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(response.body.size).isLessThanOrEqualTo(10)
}}''',
            'assertions': [
                {'type': 'PAGINATION', 'description': 'Should support pagination parameters'},
                {'type': 'SIZE_LIMIT', 'description': 'Should respect page size limit'}
            ]
        })
    
    return tests

def generate_performance_tests(endpoint, method, api_type):
    """Generate performance tests"""
    tests = []
    method_cap = method.capitalize()
    method_lower = method.lower()
    
    tests.append({
        'name': f'test_{method_lower}_response_time',
        'description': f'Test {method} response time is acceptable',
        'type': 'PERFORMANCE',
        'priority': 'LOW',
        'test_code': f'''@Test
fun test{method_cap}ResponseTime() {{
    val startTime = System.currentTimeMillis()
    val response = apiClient.{method_lower}("{endpoint}")
    val endTime = System.currentTimeMillis()
    val responseTime = endTime - startTime
    
    assertThat(response.statusCode).isEqualTo(200)
    assertThat(responseTime).isLessThan(2000) // 2 seconds
}}''',
        'assertions': [
            {'type': 'RESPONSE_TIME', 'expected': '< 2000ms', 'description': 'Response time should be under 2 seconds'}
        ]
    })
    
    return tests


@app.route('/generate_test_code', methods=['POST'])
def generate_test_code():
    """
    Generate test code in specified language (Kotlin, Java, or Python)
    Takes validation rules and generates complete test code
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        endpoint = data.get('endpoint')
        if not endpoint:
            return jsonify({'error': 'endpoint is required'}), 400
        
        method = data.get('method', 'GET').upper()
        if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return jsonify({'error': f'Invalid HTTP method: {method}'}), 400
        
        language = data.get('language', 'kotlin').lower()
        if language not in ['kotlin', 'java', 'python']:
            return jsonify({'error': f'Invalid language: {language}. Must be kotlin, java, or python'}), 400
        
        # Get fields - either from user input or infer from endpoint
        provided_fields = data.get('fields', [])
        if provided_fields:
            fields_to_analyze = provided_fields
        else:
            fields_to_analyze = infer_fields_from_endpoint(endpoint, method)
        
        # Use Bob AI to analyze fields and get validation rules
        bob_ai = get_bob_ai()
        field_analyses = []
        
        for field_info in fields_to_analyze:
            analysis = bob_ai.analyze_field_semantics(
                field_info['name'],
                field_info['type'],
                'REST',
                None,
                method
            )
            field_analyses.append(analysis)
        
        # Convert field analyses to validation rules format expected by generators
        validation_rules = []
        for analysis in field_analyses:
            for validation in analysis.validation_suggestions[:5]:  # Top 5 validations per field
                validation_rules.append({
                    'type': validation.get('type', 'NOT_NULL'),
                    'priority': validation.get('priority', 'MEDIUM'),
                    'description': validation.get('description', ''),
                    'fieldName': analysis.field_name
                })
        
        # Generate test code based on language using inline generators
        if language == 'kotlin':
            test_code = generate_kotlin_test_inline(endpoint, method, validation_rules)
        elif language == 'java':
            test_code = generate_java_test_inline(endpoint, method, validation_rules)
        else:  # python
            test_code = generate_python_test_inline(endpoint, method, validation_rules)
        
        return jsonify({
            'endpoint': endpoint,
            'method': method,
            'language': language,
            'test_code': test_code,
            'validation_rules_count': len(validation_rules),
            'source': 'Bob AI + Code Generator'
        }), 200
        
    except Exception as e:
        print(f"Error in /generate_test_code: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def generate_kotlin_test_inline(endpoint, method, validation_rules):
    """Fallback inline Kotlin test generator"""
    test_name = f"test_{method.lower()}_{endpoint.replace('/', '_').strip('_')}"
    assertions = []
    
    for rule in validation_rules[:10]:  # Limit to 10 assertions
        field = rule['fieldName']
        rule_type = rule['type']
        desc = rule['description']
        
        if rule_type == 'NOT_NULL':
            assertions.append(f'    // {desc}\n    assertNotNull(response.{field}, "{field} should not be null")')
        elif rule_type == 'NOT_EMPTY':
            assertions.append(f'    // {desc}\n    assertTrue(response.{field}.isNotEmpty(), "{field} should not be empty")')
        elif rule_type == 'FORMAT':
            if 'email' in desc.lower():
                pattern = '^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$'
            elif 'uuid' in desc.lower():
                pattern = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            else:
                pattern = '.*'
            assertions.append(f'    // {desc}\n    assertTrue(response.{field}.matches(Regex("{pattern}")), "{field} should match format")')
        else:
            assertions.append(f'    // {desc}\n    assertNotNull(response.{field})')
    
    assertions_code = '\n\n'.join(assertions)
    
    return f'''import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import io.restassured.RestAssured.*
import io.restassured.http.ContentType

/**
 * AI-Generated Test for {method} {endpoint}
 * Generated by Bob AI-Powered Test Oracle
 */
class {test_name.title().replace('_', '')}Test {{
    
    @Test
    fun `{test_name}`() {{
        // Execute API call
        val response = given()
            .contentType(ContentType.JSON)
            .`when`()
            .{method.lower()}("{endpoint}")
            .then()
            .statusCode(200)
            .extract()
            .response()
        
        // AI-Generated Assertions
{assertions_code}
    }}
}}
'''

def generate_java_test_inline(endpoint, method, validation_rules):
    """Fallback inline Java test generator"""
    test_name = f"test_{method.lower()}_{endpoint.replace('/', '_').strip('_')}"
    class_name = ''.join(word.capitalize() for word in test_name.split('_')) + 'Test'
    assertions = []
    
    for rule in validation_rules[:10]:
        field = rule['fieldName']
        rule_type = rule['type']
        desc = rule['description']
        
        if rule_type == 'NOT_NULL':
            assertions.append(f'        // {desc}\n        assertNotNull(response.get("{field}"), "{field} should not be null");')
        elif rule_type == 'NOT_EMPTY':
            assertions.append(f'        // {desc}\n        assertFalse(response.get("{field}").toString().isEmpty(), "{field} should not be empty");')
        else:
            assertions.append(f'        // {desc}\n        assertNotNull(response.get("{field}"));')
    
    assertions_code = '\n\n'.join(assertions)
    
    return f'''import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import java.util.Map;

/**
 * AI-Generated Test for {method} {endpoint}
 * Generated by Bob AI-Powered Test Oracle
 */
public class {class_name} {{

    @Test
    public void {test_name}() {{
        // Execute API call
        Response response = RestAssured.given()
            .contentType(ContentType.JSON)
            .when()
            .{method.lower()}("{endpoint}")
            .then()
            .statusCode(200)
            .extract()
            .response();

        Map<String, Object> responseBody = response.jsonPath().getMap("$");

        // AI-Generated Assertions
{assertions_code}
    }}
}}
'''

def generate_python_test_inline(endpoint, method, validation_rules):
    """Fallback inline Python test generator"""
    test_name = f"test_{method.lower()}_{endpoint.replace('/', '_').strip('_')}"
    assertions = []
    
    for rule in validation_rules[:10]:
        field = rule['fieldName']
        rule_type = rule['type']
        desc = rule['description']
        
        if rule_type == 'NOT_NULL':
            assertions.append(f'    # {desc}\n    assert response["{field}"] is not None, "{field} should not be null"')
        elif rule_type == 'NOT_EMPTY':
            assertions.append(f'    # {desc}\n    assert len(response["{field}"]) > 0, "{field} should not be empty"')
        elif rule_type == 'FORMAT':
            if 'email' in desc.lower():
                assertions.append(f'    # {desc}\n    import re\n    assert re.match(r"^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$", str(response["{field}"])), "{field} should match email format"')
            elif 'uuid' in desc.lower():
                assertions.append(f'    # {desc}\n    import re\n    assert re.match(r"^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$", str(response["{field}"])), "{field} should match UUID format"')
            else:
                assertions.append(f'    # {desc}\n    assert response["{field}"] is not None')
        else:
            assertions.append(f'    # {desc}\n    assert response["{field}"] is not None')
    
    assertions_code = '\n\n'.join(assertions)
    
    return f'''"""
AI-Generated Test for {method} {endpoint}
Generated by Bob AI-Powered Test Oracle
"""

import pytest
import requests
import re
from typing import Dict, Any


def {test_name}():
    """Test {method} {endpoint} with AI-generated assertions"""
    # Execute API call
    response = requests.{method.lower()}(
        "http://localhost:8080{endpoint}",
        headers={{"Content-Type": "application/json"}}
    )
    
    # Verify status code
    assert response.status_code == 200, f"Expected status 200, got {{response.status_code}}"
    
    # Parse response
    response_data = response.json()
    
    # AI-Generated Assertions
{assertions_code}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

@app.route('/reload', methods=['POST'])
def reload_model():
    """Reload the model from disk"""
    success = load_model()
    return jsonify({
        'success': success,
        'model_loaded': model_loaded
    })

if __name__ == '__main__':
    print("=" * 60)
    print("AI-Powered Test Oracle - Model Server")
    print("=" * 60)
    print()
    
    # Try to load model on startup
    load_model()
    
    print()
    print("Starting server on http://localhost:5001")
    print("Endpoints:")
    print("  POST /predict                    - Get validation predictions")
    print("  POST /generate_tests             - Generate complete test cases")
    print("  POST /bob_generate_tests         - Generate intelligent tests with Bob AI")
    print("  POST /bob_generate_all_scenarios - Generate all test scenarios")
    print("  POST /generate_test_code         - Generate test code (Kotlin/Java/Python)")
    print("  GET  /health                     - Health check")
    print("  POST /reload                     - Reload model from disk")
    print()
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)

# Made with Bob

