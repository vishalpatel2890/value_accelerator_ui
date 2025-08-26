#!/usr/bin/env python3
"""
Test script to verify fail-fast behavior in deployment process.
This script tests that when a deployment step fails, the process:
1. Stops immediately
2. Returns an error response with success: false
3. Does not attempt to retry or continue
"""

import requests
import json
import time
import random

def test_deployment_fail_fast():
    """Test that deployment fails fast when encountering errors"""
    
    # Test configuration
    api_url = "http://localhost:8000/api/deploy/create"
    
    # Test Case 1: Test with valid token that should fail at ruleset creation
    # This simulates a real scenario where everything works until rulesets
    print("\n=== Test Case 1: Simulating ruleset creation failure ===")
    
    # Use a real token but with a repo name that will succeed initially
    test_repo_name = f"test-fail-fast-{int(time.time())}"
    
    payload = {
        "github_token": "ghp_REPLACE_WITH_VALID_TOKEN",  # Replace with a valid token for testing
        "repo_name": test_repo_name,
        "source_package": "retail-starter-pack",
        "project_name": "test-project",
        "organization": "",
        "create_rulesets": True,
        "td_api_key": "test_api_key",
        "td_region": "us01",
        "env_tokens": {
            "prod": "test_token_prod",
            "qa": "test_token_qa",
            "dev": "test_token_dev"
        }
    }
    
    print(f"Sending deployment request for repo: {test_repo_name}")
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {json.dumps(result, indent=2)}")
        
        # Verify the response
        if response.status_code == 200 and result.get('success') == False:
            print("✅ SUCCESS: Deployment failed as expected with success: false")
            print(f"Error message: {result.get('message')}")
            print(f"Errors: {result.get('errors')}")
            
            # Check that we got details about what was completed
            if result.get('details'):
                print("✅ Details provided about completed steps")
        else:
            print("❌ FAILED: Expected 200 with success: false")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Case 2: Test with invalid token (should fail immediately)
    print("=== Test Case 2: Testing with invalid token ===")
    
    payload = {
        "github_token": "invalid_token_12345",
        "repo_name": f"test-repo-{int(time.time())}",
        "source_package": "retail-starter-pack", 
        "project_name": "test-project",
        "organization": "",
        "create_rulesets": True
    }
    
    print("Sending deployment request with invalid token...")
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        result = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {json.dumps(result, indent=2)}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Invalid token rejected immediately")
        else:
            print("❌ FAILED: Expected 401 for invalid token")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Case 3: Test duplicate repository creation
    print("=== Test Case 3: Testing duplicate repository creation ===")
    
    # First create a repo (replace with valid token)
    test_repo_name = f"test-duplicate-{int(time.time())}"
    
    payload = {
        "github_token": "ghp_REPLACE_WITH_VALID_TOKEN",  # Replace with valid token
        "repo_name": test_repo_name,
        "source_package": "retail-starter-pack",
        "project_name": "test-project",
        "organization": "",
        "create_rulesets": False  # Disable to ensure first one succeeds
    }
    
    print(f"Creating initial repository: {test_repo_name}")
    
    try:
        # First request - should succeed
        response1 = requests.post(api_url, json=payload, timeout=30)
        result1 = response1.json()
        
        if response1.status_code == 200 and result1.get('success'):
            print("✅ First repository created successfully")
            
            # Now try to create the same repo again
            print("\nAttempting to create duplicate repository...")
            response2 = requests.post(api_url, json=payload, timeout=10)
            result2 = response2.json()
            
            print(f"Response Status: {response2.status_code}")
            print(f"Response Body: {json.dumps(result2, indent=2)}")
            
            if response2.status_code == 422:
                print("✅ SUCCESS: Duplicate repository rejected immediately")
            else:
                print("❌ FAILED: Expected 422 for duplicate repository")
        else:
            print("❌ Failed to create first repository for duplicate test")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    print("Testing Fail-Fast Deployment Behavior")
    print("=====================================")
    print("This test verifies that deployment fails immediately when errors occur")
    print("and does not attempt to retry or continue with subsequent steps.\n")
    
    print("NOTE: Replace 'ghp_REPLACE_WITH_VALID_TOKEN' with a valid GitHub token")
    print("for Test Cases 1 and 3 to work properly.\n")
    
    test_deployment_fail_fast()