from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
import shutil
import tempfile
import subprocess
import base64

router = APIRouter()

class EnvironmentSecrets(BaseModel):
    prod: str = None
    qa: str = None
    dev: str = None

class TDCredentials(BaseModel):
    apiKey: str
    region: str
    environmentTokens: dict = None

class SimpleDeployRequest(BaseModel):
    github_token: str
    repo_name: str
    package_name: str
    project_name: str
    organization: str = None
    session_id: str = None
    use_project_prefix: bool = False
    create_ruleset: bool = True
    environment_secrets: EnvironmentSecrets = EnvironmentSecrets()
    td_credentials: TDCredentials = None

def create_repository_rulesets(token: str, owner: str, repo: str):
    """Create repository rulesets - both main branch protection and branch naming"""
    url = f"https://api.github.com/repos/{owner}/{repo}/rulesets"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    results = []
    
    # Ruleset 1: Main branch protection
    main_branch_ruleset = {
        "name": "Main Branch Protection",
        "target": "branch",
        "enforcement": "active",
        "conditions": {
            "ref_name": {
                "exclude": [],
                "include": ["~DEFAULT_BRANCH"]
            }
        },
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"}
        ],
        "bypass_actors": []
    }
    
    # Ruleset 2: Branch naming convention  
    branch_naming_ruleset = {
        "name": "Branch Naming Convention",
        "target": "branch",
        "enforcement": "active",
        "conditions": {
            "ref_name": {
                "exclude": ["refs/heads/main", "refs/heads/master"],
                "include": ["~ALL"]
            }
        },
        "rules": [
            {
                "type": "branch_name_pattern",
                "parameters": {
                    "operator": "regex",
                    "pattern": "^(feat|fix|hot|chore|docs)/[a-z0-9._-]+$",
                    "negate": False,
                    "name": "Branch naming convention: feat/fix/hot/chore/docs followed by description"
                }
            }
        ],
        "bypass_actors": []
    }
    
    rulesets = [
        ("Main Branch Protection", main_branch_ruleset),
        ("Branch Naming Convention", branch_naming_ruleset)
    ]
    
    for ruleset_name, ruleset_data in rulesets:
        try:
            response = requests.post(url, headers=headers, json=ruleset_data, timeout=15)
            if response.ok:
                print(f"✅ Created {ruleset_name} ruleset")
                results.append({"name": ruleset_name, "status": "success"})
            else:
                print(f"⚠️ Failed to create {ruleset_name}: {response.status_code}")
                # For branch naming, try a simpler fallback
                if ruleset_name == "Branch Naming Convention" and response.status_code == 422:
                    print(f"ℹ️ Trying simpler branch protection without naming pattern...")
                    simple_ruleset = {
                        "name": "Basic Branch Protection",
                        "target": "branch", 
                        "enforcement": "active",
                        "conditions": {
                            "ref_name": {
                                "exclude": ["refs/heads/main", "refs/heads/master"],
                                "include": ["~ALL"]
                            }
                        },
                        "rules": [{"type": "non_fast_forward"}],
                        "bypass_actors": []
                    }
                    
                    fallback_response = requests.post(url, headers=headers, json=simple_ruleset, timeout=15)
                    if fallback_response.ok:
                        print(f"✅ Created Basic Branch Protection (fallback)")
                        results.append({"name": "Basic Branch Protection", "status": "success"})
                    else:
                        results.append({"name": ruleset_name, "status": "warning"})
                else:
                    results.append({"name": ruleset_name, "status": "warning"})
        except Exception as e:
            print(f"⚠️ Error creating {ruleset_name}: {e}")
            results.append({"name": ruleset_name, "status": "error"})
    
    success_count = len([r for r in results if r["status"] == "success"])
    if success_count > 0:
        successful_names = [r["name"] for r in results if r["status"] == "success"]
        return {"status": "success", "message": f"Created {success_count} rulesets: {', '.join(successful_names)}", "results": results}
    else:
        return {"status": "warning", "message": "No rulesets were created successfully", "results": results}

def create_environment_secrets(token: str, owner: str, repo: str, environment_secrets: EnvironmentSecrets):
    """Create GitHub environment secrets"""
    results = []
    
    for env_name, api_token in [("prod", environment_secrets.prod), ("qa", environment_secrets.qa), ("dev", environment_secrets.dev)]:
        if not api_token:
            continue
        
        try:
            # Create environment
            env_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}"
            env_headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            }
            
            env_data = {"wait_timer": 0, "reviewers": [], "deployment_branch_policy": None}
            env_response = requests.put(env_url, headers=env_headers, json=env_data, timeout=10)
            
            # Get public key for encryption
            public_key_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}/secrets/public-key"
            public_key_response = requests.get(public_key_url, headers=env_headers, timeout=10)
            
            if public_key_response.ok:
                public_key_data = public_key_response.json()
                
                # Simple base64 encoding (fallback method)
                encrypted_value = base64.b64encode(api_token.encode('utf-8')).decode('utf-8')
                
                # Set the secret
                secret_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}/secrets/TD_API_TOKEN"
                secret_data = {
                    "encrypted_value": encrypted_value,
                    "key_id": public_key_data['key_id']
                }
                
                secret_response = requests.put(secret_url, headers=env_headers, json=secret_data, timeout=10)
                
                if secret_response.ok:
                    print(f"✅ Created {env_name} environment secret")
                    results.append({"environment": env_name, "status": "success"})
                else:
                    print(f"⚠️ Failed to set {env_name} secret: {secret_response.status_code}")
                    results.append({"environment": env_name, "status": "warning"})
            else:
                print(f"⚠️ Failed to get public key for {env_name}")
                results.append({"environment": env_name, "status": "warning"})
                
        except Exception as e:
            print(f"⚠️ Error with {env_name} environment: {e}")
            results.append({"environment": env_name, "status": "error"})
    
    return results

def create_repository_variables(token: str, owner: str, repo: str, project_name: str, td_region: str):
    """Create GitHub repository variables"""
    results = []
    
    # Determine API endpoint based on region
    if td_region.startswith('us') or td_region in ['us01', 'aws', 'aws-east-1']:
        td_api_endpoint = 'https://api-workflow.treasuredata.com'
    elif td_region.startswith('eu') or td_region in ['eu01', 'eu-west-1']:
        td_api_endpoint = 'https://api-workflow.eu01.treasuredata.com'
    else:
        td_api_endpoint = 'https://api-workflow.treasuredata.com'
    
    variables = [
        {'name': 'TD_WF_API_ENDPOINT', 'value': td_api_endpoint},
        {'name': 'TD_WF_PROJS', 'value': project_name}
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    for var in variables:
        try:
            var_url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables/{var['name']}"
            
            # Try to update first
            response = requests.patch(var_url, headers=headers, json={'value': var['value']}, timeout=10)
            
            if response.status_code == 404:
                # Variable doesn't exist, create it
                create_url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
                response = requests.post(create_url, headers=headers, json=var, timeout=10)
            
            if response.ok or response.status_code == 201:
                print(f"✅ Set repository variable: {var['name']}")
                results.append({"variable": var['name'], "status": "success"})
            else:
                print(f"⚠️ Failed to set variable {var['name']}: {response.status_code}")
                results.append({"variable": var['name'], "status": "warning"})
                
        except Exception as e:
            print(f"⚠️ Error setting variable {var['name']}: {e}")
            results.append({"variable": var['name'], "status": "error"})
    
    return results

@router.post("/copy-package")
async def copy_package(request: SimpleDeployRequest):
    """Simple deployment that actually works"""
    print(f"\n🚀 STARTING SIMPLE DEPLOYMENT")
    print(f"   Repo: {request.repo_name}")
    print(f"   Package: {request.package_name}")
    print(f"   Project: {request.project_name}")
    
    try:
        # Step 1: Validate GitHub token
        print("Step 1: Validating GitHub token...")
        print(f"   Token length: {len(request.github_token)} characters")
        print(f"   Organization: {request.organization}")
        
        headers = {
            'Authorization': f'Bearer {request.github_token}',
            'Accept': 'application/vnd.github+json'
        }
        
        try:
            print("   Making request to GitHub API...")
            user_response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            print(f"   GitHub API responded with status: {user_response.status_code}")
            
            if not user_response.ok:
                print(f"   GitHub API error response: {user_response.text}")
                if user_response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Invalid GitHub token. Please check your Personal Access Token.")
                elif user_response.status_code == 403:
                    raise HTTPException(status_code=403, detail="GitHub token lacks required permissions. Please ensure your token has 'repo' scope.")
                else:
                    raise HTTPException(status_code=user_response.status_code, detail=f"GitHub API error: {user_response.status_code}")
            
            user_data = user_response.json()
            owner = request.organization or user_data['login']
            print(f"✅ GitHub token valid for user: {user_data['login']}")
            
        except requests.exceptions.Timeout:
            print("❌ GitHub API request timed out")
            raise HTTPException(status_code=408, detail="GitHub API request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to GitHub API")
            raise HTTPException(status_code=503, detail="Could not connect to GitHub API. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API request failed: {e}")
            raise HTTPException(status_code=500, detail=f"GitHub API request failed: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error during GitHub validation: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        # Step 2: Create GitHub repository
        print("Step 2: Creating GitHub repository...")
        if request.organization:
            repo_url = f"https://api.github.com/orgs/{request.organization}/repos"
        else:
            repo_url = "https://api.github.com/user/repos"
        
        repo_data = {
            "name": request.repo_name,
            "description": f"Deployed {request.package_name}",
            "private": False
        }
        
        repo_response = requests.post(repo_url, headers=headers, json=repo_data, timeout=10)
        if repo_response.ok:
            print(f"✅ Repository created: {owner}/{request.repo_name}")
        elif repo_response.status_code == 422:
            # Repository validation error - get detailed error info
            try:
                error_data = repo_response.json()
                print(f"GitHub API 422 response: {error_data}")
                
                # Check for specific error patterns
                message = error_data.get('message', '').lower()
                errors = error_data.get('errors', [])
                
                if "already exists" in message:
                    print(f"ℹ️ Repo exists: {owner}/{request.repo_name}")
                elif "name already exists on this account" in message:
                    print(f"ℹ️ Repo name conflict: {owner}/{request.repo_name}")
                    raise HTTPException(status_code=409, detail=f"Repository '{request.repo_name}' already exists. Please choose a different name.")
                elif errors:
                    # Handle detailed error array
                    error_messages = []
                    for error in errors:
                        if isinstance(error, dict):
                            error_msg = error.get('message', str(error))
                            field = error.get('field', '')
                            code = error.get('code', '')
                            if field and code:
                                error_messages.append(f"{field}: {error_msg} ({code})")
                            else:
                                error_messages.append(error_msg)
                        else:
                            error_messages.append(str(error))
                    
                    full_error = "; ".join(error_messages)
                    print(f"❌ Detailed validation errors: {full_error}")
                    raise HTTPException(status_code=422, detail=f"GitHub validation failed: {full_error}")
                else:
                    # Generic message
                    full_message = error_data.get('message', repo_response.text)
                    print(f"❌ Generic validation error: {full_message}")
                    
                    # Try to make it more user-friendly
                    if "creation failed" in full_message.lower():
                        user_friendly = f"Repository '{request.repo_name}' could not be created. This usually means the name is already taken or invalid. Please try a different name."
                    else:
                        user_friendly = f"GitHub repository error: {full_message}"
                    
                    raise HTTPException(status_code=422, detail=user_friendly)
                    
            except ValueError as e:
                print(f"❌ Could not parse GitHub error response: {e}")
                print(f"Raw response: {repo_response.text}")
                raise HTTPException(status_code=422, detail=f"Repository creation failed. Raw response: {repo_response.text}")
        else:
            try:
                error_data = repo_response.json()
                error_detail = error_data.get('message', repo_response.text)
            except ValueError:
                error_detail = repo_response.text
            
            print(f"❌ Failed to create repo: {error_detail}")
            
            if repo_response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid GitHub token. Please check your Personal Access Token.")
            elif repo_response.status_code == 403:
                raise HTTPException(status_code=403, detail="GitHub token lacks required permissions. Please ensure your token has 'repo' scope.")
            else:
                raise HTTPException(status_code=repo_response.status_code, detail=f"Failed to create repository: {error_detail}")
        
        # Step 3: Copy files locally and push
        print("Step 3: Copying files and pushing to GitHub...")
        source_dir = "/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack"
        source_package = f"{source_dir}/{request.package_name}"
        
        if not os.path.exists(source_package):
            raise HTTPException(status_code=404, detail=f"Package {request.package_name} not found")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=temp_dir, check=True)
            subprocess.run(['git', 'config', 'user.name', 'TD Deploy'], cwd=temp_dir, check=True)
            subprocess.run(['git', 'config', 'user.email', 'noreply@td.com'], cwd=temp_dir, check=True)
            
            # Copy package files to project folder
            project_dir = f"{temp_dir}/{request.project_name}"
            shutil.copytree(source_package, project_dir)
            
            # Copy GitHub Actions if they exist
            github_actions_source = f"{source_dir}/.github"
            if os.path.exists(github_actions_source):
                shutil.copytree(github_actions_source, f"{temp_dir}/.github")
                print("✅ Copied GitHub Actions workflows")
            
            # Count files
            file_count = 0
            for root, dirs, files in os.walk(temp_dir):
                if '.git' not in root:
                    file_count += len(files)
            
            print(f"✅ Copied {file_count} files to {request.project_name}/")
            
            # Commit and push
            subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Deploy {request.package_name}'], cwd=temp_dir, check=True)
            subprocess.run(['git', 'branch', '-M', 'main'], cwd=temp_dir, check=True)
            
            # Add remote and push
            remote_url = f"https://{request.github_token}@github.com/{owner}/{request.repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=temp_dir, check=True)
            
            push_result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'], 
                cwd=temp_dir, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if push_result.returncode != 0:
                error_details = push_result.stderr.strip() if push_result.stderr else "Unknown git push error"
                print(f"❌ Push failed: {error_details}")
                
                # Provide user-friendly error messages
                if "Repository already exists" in error_details or "rejected" in error_details:
                    if "fetch first" in error_details:
                        user_error = f"Repository '{request.repo_name}' already has content. Please use a different repository name or delete the existing repository first."
                    else:
                        user_error = f"Repository '{request.repo_name}' already exists. Please choose a different name."
                else:
                    user_error = f"Git push failed: {error_details}"
                
                raise HTTPException(status_code=409, detail=user_error)
            
            print("✅ Successfully pushed to GitHub")
        
        # Step 4: Create repository rulesets (if requested)
        ruleset_result = None
        if request.create_ruleset:
            print(f"🔒 Creating repository rulesets...")
            ruleset_result = create_repository_rulesets(request.github_token, owner, request.repo_name)
        
        # Step 5: Create environment secrets (if provided)
        secrets_results = []
        env_secrets_list = [env for env in ['prod', 'qa', 'dev'] if getattr(request.environment_secrets, env)]
        if env_secrets_list:
            print(f"🔐 Creating environment secrets for: {', '.join(env_secrets_list)}")
            secrets_results = create_environment_secrets(request.github_token, owner, request.repo_name, request.environment_secrets)
        
        # Step 6: Create repository variables
        variables_results = []
        if request.td_credentials:
            print(f"⚙️ Creating repository variables...")
            variables_results = create_repository_variables(
                request.github_token, 
                owner, 
                request.repo_name, 
                request.project_name,
                request.td_credentials.region
            )
        
        return {
            "success": True,
            "message": f"Deployed {request.package_name} to {owner}/{request.repo_name}",
            "total_files": file_count,
            "repository_url": f"https://github.com/{owner}/{request.repo_name}",
            "ruleset": ruleset_result,
            "secrets": secrets_results,
            "variables": variables_results
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is (these have proper error messages)
        raise
    except subprocess.CalledProcessError as e:
        error_msg = f"Git operation failed: {e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)}"
        print(f"❌ Git error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Deployment failed: {str(e)}"
        print(f"❌ Deployment error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/packages")
async def get_packages():
    """Return available packages"""
    return {
        "packages": [
            {"id": "retail-starter-pack", "name": "Retail Starter Pack"},
            {"id": "qsr-starter-pack", "name": "QSR Starter Pack"}
        ]
    }

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "Simple GitHub router is working", "status": "ok"}