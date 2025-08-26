# TD Value Accelerator - Simplified Deployment

## Overview

The deployment functionality has been completely rebuilt from scratch with a focus on simplicity, reliability, and user experience.

## Architecture

### Backend (`/server/routers/deployment.py`)
- **Simple REST API** - No Pydantic models, just plain dictionaries
- **Single endpoint** - `/api/deploy/create` handles the entire deployment process
- **Atomic operations** - All steps are performed in sequence with proper error handling
- **Clean error messages** - User-friendly error messages with actionable steps

### Frontend (`/src/components/deployment/`)
- **SimpleDeploymentForm.tsx** - Clean form with real-time validation
- **SimpleDeploymentProgress.tsx** - Visual progress tracking with detailed error handling
- **DeploymentPage.tsx** - Main page coordinating the deployment flow

## API Endpoint

### POST `/api/deploy/create`

Creates a new GitHub repository and deploys a starter package.

**Request Body:**
```json
{
  "github_token": "ghp_...",           // Required: GitHub Personal Access Token
  "repo_name": "my-repo",              // Required: Repository name to create
  "source_package": "retail-starter-pack", // Required: Package to deploy
  "project_name": "my-project",        // Required: Folder name in repo
  "organization": "my-org",            // Optional: GitHub org (default: personal)
  "create_rulesets": true,             // Optional: Create branch protection
  "td_api_key": "td_key",              // Optional: For creating variables
  "td_region": "us01",                 // Optional: TD region (default: us01)
  "env_tokens": {                      // Optional: Environment secrets
    "prod": "token",
    "qa": "token",
    "dev": "token"
  }
}
```

**Response:**
```json
{
  "success": true,
  "repository_url": "https://github.com/owner/repo",
  "message": "Successfully deployed retail-starter-pack to my-repo",
  "details": {
    "repository": { "url": "...", "owner": "...", "name": "..." },
    "files": { "count": 42, "project_folder": "my-project" },
    "secrets": [...],
    "variables": [...],
    "rulesets": [...]
  },
  "errors": [],
  "warnings": []
}
```

## Deployment Process

1. **Validate GitHub Token** - Checks token validity and permissions
2. **Create Repository** - Creates a new GitHub repository
3. **Copy & Push Files** - Copies starter pack files and pushes to GitHub
4. **Create Secrets** - Sets up environment secrets (if provided)
5. **Create Variables** - Sets up repository variables (if TD API key provided)
6. **Create Rulesets** - Applies branch protection rules (if requested)

## Error Handling

The system provides detailed, actionable error messages:

- **Invalid Token**: Instructions to generate a new token with correct scopes
- **Repository Exists**: Suggests choosing a different name
- **Network Errors**: Advises checking internet connection
- **Permission Errors**: Specifies which permissions are missing

## Testing

Run the test script to verify functionality:

```bash
python test_deployment.py
```

Before running tests, edit the script and add your GitHub token:
```python
TEST_CONFIG = {
    "github_token": "ghp_YOUR_TOKEN_HERE",  # Replace with your token
    ...
}
```

## Required GitHub Token Permissions

**Classic Token (Recommended):**
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows  
- `admin:repo_hook` - Full control of repository hooks

**Fine-grained Token:**
- Repository permissions:
  - Actions: Read/Write
  - Administration: Read/Write
  - Contents: Read/Write
  - Secrets: Read/Write
  - Variables: Read/Write

## UI Features

### Form Validation
- Real-time validation with clear error messages
- Token format validation
- Repository name validation (alphanumeric + hyphens/underscores)
- Visual feedback for missing environment tokens

### Progress Tracking
- Step-by-step visual progress
- Real-time status updates
- Detailed error messages with troubleshooting steps
- Warning handling for partial failures

### Error Recovery
- "Try Again" button on failures
- Clear instructions for fixing common issues
- Preserves form data on retry

## Development

### Running the Backend
```bash
cd server
python main.py
```

### Running the Frontend
```bash
npm run dev
```

### Key Files
- `/server/routers/deployment.py` - Main deployment API
- `/src/components/deployment/SimpleDeploymentForm.tsx` - Deployment form
- `/src/components/deployment/SimpleDeploymentProgress.tsx` - Progress UI
- `/src/components/deployment/DeploymentPage.tsx` - Main page component

## Troubleshooting

### Common Issues

1. **"Invalid GitHub token"**
   - Generate a new token at GitHub.com → Settings → Developer settings
   - Ensure token has required scopes: repo, workflow, admin:repo_hook

2. **"Repository already exists"**
   - Choose a different repository name
   - Or delete the existing repository first

3. **"Organization not found"**
   - Check organization name spelling
   - Ensure you have access to the organization
   - Try leaving organization field empty

4. **"Git push failed"**
   - Repository might already have content
   - Try with a completely new repository name

### Debug Mode

In development, deployment details are shown at the bottom of the progress component for debugging.

## Improvements from Previous Version

1. **Simplified Backend**: Removed complex Pydantic models and type annotations
2. **Better Error Messages**: User-friendly messages with actionable steps
3. **Cleaner UI**: Streamlined form and progress tracking
4. **Atomic Operations**: All-or-nothing deployment with proper cleanup
5. **Better Progress Tracking**: Visual feedback for each step
6. **Improved Validation**: Real-time form validation with helpful messages