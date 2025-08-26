# TD Value Accelerator Tests

This directory contains test scripts for the TD Value Accelerator UI.

## Test Scripts

### Deployment Tests
- **[test_deployment.py](./test_deployment.py)** - Current deployment API test suite
- **[test_deployment_fixes.py](./test_deployment_fixes.py)** - Tests for deployment fixes
- **[test_deployment_without_github.py](./test_deployment_without_github.py)** - Tests without GitHub integration

## Running Tests

### Prerequisites
1. Ensure the server is running on port 8000:
   ```bash
   cd ../server
   python main.py
   ```

2. For deployment tests, you'll need a GitHub Personal Access Token with these scopes:
   - `repo` - Full control of private repositories
   - `workflow` - Update GitHub Action workflows
   - `admin:repo_hook` - Full control of repository hooks

### Running Individual Tests

1. **Test Deployment API**:
   ```bash
   # First, edit the test file and add your GitHub token
   python test_deployment.py
   ```

2. **Test Deployment Fixes**:
   ```bash
   python test_deployment_fixes.py
   ```

3. **Test Without GitHub**:
   ```bash
   python test_deployment_without_github.py
   ```

## Test Coverage

The test scripts cover:
- API endpoint validation
- Error handling (invalid tokens, missing fields)
- Full deployment flow
- Repository creation
- Secrets and variables setup
- Branch protection rules

## Adding New Tests

When adding new test scripts:
1. Follow the naming convention: `test_*.py`
2. Include clear documentation in the script
3. Add error handling for common issues
4. Update this README with the new test description