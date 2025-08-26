from fastapi import APIRouter, HTTPException
import os
import subprocess
import tempfile
import shutil
import requests
import base64
from logging_config import logger
from github import Github, GithubException

router = APIRouter()

def validate_github_token(token, org=None):
    """Validate GitHub token and return (is_valid, username, error_message)"""
    try:
        g = Github(token)
        user = g.get_user()
        username = user.login
        
        # Test permissions
        if org:
            try:
                g.get_organization(org).get_repos(type="all").get_page(0)
            except GithubException as e:
                if e.status == 404:
                    return False, "", f"Organization '{org}' not found or you don't have access"
                elif e.status == 403:
                    return False, "", "Token lacks organization permissions. Add 'admin:org' scope"
                else:
                    return False, "", f"Organization access error: {e.data.get('message', str(e))}"
        else:
            user.get_repos().get_page(0)
            
        return True, username, ""
    except GithubException as e:
        if e.status == 401:
            return False, "", "Invalid GitHub token. Please check your Personal Access Token"
        elif e.status == 403:
            return False, "", "Token lacks required permissions. Ensure it has 'repo' scope"
        else:
            return False, "", f"GitHub error: {e.data.get('message', str(e))}"
    except Exception as e:
        return False, "", f"Unexpected error validating token: {str(e)}"

def create_github_repo(g, owner, repo_name, is_org):
    """Create GitHub repository. Returns (success, repo_url, error_message)"""
    try:
        repo_data = {
            "name": repo_name,
            "description": f"TD Value Accelerator deployment",
            "private": False,
            "auto_init": False
        }
        
        if is_org:
            org = g.get_organization(owner)
            repo = org.create_repo(**repo_data)
        else:
            user = g.get_user()
            repo = user.create_repo(**repo_data)
            
        return True, repo.html_url, ""
    except GithubException as e:
        if e.status == 422:
            if "already exists" in str(e.data.get('message', '')).lower():
                return False, "", f"Repository '{repo_name}' already exists. Please choose a different name"
            else:
                errors = e.data.get('errors', [])
                if errors:
                    error_msgs = [f"{err.get('field', 'field')}: {err.get('message', 'error')}" for err in errors]
                    return False, "", f"Validation failed: {'; '.join(error_msgs)}"
                return False, "", f"Repository creation failed: {e.data.get('message', 'Unknown error')}"
        else:
            return False, "", f"GitHub API error: {e.data.get('message', str(e))}"
    except Exception as e:
        return False, "", f"Unexpected error creating repository: {str(e)}"

def copy_and_push_files(token, owner, repo_name, source_package, project_name):
    """Copy files from source package and push to GitHub. Returns (success, file_count, error_message)"""
    source_base = "/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack"
    source_path = os.path.join(source_base, source_package)
    
    if not os.path.exists(source_path):
        return False, 0, f"Source package '{source_package}' not found"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=temp_dir, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'TD Deploy Bot'], cwd=temp_dir, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'deploy@treasuredata.com'], cwd=temp_dir, check=True, capture_output=True)
            
            # Copy package files to project directory
            dest_path = os.path.join(temp_dir, project_name)
            shutil.copytree(source_path, dest_path)
            
            # Copy GitHub Actions workflows if they exist
            github_actions_source = os.path.join(source_base, ".github")
            if os.path.exists(github_actions_source):
                shutil.copytree(github_actions_source, os.path.join(temp_dir, ".github"))
            
            # Count files
            file_count = sum(len(files) for _, _, files in os.walk(temp_dir) if '.git' not in _)
            
            # Create initial commit
            subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'Initial deployment of {source_package}'], cwd=temp_dir, check=True, capture_output=True)
            subprocess.run(['git', 'branch', '-M', 'main'], cwd=temp_dir, check=True, capture_output=True)
            
            # Add remote and push
            remote_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=temp_dir, check=True, capture_output=True)
            
            # Push with proper error handling
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown push error"
                if "already exists" in error_msg:
                    return False, 0, "Repository already has content. Please use an empty repository"
                return False, 0, f"Git push failed: {error_msg}"
            
            return True, file_count, ""
            
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode() if e.stderr else str(e)
        return False, 0, f"Git operation failed: {error_output}"
    except Exception as e:
        return False, 0, f"File operation failed: {str(e)}"

def create_repository_secrets(github_token, owner, repo_name, secrets):
    """Create repository secrets using GitHub token directly. Returns list of results"""
    results = []
    
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    for env_name, token_value in secrets.items():
        if not token_value:
            continue
            
        try:
            # Create environment first
            url = f"https://api.github.com/repos/{owner}/{repo_name}/environments/{env_name}"
            env_data = {"wait_timer": 0, "reviewers": [], "deployment_branch_policy": None}
            requests.put(url, headers=headers, json=env_data, timeout=10)
            
            # Get public key
            key_url = f"{url}/secrets/public-key"
            key_response = requests.get(key_url, headers=headers, timeout=10)
            
            if key_response.ok:
                key_data = key_response.json()
                
                # For simplicity, using base64 encoding (should use proper encryption in production)
                encrypted = base64.b64encode(token_value.encode()).decode()
                
                # Create secret
                secret_url = f"{url}/secrets/TD_API_TOKEN"
                secret_data = {
                    "encrypted_value": encrypted,
                    "key_id": key_data['key_id']
                }
                
                secret_response = requests.put(secret_url, headers=headers, json=secret_data, timeout=10)
                
                if secret_response.ok:
                    results.append({"name": f"{env_name}/TD_API_TOKEN", "status": "created"})
                else:
                    results.append({"name": f"{env_name}/TD_API_TOKEN", "status": "failed", "error": secret_response.text})
            else:
                results.append({"name": f"{env_name}/TD_API_TOKEN", "status": "failed", "error": "Could not get public key"})
                
        except Exception as e:
            results.append({"name": f"{env_name}/TD_API_TOKEN", "status": "failed", "error": str(e)})
        
    return results

def create_repository_variables(github_token, owner, repo_name, td_region, project_name):
    """Create repository variables using GitHub token directly. Returns list of results"""
    results = []
    
    # Determine TD endpoint based on region
    endpoint_map = {
        'us01': 'https://api-workflow.treasuredata.com',
        'eu01': 'https://api-workflow.eu01.treasuredata.com',
        'aws': 'https://api-workflow.treasuredata.com',
        'aws-east-1': 'https://api-workflow.treasuredata.com',
        'eu-west-1': 'https://api-workflow.eu01.treasuredata.com'
    }
    
    td_endpoint = endpoint_map.get(td_region, 'https://api-workflow.treasuredata.com')
    
    variables = [
        {'name': 'TD_WF_API_ENDPOINT', 'value': td_endpoint},
        {'name': 'TD_WF_PROJS', 'value': project_name}
    ]
    
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    for var in variables:
        try:
            # Try to update first
            var_url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/variables/{var['name']}"
            response = requests.patch(var_url, headers=headers, json={'value': var['value']}, timeout=10)
            
            if response.status_code == 404:
                # Create new variable
                create_url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/variables"
                response = requests.post(create_url, headers=headers, json=var, timeout=10)
            
            if response.ok or response.status_code == 201:
                results.append({"name": var['name'], "value": var['value'], "status": "created"})
            else:
                results.append({"name": var['name'], "status": "failed", "error": response.text})
                
        except Exception as e:
            results.append({"name": var['name'], "status": "failed", "error": str(e)})
        
    return results

def create_rulesets_for_repo(github_token, owner, repo_name):
    """Create repository rulesets using GitHub token directly. Returns list of results"""
    results = []
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/rulesets"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    # Main branch protection
    main_ruleset = {
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
    
    # Branch naming convention
    branch_ruleset = {
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
                    "name": "Branch naming: feat/fix/hot/chore/docs"
                }
            }
        ],
        "bypass_actors": []
    }
    
    for ruleset_name, ruleset_data in [("Main Protection", main_ruleset), ("Branch Naming", branch_ruleset)]:
        try:
            response = requests.post(url, headers=headers, json=ruleset_data, timeout=15)
            if response.ok:
                results.append({"name": ruleset_name, "status": "created"})
            else:
                # Check if it's a plan limitation error
                if response.status_code == 403 and "billing plan" in response.text.lower():
                    results.append({"name": ruleset_name, "status": "skipped", "error": "Requires GitHub Pro/Team/Enterprise plan"})
                else:
                    results.append({"name": ruleset_name, "status": "failed", "error": response.text[:100]})
        except Exception as e:
            results.append({"name": ruleset_name, "status": "failed", "error": str(e)})
            
    return results

@router.post("/create")
async def create_deployment(request: dict):
    """
    Create a new deployment by cloning a starter pack to GitHub
    
    Expected request format:
    {
        "github_token": "ghp_...",
        "repo_name": "my-repo",
        "source_package": "retail-starter-pack",
        "project_name": "my-project",
        "organization": "my-org",  # optional
        "create_rulesets": true,
        "td_api_key": "td_api_key",  # optional
        "td_region": "us01",
        "env_tokens": {  # optional
            "prod": "token",
            "qa": "token",
            "dev": "token"
        }
    }
    """
    logger.info(f"🚀 Starting deployment: {request.get('repo_name')}")
    
    warnings = []
    details = {}
    repo_created = False
    repo_url = ""
    
    try:
        # Extract request data
        github_token = request.get('github_token')
        repo_name = request.get('repo_name')
        source_package = request.get('source_package')
        project_name = request.get('project_name')
        organization = request.get('organization')
        create_rulesets = request.get('create_rulesets', True)
        td_api_key = request.get('td_api_key')
        td_region = request.get('td_region', 'us01')
        env_tokens = request.get('env_tokens', {})
        
        # Validate required fields
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub token is required")
        if not repo_name:
            raise HTTPException(status_code=400, detail="Repository name is required")
        if not source_package:
            raise HTTPException(status_code=400, detail="Source package is required")
        if not project_name:
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Step 1: Validate GitHub token
        logger.info("Step 1: Validating GitHub token...")
        is_valid, username, error_msg = validate_github_token(github_token, organization)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail=error_msg)
        
        owner = organization or username
        is_org = bool(organization)
        logger.info(f"✅ Token valid for: {owner} (org: {is_org})")
        
        # Create GitHub client
        g = Github(github_token)
        
        # Step 2: Create repository
        logger.info(f"Step 2: Creating repository: {repo_name}")
        success, repo_url, error_msg = create_github_repo(g, owner, repo_name, is_org)
        
        if not success:
            raise HTTPException(status_code=422, detail=error_msg)
        
        repo_created = True
        logger.info(f"✅ Repository created: {repo_url}")
        details["repository"] = {"url": repo_url, "owner": owner, "name": repo_name}
        
        # Step 3: Copy and push files
        logger.info("Step 3: Copying and pushing files...")
        success, file_count, error_msg = copy_and_push_files(
            github_token,
            owner,
            repo_name,
            source_package,
            project_name
        )
        
        if not success:
            # Clean up the repo if file push failed
            if repo_created:
                try:
                    repo = g.get_repo(f"{owner}/{repo_name}")
                    repo.delete()
                    logger.info(f"Cleaned up repository {repo_name} after failed file push")
                except:
                    logger.warning(f"Could not clean up repository {repo_name}. Please delete it manually.")
            raise HTTPException(status_code=500, detail=f"File push failed: {error_msg}")
        
        logger.info(f"✅ Pushed {file_count} files")
        details["files"] = {"count": file_count, "project_folder": project_name}
        
        # Step 4: Create secrets (if TD credentials provided)
        if env_tokens:
            logger.info("Step 4: Creating environment secrets...")
            try:
                secrets_results = create_repository_secrets(github_token, owner, repo_name, env_tokens)
                details["secrets"] = secrets_results
                
                failed_secrets = [s for s in secrets_results if s.get("status") == "failed"]
                if failed_secrets:
                    error_msg = f"Failed to create {len(failed_secrets)} environment secrets"
                    logger.error(f"❌ {error_msg}")
                    # Return immediately with error status
                    return {
                        "success": False,
                        "repository_url": repo_url,
                        "message": error_msg,
                        "details": details,
                        "errors": [error_msg],
                        "warnings": warnings
                    }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to create secrets: {str(e)}")
                # Return immediately with error status
                return {
                    "success": False,
                    "repository_url": repo_url,
                    "message": f"Failed to create environment secrets: {str(e)}",
                    "details": details,
                    "errors": [f"Failed to create environment secrets: {str(e)}"],
                    "warnings": warnings
                }
        
        # Step 5: Create variables (if TD API key provided)
        if td_api_key:
            logger.info("Step 5: Creating repository variables...")
            try:
                vars_results = create_repository_variables(github_token, owner, repo_name, td_region, project_name)
                details["variables"] = vars_results
                
                failed_vars = [v for v in vars_results if v.get("status") == "failed"]
                if failed_vars:
                    error_msg = f"Failed to create {len(failed_vars)} repository variables"
                    logger.error(f"❌ {error_msg}")
                    # Return immediately with error status
                    return {
                        "success": False,
                        "repository_url": repo_url,
                        "message": error_msg,
                        "details": details,
                        "errors": [error_msg],
                        "warnings": warnings
                    }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to create variables: {str(e)}")
                # Return immediately with error status
                return {
                    "success": False,
                    "repository_url": repo_url,
                    "message": f"Failed to create repository variables: {str(e)}",
                    "details": details,
                    "errors": [f"Failed to create repository variables: {str(e)}"],
                    "warnings": warnings
                }
        
        # Step 6: Create rulesets (if requested)
        if create_rulesets:
            logger.info("Step 6: Creating repository rulesets...")
            try:
                ruleset_results = create_rulesets_for_repo(github_token, owner, repo_name)
                details["rulesets"] = ruleset_results
                
                # Check for plan limitations (these are acceptable - just warnings)
                skipped_rulesets = [r for r in ruleset_results if r.get("status") == "skipped"]
                if skipped_rulesets:
                    warnings.append("Branch protection rules require GitHub Pro/Team/Enterprise plan for private repos")
                
                failed_rulesets = [r for r in ruleset_results if r.get("status") == "failed"]
                if failed_rulesets:
                    error_msg = f"Failed to create {len(failed_rulesets)} repository rulesets"
                    logger.error(f"❌ {error_msg}")
                    # Return immediately with error status
                    return {
                        "success": False,
                        "repository_url": repo_url,
                        "message": error_msg,
                        "details": details,
                        "errors": [error_msg],
                        "warnings": warnings
                    }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to create rulesets: {str(e)}")
                # Return immediately with error status
                return {
                    "success": False,
                    "repository_url": repo_url,
                    "message": f"Failed to create repository rulesets: {str(e)}",
                    "details": details,
                    "errors": [f"Failed to create repository rulesets: {str(e)}"],
                    "warnings": warnings
                }
        
        # If we reach here, deployment was successful
        logger.info(f"✅ Deployment completed successfully!")
        
        return {
            "success": True,
            "repository_url": repo_url,
            "message": f"Successfully deployed {source_package} to {repo_name}",
            "details": details,
            "errors": [],
            "warnings": warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        
        # If we created a repo but something else failed, provide cleanup instructions
        error_msg = str(e)
        if repo_created and repo_url:
            error_msg = f"Deployment failed. Repository was created at {repo_url} - please delete it manually. Error: {str(e)}"
        
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/packages")
async def list_packages():
    """List available starter packages"""
    source_base = "/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack"
    
    packages = []
    if os.path.exists(source_base):
        for item in os.listdir(source_base):
            if os.path.isdir(os.path.join(source_base, item)) and not item.startswith('.'):
                packages.append({
                    "id": item,
                    "name": item.replace('-', ' ').title()
                })
    
    return {"packages": packages}