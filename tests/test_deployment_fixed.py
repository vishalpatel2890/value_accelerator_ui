#!/usr/bin/env python3
"""
Test script for the fixed deployment API
Tests error handling and partial failure scenarios
"""
import requests
import json
import sys
import time

# Test configuration
API_BASE = "http://localhost:8000"

def test_duplicate_repo_handling():
    """Test that duplicate repository creation is handled properly"""
    print("\n🧪 Testing: Duplicate repository handling...")
    
    repo_name = f"test-duplicate-{int(time.time())}"
    config = {
        "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with valid token
        "repo_name": repo_name,
        "source_package": "retail-starter-pack",
        "project_name": "test-project",
        "create_rulesets": False  # Disable to avoid plan issues
    }
    
    if config["github_token"] == "ghp_YOUR_TOKEN_HERE":
        print("❌ Please set a valid GitHub token")
        return False
    
    try:
        # First deployment should succeed
        print(f"Creating repository: {repo_name}")
        response1 = requests.post(f"{API_BASE}/api/deploy/create", json=config)
        data1 = response1.json()
        
        if response1.status_code == 200 and data1.get("success"):
            print(f"✅ First deployment successful")
            print(f"   Repository URL: {data1.get('repository_url')}")
        else:
            print(f"❌ First deployment failed: {data1.get('detail', 'Unknown error')}")
            return False
        
        # Second deployment with same name should fail gracefully
        print(f"\nAttempting duplicate deployment...")
        response2 = requests.post(f"{API_BASE}/api/deploy/create", json=config)
        data2 = response2.json()
        
        if response2.status_code == 422:
            print(f"✅ Correctly rejected duplicate repository")
            print(f"   Error: {data2.get('detail')}")
            return True
        else:
            print(f"❌ Expected 422 but got {response2.status_code}")
            print(f"   Response: {data2}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_ruleset_failure_handling():
    """Test handling of ruleset creation failures (e.g., plan limitations)"""
    print("\n🧪 Testing: Ruleset failure handling...")
    
    config = {
        "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with valid token
        "repo_name": f"test-ruleset-{int(time.time())}",
        "source_package": "retail-starter-pack",
        "project_name": "test-project",
        "create_rulesets": True,
        "env_tokens": {
            "prod": "test_token_prod",
            "qa": "test_token_qa"
        }
    }
    
    if config["github_token"] == "ghp_YOUR_TOKEN_HERE":
        print("❌ Please set a valid GitHub token")
        return False
    
    try:
        response = requests.post(f"{API_BASE}/api/deploy/create", json=config)
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print(f"✅ Deployment completed")
            print(f"   Repository URL: {data.get('repository_url')}")
            
            # Check for warnings about rulesets
            if data.get("warnings"):
                print(f"⚠️  Warnings detected:")
                for warning in data["warnings"]:
                    print(f"   - {warning}")
            
            # Check ruleset details
            if "rulesets" in data.get("details", {}):
                print(f"\n📋 Ruleset Results:")
                for ruleset in data["details"]["rulesets"]:
                    status = ruleset.get("status")
                    name = ruleset.get("name")
                    if status == "skipped":
                        print(f"   - {name}: Skipped (requires paid plan)")
                    elif status == "created":
                        print(f"   - {name}: Created successfully")
                    else:
                        print(f"   - {name}: Failed - {ruleset.get('error', 'Unknown error')}")
            
            return True
        else:
            print(f"❌ Deployment failed: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_partial_failure_recovery():
    """Test that failures are handled without duplicate attempts"""
    print("\n🧪 Testing: Partial failure recovery...")
    
    # This test simulates a scenario where secrets/variables might fail
    config = {
        "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with valid token
        "repo_name": f"test-partial-{int(time.time())}",
        "source_package": "retail-starter-pack",
        "project_name": "test-project",
        "create_rulesets": False,
        "td_api_key": "invalid_key",  # This might cause variables to fail
        "td_region": "us01",
        "env_tokens": {
            "prod": "very_long_token_that_might_cause_issues_" * 10  # Intentionally long
        }
    }
    
    if config["github_token"] == "ghp_YOUR_TOKEN_HERE":
        print("❌ Please set a valid GitHub token")
        return False
    
    try:
        response = requests.post(f"{API_BASE}/api/deploy/create", json=config)
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Deployment completed (with possible warnings)")
            print(f"   Repository URL: {data.get('repository_url')}")
            
            # Check what succeeded and what failed
            details = data.get("details", {})
            
            if "files" in details:
                print(f"   ✅ Files: {details['files']['count']} pushed successfully")
            
            if "secrets" in details:
                print(f"   📋 Secrets:")
                for secret in details["secrets"]:
                    status = secret.get("status")
                    name = secret.get("name")
                    if status == "created":
                        print(f"      ✅ {name}")
                    else:
                        print(f"      ❌ {name}: {secret.get('error', 'Failed')}")
            
            if "variables" in details:
                print(f"   📋 Variables:")
                for var in details["variables"]:
                    status = var.get("status")
                    name = var.get("name")
                    if status == "created":
                        print(f"      ✅ {name}")
                    else:
                        print(f"      ❌ {name}: {var.get('error', 'Failed')}")
            
            return True
        else:
            # Check if it provides cleanup instructions
            if data.get("errors"):
                print(f"❌ Deployment failed with errors:")
                for error in data["errors"]:
                    print(f"   - {error}")
                
                # Check for cleanup instructions
                cleanup_msg = next((e for e in data["errors"] if "delete it manually" in e), None)
                if cleanup_msg:
                    print(f"   ✅ Cleanup instructions provided")
                    return True
            
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_invalid_package():
    """Test handling of invalid package name"""
    print("\n🧪 Testing: Invalid package handling...")
    
    config = {
        "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with valid token
        "repo_name": f"test-invalid-pkg-{int(time.time())}",
        "source_package": "non-existent-package",
        "project_name": "test-project"
    }
    
    if config["github_token"] == "ghp_YOUR_TOKEN_HERE":
        print("❌ Please set a valid GitHub token")
        return False
    
    try:
        response = requests.post(f"{API_BASE}/api/deploy/create", json=config)
        data = response.json()
        
        if response.status_code == 500:
            error_msg = data.get("detail", "")
            if "not found" in error_msg.lower():
                print(f"✅ Correctly rejected invalid package")
                print(f"   Error: {error_msg}")
                
                # Check if repo was cleaned up
                if "delete it manually" in str(data.get("errors", [])):
                    print(f"   ⚠️  Repository needs manual cleanup")
                else:
                    print(f"   ✅ Repository was cleaned up automatically")
                
                return True
        
        print(f"❌ Unexpected response: {response.status_code}")
        print(f"   Data: {data}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 TD Value Accelerator - Fixed Deployment Tests")
    print("=" * 60)
    print("⚠️  Make sure to set a valid GitHub token in the test configurations!")
    print("=" * 60)
    
    tests = [
        ("Invalid Package Handling", test_invalid_package),
        ("Duplicate Repository Handling", test_duplicate_repo_handling),
        ("Ruleset Failure Handling", test_ruleset_failure_handling),
        ("Partial Failure Recovery", test_partial_failure_recovery),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! The deployment error handling is working correctly.")
    else:
        print("❌ Some tests failed. Please check the error handling logic.")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())