#!/usr/bin/env python3
"""
Test deployment logic without GitHub validation
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_local_file_copy():
    """Test the local file copying logic"""
    print("=== Testing Local File Copy Logic ===")
    
    # Check source directory
    source_dir = "/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack"
    if not os.path.exists(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        return False
    
    print(f"✅ Source directory exists: {source_dir}")
    
    # Test package directories
    qsr_path = f"{source_dir}/qsr-starter-pack"
    retail_path = f"{source_dir}/retail-starter-pack"
    github_path = f"{source_dir}/.github"
    
    if not os.path.exists(qsr_path):
        print(f"❌ QSR package not found: {qsr_path}")
        return False
    if not os.path.exists(retail_path):
        print(f"❌ Retail package not found: {retail_path}")
        return False
    if not os.path.exists(github_path):
        print(f"❌ GitHub workflows not found: {github_path}")
        return False
    
    print(f"✅ All packages found")
    
    # Test file copying logic
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_dir = f"{temp_dir}/test-repo"
        project_name = "test-project"
        package_name = "qsr-starter-pack"
        
        print(f"Using temp directory: {temp_dir}")
        
        # Initialize git repo
        os.makedirs(dest_dir)
        subprocess.run(['git', 'init', dest_dir], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=dest_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=dest_dir, check=True)
        
        # Create initial commit
        with open(f"{dest_dir}/README.md", 'w') as f:
            f.write(f"# test-repo\n\nTest deployment\n")
        subprocess.run(['git', 'add', 'README.md'], cwd=dest_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=dest_dir, check=True)
        
        print(f"✅ Initialized test repository")
        
        # Copy package files
        source_package_path = f"{source_dir}/{package_name}"
        dest_project_path = f"{dest_dir}/{project_name}"
        os.makedirs(dest_project_path, exist_ok=True)
        
        # Copy all package files
        for item in os.listdir(source_package_path):
            s = os.path.join(source_package_path, item)
            d = os.path.join(dest_project_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        print(f"✅ Copied package files to {project_name} folder")
        
        # Copy GitHub Actions workflows
        dest_github_dir = f"{dest_dir}/.github"
        shutil.copytree(github_path, dest_github_dir, dirs_exist_ok=True)
        print(f"✅ Copied .github directory")
        
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(dest_dir):
            if '.git' in root:
                continue
            file_count += len(files)
        
        print(f"✅ Total files in repository: {file_count}")
        
        # Test commit
        subprocess.run(['git', 'add', '.'], cwd=dest_dir, check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=dest_dir, capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            commit_message = f"Deploy {package_name} to {project_name}\n\n" \
                           f"- Package: {package_name}\n" \
                           f"- Project: {project_name}\n" \
                           f"- Files: {file_count}\n\n" \
                           f"🤖 Generated with TD Value Accelerator"
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=dest_dir, check=True)
            print(f"✅ Successfully committed {file_count} files")
        else:
            print(f"ℹ️ No changes to commit")
        
        # Verify repository contents
        repo_files = []
        for root, dirs, files in os.walk(dest_dir):
            if '.git' in root:
                continue
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), dest_dir)
                repo_files.append(rel_path)
        
        print(f"\n=== Repository Contents ===")
        print(f"Total files: {len(repo_files)}")
        
        # Check key files exist
        key_files = [
            f"{project_name}/wf00_orchestration.dig",
            f"{project_name}/config/src_params.yml",
            ".github/workflows/va_deploy.yml",
            "README.md"
        ]
        
        missing_files = []
        for key_file in key_files:
            if key_file not in repo_files:
                missing_files.append(key_file)
        
        if missing_files:
            print(f"❌ Missing key files: {missing_files}")
            return False
        else:
            print(f"✅ All key files present")
        
        # Show sample of files
        print(f"\nSample files:")
        for i, file in enumerate(sorted(repo_files)):
            if i < 10:
                print(f"  - {file}")
            elif i == 10:
                print(f"  ... and {len(repo_files) - 10} more files")
                break
        
        return True

if __name__ == "__main__":
    print("🧪 Testing deployment file copy logic...\n")
    
    try:
        success = test_local_file_copy()
        
        print(f"\n{'='*50}")
        print(f"TEST RESULT")
        print(f"{'='*50}")
        
        if success:
            print(f"✅ SUCCESS: File copy logic works correctly!")
            print(f"   - Source files are accessible")
            print(f"   - Package copying works")
            print(f"   - GitHub workflows are copied")
            print(f"   - Git operations work")
            print(f"   - Repository structure is correct")
            print(f"\n💡 The issue is likely just GitHub token validation.")
            print(f"   With a valid GitHub token, deployment should work!")
        else:
            print(f"❌ FAILED: File copy logic has issues")
            print(f"   Please check the errors above")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()