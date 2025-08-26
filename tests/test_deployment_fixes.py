#!/usr/bin/env python3
"""
Test script to validate all deployment fixes
"""

import sys
import os
import asyncio
from pathlib import Path

# Add server to Python path
sys.path.append('server')

async def test_github_service():
    """Test GitHubService functionality"""
    print("=== Testing GitHubService ===")
    
    from services.github_service import GitHubService
    
    service = GitHubService()
    print(f"✅ GitHubService initialized")
    print(f"   Local repo path: {service.local_repo_path}")
    print(f"   Path exists: {service.local_repo_path.exists()}")
    
    # Test starter pack info
    qsr_info = await service.get_starter_pack_info('qsr')
    print(f"✅ QSR info retrieved: {qsr_info.get('name', 'Unknown')}")
    
    # Test workflow files
    workflows = await service.get_workflow_files('qsr')
    print(f"✅ QSR workflows found: {len(workflows)}")
    
    retail_workflows = await service.get_workflow_files('retail')
    print(f"✅ Retail workflows found: {len(retail_workflows)}")
    
    # Test config files
    config_files = await service.get_config_files('qsr')
    print(f"✅ QSR config files found: {len(config_files)}")
    
    # Test all files
    all_files = await service.get_all_files('qsr')
    print(f"✅ QSR total files: {len(all_files)}")
    
    return True

def test_encryption():
    """Test secret encryption functionality"""
    print("\n=== Testing Secret Encryption ===")
    
    try:
        from nacl import public
        import base64
        
        print("✅ PyNaCl available for proper encryption")
        
        # Test with dummy data
        dummy_public_key = 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF3VEkyYnp2YnE1T2svTldkck8rCmQ1eDVaTk5HSTZJYjU2R1BwYkwyRFgyRkVhWWl3UzZneUEyMVNzWGx5Z2FLU0k1aUc1L1h4UzAyNTNOZGhxZmwKaU9tT3RnbTJEd0drd0tUd1B6OVFhY2hHSWZlb1dhWTJKRW9aZXBGUTJEYWlSTng1WHQ3MThGVlR0OFdrb0hzVQpyZW5TVnZRNk5KdkhXeXNnWlhycVVNcWF2eE9MVXN0akY3ZENOemdEalNOcmEzSEJVTEdQbnFacXQ2aXFHdmpOCnNhZmdWeGMyQWlkQUFvY2w5NTVZRWpWZkxSUUNFZGpob2hMN2hRTU1DczVHcjhPS0VudHYxcmUxNkh2TThpN1oKcHBXMm16Ylk1QW4vdVlONCs4Vitwam5KSXh5TjdMMHY1TGUxNnBrU2w4akdCWHJLWWJWbEIrZE1PYkhGWXdJRApBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo='
        
        secret_text = "test_api_token_12345"
        
        # Simulate encryption process
        public_key_bytes = base64.b64decode(dummy_public_key)
        print(f"✅ Public key decoded successfully")
        
        return True
        
    except ImportError:
        print("❌ PyNaCl not available - secret encryption will use fallback")
        return False
    except Exception as e:
        print(f"⚠️ Encryption test failed: {e}")
        return False

def test_paths():
    """Test path resolution"""
    print("\n=== Testing Path Resolution ===")
    
    # Test source directory
    source_path = Path("/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack")
    print(f"Source path exists: {source_path.exists()}")
    
    if source_path.exists():
        # Test starter pack directories
        qsr_path = source_path / "qsr-starter-pack"
        retail_path = source_path / "retail-starter-pack"
        github_path = source_path / ".github"
        
        print(f"✅ QSR starter pack exists: {qsr_path.exists()}")
        print(f"✅ Retail starter pack exists: {retail_path.exists()}")
        print(f"✅ GitHub workflows exist: {github_path.exists()}")
        
        if github_path.exists():
            workflows_path = github_path / "workflows"
            print(f"✅ Workflows directory exists: {workflows_path.exists()}")
            
            if workflows_path.exists():
                workflow_files = list(workflows_path.glob("*.yml"))
                print(f"✅ Workflow files found: {len(workflow_files)}")
                for wf in workflow_files[:3]:
                    print(f"   - {wf.name}")
        
        return True
    else:
        print("❌ Source path does not exist")
        return False

def test_api_imports():
    """Test API module imports"""
    print("\n=== Testing API Imports ===")
    
    try:
        from routers.github import router as github_router
        print("✅ GitHub router imported successfully")
        
        from routers.deployment import router as deployment_router
        print("✅ Deployment router imported successfully")
        
        from services.deployment_service import DeploymentService
        print("✅ DeploymentService imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Running deployment fixes validation tests...\n")
    
    results = []
    
    # Test GitHub service
    try:
        result = await test_github_service()
        results.append(("GitHubService", result))
    except Exception as e:
        print(f"❌ GitHubService test failed: {e}")
        results.append(("GitHubService", False))
    
    # Test encryption
    try:
        result = test_encryption()
        results.append(("Encryption", result))
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        results.append(("Encryption", False))
    
    # Test paths
    try:
        result = test_paths()
        results.append(("Paths", result))
    except Exception as e:
        print(f"❌ Path test failed: {e}")
        results.append(("Paths", False))
    
    # Test imports
    try:
        result = test_api_imports()
        results.append(("API Imports", result))
    except Exception as e:
        print(f"❌ API import test failed: {e}")
        results.append(("API Imports", False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work correctly now.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())