from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import base64
import uuid

router = APIRouter()

# Progress tracking for file copy operations
copy_progress = {}  # Dict to store progress by session ID

# GitHub repository details
GITHUB_REPO_URL = "https://api.github.com/repos/treasure-data/se-starter-pack"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/treasure-data/se-starter-pack/main"

@router.get("/starter-packs")
async def get_starter_packs():
    """Get available starter packs from GitHub repository"""
    try:
        # For demo, return predefined starter packs
        return {
            "packs": [
                {
                    "id": "qsr",
                    "name": "QSR Starter Pack",
                    "description": "Quick Service Restaurant analytics and customer journey tracking",
                    "type": "QSR",
                    "path": "qsr-starter-pack",
                    "features": [
                        "Order analytics and sales trends",
                        "Customer journey mapping", 
                        "Marketing attribution",
                        "Cohort analysis",
                        "Segmentation and targeting",
                        "Dashboard templates"
                    ],
                    "workflows": [
                        "wf02_mapping.dig",
                        "wf03_validate.dig",
                        "wf04_stage.dig",
                        "wf05_unify.dig",
                        "wf06_golden.dig",
                        "wf07_analytics.dig",
                        "wf08_create_refresh_master_segment.dig"
                    ]
                },
                {
                    "id": "retail",
                    "name": "Retail Starter Pack",
                    "description": "Comprehensive retail analytics with customer insights and product performance",
                    "type": "Retail",
                    "path": "retail-starter-pack",
                    "features": [
                        "Sales and product analytics",
                        "Customer lifetime value",
                        "Inventory optimization insights",
                        "Cross-sell recommendations",
                        "Web analytics integration",
                        "Advanced segmentation"
                    ],
                    "workflows": [
                        "wf02_mapping.dig",
                        "wf03_validate.dig", 
                        "wf04_stage.dig",
                        "wf05_unify.dig",
                        "wf06_golden.dig",
                        "wf07_analytics.dig",
                        "wf08_create_refresh_master_segment.dig"
                    ]
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch starter packs: {str(e)}")

@router.get("/pack-details/{pack_name}")
async def get_pack_details(pack_name: str):
    """Get detailed information about a specific starter pack"""
    try:
        # This would fetch from GitHub API
        # For demo, return mock detailed information
        if pack_name in ["qsr", "retail"]:
            return {
                "configuration": {
                    "src_params.yml": "# Source parameters configuration",
                    "email_ids.yml": "# Email notification configuration", 
                    "schema_map.yml": "# Schema mapping configuration"
                },
                "workflows": [
                    {"name": "wf02_mapping.dig", "description": "Data mapping workflow"},
                    {"name": "wf03_validate.dig", "description": "Data validation workflow"},
                    {"name": "wf04_stage.dig", "description": "Data staging workflow"}
                ]
            }
        else:
            raise HTTPException(status_code=404, detail="Starter pack not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pack details: {str(e)}")

@router.get("/pack-files/{pack_name}")
async def get_pack_files(pack_name: str):
    """Get all files in a starter pack"""
    try:
        # This would fetch actual files from GitHub
        # For demo, return mock file structure
        return {
            "files": [
                {
                    "name": "config/src_params.yml",
                    "type": "yml",
                    "content": "# Source parameters\ndatabase: ${TD_DATABASE}\ntable_prefix: ${TABLE_PREFIX}"
                },
                {
                    "name": "wf02_mapping.dig", 
                    "type": "dig",
                    "content": "timezone: UTC\nschedule:\n  daily>: 02:00:00"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pack files: {str(e)}")


class EnvironmentSecrets(BaseModel):
    prod: str = None
    qa: str = None
    dev: str = None

class TDCredentials(BaseModel):
    apiKey: str  # Match frontend camelCase
    region: str
    environmentTokens: dict = None  # Optional nested structure from frontend

class PackageCopyRequest(BaseModel):
    github_token: str
    organization: str = None
    repo_name: str
    package_name: str
    project_name: str
    session_id: str = None  # Optional session ID for progress tracking
    use_project_prefix: bool = True  # Whether to prefix files with project name
    create_ruleset: bool = True  # Whether to create repository ruleset (default True)
    environment_secrets: EnvironmentSecrets = EnvironmentSecrets()  # Environment secrets for TD_API_TOKEN
    td_credentials: TDCredentials = None  # TD credentials for region information

def get_github_tree(repo_owner: str, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
    """Get the file tree from GitHub repository"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/main"
    if path:
        # Get tree for specific path
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, 
                          detail=f"Failed to fetch repository tree: {response.text}")
    
    return response.json()

def get_package_files_from_github(package_name: str, github_token: str = None) -> List[Dict[str, Any]]:
    """Get all files from a package in the GitHub repository"""
    import requests
    import base64
    
    files = []
    
    # GitHub repository details
    repo_owner = "treasure-data"
    repo_name = "se-starter-pack"
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    print(f"Starting to fetch files for package: {package_name}")
    print(f"GitHub repository: {repo_owner}/{repo_name}")
    print(f"Package directory: {package_name}")
    
    # Try GitHub first (may be private and require auth)
    
    def get_directory_contents(path: str = "") -> List[Dict[str, Any]]:
        """Recursively get all files from a directory in the GitHub repo"""
        url = f"{base_url}/contents/{path}" if path else f"{base_url}/contents"
        
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        # Add authentication if token is provided
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if not response.ok:
                print(f"Failed to fetch directory {path}: {response.status_code} - {response.text}")
                return []
            
            contents = response.json()
            directory_files = []
            
            for item in contents:
                if item['type'] == 'file':
                    # Get file content
                    file_response = requests.get(item['download_url'], timeout=10)
                    if file_response.ok:
                        try:
                            # Try to decode as text
                            content = file_response.text
                            encoding = 'utf-8'
                        except UnicodeDecodeError:
                            # If not text, encode as base64
                            content = base64.b64encode(file_response.content).decode('utf-8')
                            encoding = 'base64'
                        
                        # Remove package name prefix from path
                        relative_path = item['path']
                        if relative_path.startswith(f"{package_name}/"):
                            relative_path = relative_path[len(f"{package_name}/"):]
                        
                        directory_files.append({
                            'path': relative_path,
                            'content': content,
                            'encoding': encoding,
                            'sha': item['sha']
                        })
                        print(f"Added file: {item['path']}")
                    else:
                        print(f"Failed to download file {item['path']}: {file_response.status_code}")
                
                elif item['type'] == 'dir':
                    # Recursively get files from subdirectory
                    subdirectory_files = get_directory_contents(item['path'])
                    directory_files.extend(subdirectory_files)
            
            return directory_files
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching directory {path}: {e}")
            return []
    
    # Get all files from the package directory
    files = get_directory_contents(package_name)
    
    if not files:
        print(f"No files found for package {package_name} in GitHub repository")
        return []
    
    print(f"Total files collected: {len(files)}")
    return files



def create_repository_rulesets(token: str, owner: str, repo: str) -> Dict[str, Any]:
    """Create repository rulesets with branch naming rules and main branch protection"""
    url = f"https://api.github.com/repos/{owner}/{repo}/rulesets"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json'
    }
    
    results = []
    
    # Ruleset 1: Branch naming enforcement for feature branches
    branch_naming_ruleset = {
        "name": "Enforce Branch Names",
        "target": "branch",
        "enforcement": "active",
        "conditions": {
            "ref_name": {
                "exclude": ["refs/heads/main"],
                "include": ["~ALL"]
            }
        },
        "rules": [
            {
                "type": "non_fast_forward"
            },
            {
                "type": "branch_name_pattern",
                "parameters": {
                    "operator": "regex",
                    "pattern": "^(feat|fix|hot)/[a-z0-9._-]+$",
                    "negate": False,
                    "name": "Enforce feature branch naming convention"
                }
            }
        ],
        "bypass_actors": []
    }
    
    # Ruleset 2: Main branch protection - minimal working version
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
            {
                "type": "deletion"  # Prevent deletion of main branch
            },
            {
                "type": "non_fast_forward"  # Prevent force pushes
            }
        ],
        "bypass_actors": []
    }
    
    rulesets = [
        ("Branch Naming", branch_naming_ruleset),
        ("Main Branch Protection", main_branch_ruleset)
    ]
    
    for ruleset_name, ruleset_data in rulesets:
        print(f"Creating {ruleset_name} ruleset for {owner}/{repo}...")
        print(f"Ruleset data: {ruleset_data}")
        
        try:
            response = requests.post(url, headers=headers, json=ruleset_data, timeout=15)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.ok:
                print(f"✅ Created {ruleset_name} ruleset successfully")
                results.append({
                    "name": ruleset_name,
                    "status": "success",
                    "id": response.json().get("id"),
                    "message": f"{ruleset_name} ruleset created successfully"
                })
            else:
                error_details = ""
                try:
                    error_json = response.json()
                    if 'message' in error_json:
                        error_details = f" - {error_json['message']}"
                    if 'errors' in error_json:
                        error_details += f" - Errors: {error_json['errors']}"
                except:
                    error_details = f" - {response.text[:200]}"
                
                error_msg = f"Failed to create {ruleset_name} ruleset: {response.status_code}{error_details}"
                print(f"❌ {error_msg}")
                
                # Special handling for branch naming ruleset - try fallback
                if ruleset_name == "Branch Naming" and response.status_code == 422:
                    print(f"ℹ️ Attempting fallback: Basic branch protection without naming pattern...")
                    
                    # Create fallback ruleset with just non_fast_forward
                    fallback_ruleset = {
                        "name": "Basic Branch Protection",
                        "target": "branch",
                        "enforcement": "active",
                        "conditions": {
                            "ref_name": {
                                "exclude": ["refs/heads/main"],
                                "include": ["~ALL"]
                            }
                        },
                        "rules": [
                            {
                                "type": "non_fast_forward"
                            }
                        ],
                        "bypass_actors": []
                    }
                    
                    try:
                        fallback_response = requests.post(url, headers=headers, json=fallback_ruleset, timeout=15)
                        if fallback_response.ok:
                            print(f"✅ Created fallback Basic Branch Protection ruleset")
                            results.append({
                                "name": "Basic Branch Protection (Fallback)",
                                "status": "success",
                                "id": fallback_response.json().get("id"),
                                "message": "Basic branch protection created (branch naming pattern not supported)"
                            })
                        else:
                            print(f"❌ Fallback also failed: {fallback_response.status_code}")
                            results.append({
                                "name": ruleset_name,
                                "status": "error",
                                "message": error_msg + " (fallback also failed)"
                            })
                    except Exception as fallback_error:
                        print(f"❌ Fallback error: {fallback_error}")
                        results.append({
                            "name": ruleset_name,
                            "status": "error",
                            "message": error_msg + f" (fallback error: {fallback_error})"
                        })
                else:
                    results.append({
                        "name": ruleset_name,
                        "status": "error",
                        "message": error_msg
                    })
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error creating {ruleset_name} ruleset: {str(e)}"
            print(f"❌ {error_msg}")
            results.append({
                "name": ruleset_name,
                "status": "error",
                "message": error_msg
            })
    
    return {"results": results, "total_rulesets": len(results)}

def create_github_environment_secrets(token: str, owner: str, repo: str, environment_secrets: EnvironmentSecrets) -> Dict[str, Any]:
    """Create GitHub environment secrets for TD_API_TOKEN"""
    results = []
    
    for env_name, api_token in [("prod", environment_secrets.prod), ("qa", environment_secrets.qa), ("dev", environment_secrets.dev)]:
        if not api_token:
            continue
            
        print(f"Creating {env_name} environment and setting TD_API_TOKEN secret...")
        
        try:
            # Step 1: Create environment
            env_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}"
            env_headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/json'
            }
            
            env_data = {
                "wait_timer": 0,
                "reviewers": [],
                "deployment_branch_policy": None
            }
            
            env_response = requests.put(env_url, headers=env_headers, json=env_data, timeout=10)
            if env_response.ok:
                print(f"✅ Created {env_name} environment")
            else:
                print(f"⚠️ Environment {env_name} creation warning: {env_response.status_code} - {env_response.text}")
            
            # Step 2: Get public key for secret encryption
            public_key_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}/secrets/public-key"
            public_key_response = requests.get(public_key_url, headers=env_headers, timeout=10)
            
            if not public_key_response.ok:
                raise Exception(f"Failed to get public key for {env_name}: {public_key_response.status_code}")
            
            public_key_data = public_key_response.json()
            
            # Step 3: Encrypt the secret using PyNaCl (proper encryption)
            import base64  # Import base64 first for all cases
            
            try:
                from nacl import encoding, public
                
                # Decode the public key
                public_key_bytes = base64.b64decode(public_key_data['key'])
                
                # Create a Box for encryption
                public_key_obj = public.PublicKey(public_key_bytes)
                sealed_box = public.SealedBox(public_key_obj)
                
                # Encrypt the secret
                encrypted_bytes = sealed_box.encrypt(api_token.encode('utf-8'))
                encrypted_value = base64.b64encode(encrypted_bytes).decode('utf-8')
                
            except ImportError:
                # Fallback to base64 if PyNaCl is not available
                encrypted_value = base64.b64encode(api_token.encode('utf-8')).decode('utf-8')
                print(f"⚠️ Warning: Using base64 fallback for {env_name} - install PyNaCl for proper encryption")
            
            # Step 4: Set the secret
            secret_url = f"https://api.github.com/repos/{owner}/{repo}/environments/{env_name}/secrets/TD_API_TOKEN"
            secret_data = {
                "encrypted_value": encrypted_value,
                "key_id": public_key_data['key_id']
            }
            
            secret_response = requests.put(secret_url, headers=env_headers, json=secret_data, timeout=10)
            
            if secret_response.ok:
                print(f"✅ Set TD_API_TOKEN secret for {env_name} environment")
                results.append({
                    "environment": env_name,
                    "status": "success",
                    "message": f"TD_API_TOKEN secret set for {env_name}"
                })
            else:
                error_msg = f"Failed to set secret for {env_name}: {secret_response.status_code} - {secret_response.text}"
                print(f"❌ {error_msg}")
                results.append({
                    "environment": env_name,
                    "status": "error",
                    "message": error_msg
                })
                
        except Exception as e:
            error_msg = f"Error setting up {env_name} environment: {str(e)}"
            print(f"❌ {error_msg}")
            results.append({
                "environment": env_name,
                "status": "error",
                "message": error_msg
            })
    
    return {"results": results, "total_environments": len(results)}

def create_github_repository_variables(token: str, owner: str, repo: str, project_name: str, td_region: str) -> Dict[str, Any]:
    """Create GitHub repository variables for TD workflow configuration"""
    results = []
    
    # Determine API endpoint based on region
    # Map US regions to standard US endpoint, EU to EU endpoint  
    print(f"Determining TD_WF_API_ENDPOINT for region: {td_region}")
    
    if td_region.startswith('us') or td_region in ['us01', 'aws', 'aws-east-1']:
        td_api_endpoint = 'https://api-workflow.treasuredata.com'
        print(f"Region '{td_region}' mapped to US endpoint: {td_api_endpoint}")
    elif td_region.startswith('eu') or td_region in ['eu01', 'eu-west-1']:
        td_api_endpoint = 'https://api-workflow.eu01.treasuredata.com'
        print(f"Region '{td_region}' mapped to EU endpoint: {td_api_endpoint}")
    else:
        # Default to US for any other regions
        td_api_endpoint = 'https://api-workflow.treasuredata.com'
        print(f"Region '{td_region}' not recognized, defaulting to US endpoint: {td_api_endpoint}")
    
    # Variables to create
    print(f"Setting TD_WF_PROJS to project name: {project_name}")
    
    variables = [
        {
            'name': 'TD_WF_API_ENDPOINT',
            'value': td_api_endpoint,
            'description': 'Treasure Data Workflow API endpoint'
        },
        {
            'name': 'TD_WF_PROJS',
            'value': project_name,
            'description': 'Treasure Data Workflow project name'
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json'
    }
    
    for var in variables:
        print(f"Creating repository variable: {var['name']} = {var['value']}")
        
        try:
            # Create or update repository variable
            var_url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables/{var['name']}"
            var_data = {
                'name': var['name'],
                'value': var['value']
            }
            
            # Try to update first (in case it exists)
            response = requests.patch(var_url, headers=headers, json={'value': var['value']}, timeout=10)
            
            if response.status_code == 404:
                # Variable doesn't exist, create it
                create_url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
                response = requests.post(create_url, headers=headers, json=var_data, timeout=10)
            
            if response.ok or response.status_code == 201:
                print(f"✅ Set repository variable: {var['name']} = {var['value']}")
                results.append({
                    "variable": var['name'],
                    "value": var['value'],
                    "status": "success",
                    "message": f"Repository variable {var['name']} set successfully"
                })
            else:
                error_msg = f"Failed to set variable {var['name']}: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                results.append({
                    "variable": var['name'],
                    "value": var['value'],
                    "status": "error",
                    "message": error_msg
                })
                
        except Exception as e:
            error_msg = f"Error setting variable {var['name']}: {str(e)}"
            print(f"❌ {error_msg}")
            results.append({
                "variable": var['name'],
                "value": var['value'],
                "status": "error",
                "message": error_msg
            })
    
    return {"results": results, "total_variables": len(results)}

def create_github_file(token: str, owner: str, repo: str, file_path: str, content: str, 
                      message: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """Create a file in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    print(f"Creating GitHub file: {url}")
    print(f"Owner: {owner}, Repo: {repo}, File: {file_path}")
    
    # Encode content properly
    if encoding == 'base64':
        encoded_content = content  # Already base64 encoded
    else:
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    data = {
        'message': message,
        'content': encoded_content
    }
    
    print(f"Request headers: {headers}")
    print(f"Content length: {len(encoded_content)} characters")
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=15)
        
        if not response.ok:
            error_details = ""
            try:
                error_json = response.json()
                if 'message' in error_json:
                    error_details = f" - {error_json['message']}"
                if 'errors' in error_json:
                    error_details += f" - Errors: {error_json['errors']}"
            except:
                error_details = f" - {response.text[:200]}"
            
            error_msg = f"Failed to create file {file_path}: {response.status_code}{error_details}"
            if response.status_code == 429:  # Rate limit
                error_msg += " (Rate limit exceeded)"
            elif response.status_code == 422:  # Validation error
                error_msg += " (File might already exist or validation failed)"
            
            raise HTTPException(status_code=response.status_code, detail=error_msg)
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error creating file {file_path}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/copy-package")
async def copy_package_to_github(request: PackageCopyRequest):
    """Copy package files to GitHub repository using git operations"""
    print(f"=== GIT-BASED COPY-PACKAGE API CALLED ===")
    print(f"Raw request data: {request}")
    print(f"Request dict: {request.model_dump()}")
    print(f"GitHub token: {request.github_token[:10]}..." if request.github_token else "None")
    print(f"Repo name: {request.repo_name}")
    print(f"Package name: {request.package_name}")
    print(f"Environment secrets type: {type(request.environment_secrets)}")
    print(f"Environment secrets: {request.environment_secrets}")
    print(f"TD credentials type: {type(request.td_credentials)}")
    print(f"TD credentials: {request.td_credentials}")
    print(f"========================")
    print(f"Package: {request.package_name}")
    print(f"Repository: {request.repo_name}")
    print(f"Project: {request.project_name}")
    print(f"Organization: {request.organization}")
    print(f"Use project prefix: {request.use_project_prefix}")
    print(f"Create ruleset: {request.create_ruleset}")
    print(f"Environment secrets: {[env for env in ['prod', 'qa', 'dev'] if getattr(request.environment_secrets, env)]}")
    print(f"Session ID: {request.session_id}")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    print(f"Using session ID: {session_id}")
    
    # Initialize progress tracking
    copy_progress[session_id] = {
        'status': 'starting',
        'total_files': 0,
        'files_processed': 0,
        'files_created': 0,
        'files_failed': 0,
        'current_file': '',
        'errors': [],
        'started_at': None,
        'completed_at': None
    }
    
    try:
        import subprocess
        import tempfile
        import shutil
        import os
        
        copy_progress[session_id]['status'] = 'cloning_source'
        copy_progress[session_id]['started_at'] = __import__('datetime').datetime.now().isoformat()
        
        # Validate GitHub token first
        print(f"Validating GitHub token...")
        try:
            # Add more robust headers and error handling
            headers = {
                'Authorization': f'Bearer {request.github_token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'TD-Value-Accelerator/1.0'
            }
            
            user_response = requests.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=15  # Increased timeout
            )
            
            print(f"GitHub API response status: {user_response.status_code}")
            
            if not user_response.ok:
                try:
                    error_data = user_response.json()
                    error_message = error_data.get('message', 'Unknown GitHub API error')
                    print(f"GitHub API error response: {error_data}")
                except:
                    error_message = f"HTTP {user_response.status_code}: {user_response.text[:200]}"
                
                if user_response.status_code == 401:
                    raise HTTPException(
                        status_code=401, 
                        detail=f"Invalid GitHub token. Please check your Personal Access Token. Error: {error_message}"
                    )
                elif user_response.status_code == 403:
                    raise HTTPException(
                        status_code=403,
                        detail=f"GitHub token lacks required permissions. Please ensure your token has 'repo' scope. Error: {error_message}"
                    )
                else:
                    raise HTTPException(
                        status_code=user_response.status_code,
                        detail=f"GitHub API error: {error_message}"
                    )
            
            try:
                user_info = user_response.json()
                owner = request.organization or user_info['login']
                print(f"✅ GitHub token validated for user: {user_info.get('login', 'unknown')}")
                print(f"   Account type: {user_info.get('type', 'unknown')}")
                print(f"   Owner for deployment: {owner}")
            except Exception as json_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse GitHub user response: {str(json_error)}"
                )
                
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except requests.exceptions.Timeout:
            error_msg = "GitHub API request timed out. Please check your internet connection and try again."
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=408, detail=error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to GitHub API. Please check your internet connection."
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=503, detail=error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"GitHub API connection failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during GitHub token validation: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Use local source directory and temporary directory for destination
        source_dir = "/Users/vishal.patel/Desktop/solution-work/Value Accelerator/se-starter-pack"
        if not os.path.exists(source_dir):
            raise HTTPException(status_code=500, detail=f"Source directory not found: {source_dir}")
        
        print(f"✅ Using local source directory: {source_dir}")
        
        # Create temporary directory for destination
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = f"{temp_dir}/destination"
            
            print(f"Using temp directory: {temp_dir}")
            
            # Step 1: Skip source cloning (using local directory)
            copy_progress[session_id]['status'] = 'preparing_source'
            copy_progress[session_id]['current_file'] = 'Using local source directory'
            print(f"Using local source directory...")
            
            # Step 2: Create GitHub repository first
            copy_progress[session_id]['status'] = 'creating_repository'
            copy_progress[session_id]['current_file'] = 'Creating GitHub repository'
            print(f"Creating GitHub repository: {owner}/{request.repo_name}")
            
            # Create the repository on GitHub first
            github_create_url = f"https://api.github.com/user/repos"
            if request.organization:
                github_create_url = f"https://api.github.com/orgs/{request.organization}/repos"
            
            repo_data = {
                "name": request.repo_name,
                "description": f"Value Accelerator deployment - {request.package_name}",
                "private": False,
                "auto_init": False
            }
            
            headers = {
                'Authorization': f'Bearer {request.github_token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            }
            
            repo_response = requests.post(github_create_url, headers=headers, json=repo_data, timeout=30)
            if not repo_response.ok and repo_response.status_code != 422:  # 422 = repo already exists
                error_msg = f"Failed to create repository: {repo_response.status_code} - {repo_response.text}"
                print(f"❌ {error_msg}")
                raise HTTPException(status_code=repo_response.status_code, detail=error_msg)
            elif repo_response.status_code == 422:
                print(f"ℹ️ Repository {owner}/{request.repo_name} already exists, continuing...")
            else:
                print(f"✅ Repository {owner}/{request.repo_name} created successfully")
            
            # Step 3: Initialize local repository
            copy_progress[session_id]['status'] = 'preparing_destination'
            copy_progress[session_id]['current_file'] = 'Preparing local repository'
            print(f"Initializing local repository...")
            
            subprocess.run(['git', 'init', dest_dir], check=True)
            dest_repo_url = f"https://{request.github_token}@github.com/{owner}/{request.repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', dest_repo_url], cwd=dest_dir, check=True)
            subprocess.run(['git', 'config', 'user.name', 'TD Value Accelerator'], cwd=dest_dir, check=True)
            subprocess.run(['git', 'config', 'user.email', 'noreply@treasuredata.com'], cwd=dest_dir, check=True)
            
            print(f"✅ Local repository initialized")
            
            # Step 4: Copy package files
            copy_progress[session_id]['status'] = 'copying_files'
            copy_progress[session_id]['current_file'] = f'Copying {request.package_name} files'
            print(f"Copying {request.package_name} files...")
            
            source_package_path = f"{source_dir}/{request.package_name}"
            if not os.path.exists(source_package_path):
                raise HTTPException(status_code=404, detail=f"Package {request.package_name} not found in source repository")
            
            # Always put project files in a project folder
            dest_project_path = f"{dest_dir}/{request.project_name}"
            os.makedirs(dest_project_path, exist_ok=True)
            
            # Copy all package files to project folder
            print(f"Copying from {source_package_path} to {dest_project_path}")
            for item in os.listdir(source_package_path):
                s = os.path.join(source_package_path, item)
                d = os.path.join(dest_project_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                    print(f"  📁 Copied directory: {item}")
                else:
                    shutil.copy2(s, d)
                    print(f"  📄 Copied file: {item}")
            
            print(f"✅ Copied package files to {request.project_name} folder")
            
            # Step 5: Copy GitHub Actions workflows to root
            copy_progress[session_id]['current_file'] = 'Copying GitHub Actions workflows'
            print(f"Looking for GitHub Actions workflows...")
            
            # Check for .github directory in the source repo root
            source_github_dir = f"{source_dir}/.github"
            if os.path.exists(source_github_dir):
                dest_github_dir = f"{dest_dir}/.github"
                shutil.copytree(source_github_dir, dest_github_dir, dirs_exist_ok=True)
                print(f"✅ Copied .github directory to repository root")
            else:
                print(f"ℹ️ No .github directory found in source repository")
            
            # Count files for progress tracking (exclude .git)
            file_count = 0
            for root, dirs, files in os.walk(dest_dir):
                if '.git' in root:
                    continue
                file_count += len(files)
            
            copy_progress[session_id]['total_files'] = file_count
            copy_progress[session_id]['files_created'] = file_count
            
            print(f"✅ Total files in repository: {file_count}")
            
            # Step 6: Commit and push changes
            copy_progress[session_id]['status'] = 'committing'
            copy_progress[session_id]['current_file'] = 'Committing changes'
            print(f"Committing changes...")
            
            subprocess.run(['git', 'add', '.'], cwd=dest_dir, check=True)
            
            # Check if there are changes to commit
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         cwd=dest_dir, capture_output=True, text=True, check=True)
            
            if status_result.stdout.strip():
                commit_message = f"Deploy {request.package_name} to {request.project_name}\n\n" \
                               f"- Package: {request.package_name}\n" \
                               f"- Project: {request.project_name}\n" \
                               f"- Files: {file_count}\n\n" \
                               f"🤖 Generated with TD Value Accelerator"
                subprocess.run(['git', 'commit', '-m', commit_message], cwd=dest_dir, check=True)
                
                copy_progress[session_id]['status'] = 'pushing'
                copy_progress[session_id]['current_file'] = 'Pushing to GitHub'
                print(f"Pushing to GitHub...")
                
                # Set the default branch to main
                subprocess.run(['git', 'branch', '-M', 'main'], cwd=dest_dir, check=True)
                
                push_result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                                           cwd=dest_dir, capture_output=True, text=True, timeout=120)
                
                if push_result.returncode != 0:
                    # Try 'master' branch if 'main' fails
                    push_result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                               cwd=dest_dir, capture_output=True, text=True, timeout=120)
                
                if push_result.returncode != 0:
                    error_msg = f"Failed to push to GitHub: {push_result.stderr}"
                    print(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
                
                print(f"✅ Successfully pushed changes to GitHub")
            else:
                print(f"ℹ️ No changes to commit")
        
        # Step 7: Create repository rulesets (if requested)
        if request.create_ruleset:
            copy_progress[session_id]['status'] = 'creating_rulesets'
            copy_progress[session_id]['current_file'] = 'Setting up repository rulesets'
            print(f"Creating repository rulesets...")
            
            try:
                print(f"Attempting to create rulesets for {owner}/{request.repo_name}")
                print(f"Token length: {len(request.github_token)} characters")
                rulesets_result = create_repository_rulesets(
                    token=request.github_token,
                    owner=owner,
                    repo=request.repo_name
                )
                successful_rulesets = [result['name'] for result in rulesets_result['results'] if result['status'] == 'success']
                failed_rulesets = [result['name'] for result in rulesets_result['results'] if result['status'] == 'error']
                
                if successful_rulesets:
                    print(f"✅ Repository rulesets created: {', '.join(successful_rulesets)}")
                if failed_rulesets:
                    print(f"⚠️ Failed to create rulesets: {', '.join(failed_rulesets)}")
            except Exception as ruleset_error:
                print(f"⚠️ Warning: Failed to create rulesets: {str(ruleset_error)}")
                print(f"Error type: {type(ruleset_error).__name__}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                # Don't fail the entire deployment if ruleset creation fails
        else:
            print(f"ℹ️ Skipping rulesets creation (create_ruleset=False)")
        
        # Step 8: Create environment secrets (if provided)
        env_secrets_list = [env for env in ['prod', 'qa', 'dev'] if getattr(request.environment_secrets, env)]
        if env_secrets_list:
            copy_progress[session_id]['status'] = 'creating_secrets'
            copy_progress[session_id]['current_file'] = 'Setting up environment secrets'
            print(f"Creating environment secrets for: {', '.join(env_secrets_list)}")
            
            try:
                secrets_result = create_github_environment_secrets(
                    token=request.github_token,
                    owner=owner,
                    repo=request.repo_name,
                    environment_secrets=request.environment_secrets
                )
                successful_envs = [result['environment'] for result in secrets_result['results'] if result['status'] == 'success']
                failed_envs = [result['environment'] for result in secrets_result['results'] if result['status'] == 'error']
                
                if successful_envs:
                    print(f"✅ Environment secrets created for: {', '.join(successful_envs)}")
                if failed_envs:
                    print(f"⚠️ Failed to create secrets for: {', '.join(failed_envs)}")
                    
            except Exception as secrets_error:
                print(f"⚠️ Warning: Failed to create environment secrets: {str(secrets_error)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                # Don't fail the entire deployment if secrets creation fails
        else:
            print(f"ℹ️ No environment secrets to create")
        
        # Step 9: Create repository variables
        copy_progress[session_id]['status'] = 'creating_variables'
        copy_progress[session_id]['current_file'] = 'Setting up repository variables'
        print(f"Creating repository variables for TD Workflow...")
        
        try:
            variables_result = create_github_repository_variables(
                token=request.github_token,
                owner=owner,
                repo=request.repo_name,
                project_name=request.project_name,
                td_region=request.td_credentials.region if request.td_credentials else 'us01'
            )
            successful_vars = [result['variable'] for result in variables_result['results'] if result['status'] == 'success']
            failed_vars = [result['variable'] for result in variables_result['results'] if result['status'] == 'error']
            
            if successful_vars:
                print(f"✅ Repository variables created: {', '.join(successful_vars)}")
            if failed_vars:
                print(f"⚠️ Failed to create variables: {', '.join(failed_vars)}")
                
        except Exception as variables_error:
            print(f"⚠️ Warning: Failed to create repository variables: {str(variables_error)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            # Don't fail the entire deployment if variables creation fails
        
        # Update final progress
        copy_progress[session_id]['status'] = 'completed'
        copy_progress[session_id]['completed_at'] = __import__('datetime').datetime.now().isoformat()
        
        response_data = {
            'success': True,
            'message': f'Successfully deployed {request.package_name} using git operations',
            'total_files': copy_progress[session_id]['total_files'],
            'success_count': copy_progress[session_id]['files_created'],
            'failed_count': 0,
            'session_id': session_id,
            'method': 'git_operations'
        }
        
        print(f"\n🎉 DEPLOYMENT SUCCESS RESPONSE:")
        print(f"Response Data: {response_data}")
        print(f"Session Progress: {copy_progress.get(session_id, {})}")
        
        return response_data
        
    except HTTPException as he:
        # Re-raise HTTP exceptions with their original status codes and messages
        copy_progress[session_id]['status'] = 'error'
        copy_progress[session_id]['completed_at'] = __import__('datetime').datetime.now().isoformat()
        
        print(f"\n❌ DEPLOYMENT ERROR RESPONSE (HTTPException):")
        print(f"Status Code: {he.status_code}")
        print(f"Detail: {he.detail}")
        print(f"Session Progress: {copy_progress.get(session_id, {})}")
        
        raise
    except Exception as e:
        copy_progress[session_id]['status'] = 'error'
        copy_progress[session_id]['errors'].append(f"Fatal error: {str(e)}")
        copy_progress[session_id]['completed_at'] = __import__('datetime').datetime.now().isoformat()
        
        print(f"\n❌ DEPLOYMENT ERROR RESPONSE (Exception):")
        print(f"Error: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Session Progress: {copy_progress.get(session_id, {})}")
        
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        error_response = HTTPException(status_code=500, detail=f"Unexpected deployment error: {str(e)}")
        print(f"Raising HTTPException: {error_response.status_code} - {error_response.detail}")
        
        raise error_response

@router.get("/packages")
async def list_available_packages():
    """List available starter packages"""
    try:
        # Return predefined starter packs (same as /starter-packs endpoint)
        packages = [
            {
                "id": "qsr-starter-pack",
                "name": "QSR Starter Pack",
                "description": "Quick Service Restaurant analytics and customer journey tracking",
                "type": "QSR",
                "path": "qsr-starter-pack",
                "features": [
                    "Order analytics and sales trends",
                    "Customer journey mapping", 
                    "Marketing attribution",
                    "Cohort analysis",
                    "Segmentation and targeting",
                    "Dashboard templates"
                ]
            },
            {
                "id": "retail-starter-pack",
                "name": "Retail Starter Pack",
                "description": "Comprehensive retail analytics with customer insights and product performance",
                "type": "Retail",
                "path": "retail-starter-pack",
                "features": [
                    "Sales and product analytics",
                    "Customer lifetime value",
                    "Inventory optimization insights",
                    "Cross-sell recommendations",
                    "Web analytics integration",
                    "Advanced segmentation"
                ]
            }
        ]
        
        print(f"Total packages available: {len(packages)}")
        return {'packages': packages}
        
    except Exception as e:
        print(f"Error listing packages: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing packages: {str(e)}")

@router.get("/copy-progress/{session_id}")
async def get_copy_progress(session_id: str):
    """Get the progress of a file copy operation"""
    if session_id not in copy_progress:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return copy_progress[session_id]