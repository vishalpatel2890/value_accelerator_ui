#!/usr/bin/env python3
"""
Test script for the simplified deployment API
"""
import requests
import json
import sys
import time

# Test configuration
API_BASE = "http://localhost:8000"
TEST_CONFIG = {
    "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with your GitHub token
    "repo_name": f"test-td-deploy-{int(time.time())}",
    "source_package": "retail-starter-pack",
    "project_name": "test-project",
    "organization": "",  # Leave empty for personal account
    "create_rulesets": True,
    "td_api_key": "test_api_key",
    "td_region": "us01",
    "env_tokens": {
        "prod": "prod_token_123",
        "qa": "qa_token_456",
        "dev": "dev_token_789"
    }
}

def test_list_packages():
    """Test listing available packages"""
    print("Testing: List available packages...")
    try:
        response = requests.get(f"{API_BASE}/api/deploy/packages")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Found {len(data['packages'])} packages:")
        for pkg in data['packages']:
            print(f"   - {pkg['id']}: {pkg['name']}")
        return True
    except Exception as e:
        print(f"❌ Failed to list packages: {e}")
        return False

def test_create_deployment():
    """Test creating a deployment"""
    print("\nTesting: Create deployment...")
    
    # Check if token is set
    if TEST_CONFIG["github_token"] == "ghp_YOUR_TOKEN_HERE":
        print("❌ Please set your GitHub token in TEST_CONFIG")
        return False
    
    try:
        print(f"Creating repository: {TEST_CONFIG['repo_name']}")
        response = requests.post(
            f"{API_BASE}/api/deploy/create",
            json=TEST_CONFIG,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print(f"✅ Deployment successful!")
            print(f"   Repository URL: {data.get('repository_url')}")
            print(f"   Message: {data.get('message')}")
            
            if data.get('warnings'):
                print(f"⚠️  Warnings:")
                for warning in data['warnings']:
                    print(f"   - {warning}")
            
            if data.get('details'):
                print("\n📋 Deployment Details:")
                details = data['details']
                
                if 'repository' in details:
                    print(f"   Repository: {details['repository']['name']} ({details['repository']['owner']})")
                
                if 'files' in details:
                    print(f"   Files: {details['files']['count']} files in {details['files']['project_folder']}/")
                
                if 'secrets' in details:
                    print(f"   Secrets: {len(details['secrets'])} created")
                
                if 'variables' in details:
                    print(f"   Variables: {len(details['variables'])} created")
                
                if 'rulesets' in details:
                    print(f"   Rulesets: {len(details['rulesets'])} created")
            
            return True
        else:
            print(f"❌ Deployment failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Message: {data.get('message', 'Unknown error')}")
            
            if data.get('errors'):
                print(f"   Errors:")
                for error in data['errors']:
                    print(f"   - {error}")
            
            # Check for specific error cases
            if response.status_code == 401:
                print("\n💡 Fix: Check your GitHub token has the correct permissions (repo, workflow, admin:repo_hook)")
            elif response.status_code == 422:
                print("\n💡 Fix: The repository name might already exist. Try a different name.")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_invalid_token():
    """Test with invalid GitHub token"""
    print("\nTesting: Invalid GitHub token handling...")
    
    invalid_config = TEST_CONFIG.copy()
    invalid_config["github_token"] = "ghp_invalid_token_12345"
    invalid_config["repo_name"] = f"test-invalid-{int(time.time())}"
    
    try:
        response = requests.post(
            f"{API_BASE}/api/deploy/create",
            json=invalid_config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly rejected invalid token")
            print(f"   Error: {data.get('detail', 'Unknown error')}")
            return True
        else:
            print(f"❌ Expected 401 but got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_missing_fields():
    """Test with missing required fields"""
    print("\nTesting: Missing required fields...")
    
    incomplete_config = {
        "github_token": "ghp_test",
        "repo_name": "test-repo"
        # Missing source_package and project_name
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/deploy/create",
            json=incomplete_config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Correctly rejected incomplete request")
            print(f"   Error: {data.get('detail', 'Unknown error')}")
            return True
        else:
            print(f"❌ Expected 400 but got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 TD Value Accelerator Deployment API Tests")
    print("=" * 50)
    
    tests = [
        ("List Packages", test_list_packages),
        ("Missing Fields", test_missing_fields),
        ("Invalid Token", test_invalid_token),
        ("Create Deployment", test_create_deployment),
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
        
        print()  # Empty line between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())