import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { Button } from '@/lib/ui-components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/lib/ui-components/ui/alert';
import { GitHubService } from '@/services/githubService';
import type { GitHubDeploymentConfig } from '@/types/deployment';
import { 
  CheckCircle, 
  XCircle, 
  Loader2, 
  Github, 
  FolderPlus, 
  Key, 
  Settings,
  ShieldCheck, 
  GitBranch,
  ExternalLink 
} from 'lucide-react';

// Troubleshooting guide component
const TroubleshootingGuide = ({ errorMessage }: { errorMessage: string }) => {
  const getTroubleshootingSteps = (error: string) => {
    if (error.includes('Invalid GitHub token') || error.includes('Authentication Failed')) {
      return [
        'Go to GitHub.com → Settings → Developer settings → Personal access tokens',
        'Click "Generate new token (classic)"',
        'Select these scopes: repo, workflow, admin:repo_hook',
        'Copy the new token and paste it in the deployment form'
      ];
    }
    
    if (error.includes('Insufficient Permissions')) {
      return [
        'Edit your existing GitHub token',
        'Ensure these scopes are checked: repo, workflow, admin:repo_hook',
        'If you can\'t edit it, generate a new token with the correct scopes'
      ];
    }
    
    if (error.includes('Repository Exists')) {
      return [
        'Go to the existing repository on GitHub',
        'Delete it if it\'s no longer needed, or',
        'Choose a different client name for your deployment'
      ];
    }
    
    if (error.includes('Network Error') || error.includes('Request Timeout')) {
      return [
        'Check your internet connection',
        'Try again in a few moments',
        'If the problem persists, GitHub API might be experiencing issues'
      ];
    }
    
    return [
      'Check your GitHub token permissions',
      'Ensure your internet connection is stable',
      'Try again with a different repository name',
      'Contact support if the issue persists'
    ];
  };

  const steps = getTroubleshootingSteps(errorMessage);
  
  return (
    <div className="mt-4 p-4 bg-slate-50 rounded-lg border">
      <h4 className="font-medium text-slate-900 mb-2">💡 How to fix this:</h4>
      <ol className="list-decimal list-inside space-y-1 text-sm text-slate-700">
        {steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>
    </div>
  );
};

// Utility function to format error messages for better user experience
const formatErrorMessage = (errorMessage: string): string => {
  if (!errorMessage) return 'An unknown error occurred';
  
  // Extract the actual error message from common error patterns
  if (errorMessage.includes('Invalid GitHub token')) {
    return '❌ Invalid GitHub Token: Please check your Personal Access Token has the correct permissions (repo, workflow, admin:repo_hook)';
  }
  
  if (errorMessage.includes('Bad credentials')) {
    return '❌ Authentication Failed: Your GitHub token is invalid or expired. Please generate a new Personal Access Token';
  }
  
  if (errorMessage.includes('GitHub token lacks required permissions')) {
    return '❌ Insufficient Permissions: Your GitHub token needs additional scopes. Please ensure it has repo, workflow, and admin:repo_hook permissions';
  }
  
  if (errorMessage.includes('GitHub API connection failed')) {
    return '❌ Network Error: Unable to connect to GitHub. Please check your internet connection and try again';
  }
  
  if (errorMessage.includes('GitHub API request timed out')) {
    return '❌ Request Timeout: GitHub API is slow or unreachable. Please try again in a few moments';
  }
  
  if (errorMessage.includes('Repository') && errorMessage.includes('already exists')) {
    return '❌ Repository Exists: A repository with this name already exists. Please choose a different client name or delete the existing repository';
  }
  
  if (errorMessage.includes('Failed to copy package files:')) {
    // Remove the generic prefix and show the actual error
    return errorMessage.replace('Failed to copy package files: ', '❌ Deployment Error: ');
  }
  
  // If no specific pattern matches, show the error as-is but with an icon
  return `❌ Error: ${errorMessage}`;
};

interface DeploymentStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  error?: string;
}

interface GitHubDeploymentProgressProps {
  config: GitHubDeploymentConfig;
  onComplete: (success: boolean, repoUrl?: string) => void;
}

export function GitHubDeploymentProgress({ config, onComplete }: GitHubDeploymentProgressProps) {
  const [steps, setSteps] = useState<DeploymentStep[]>([
    {
      id: 'create-repo',
      title: 'Create Repository',
      description: `Creating va-${config.clientName} repository`,
      status: 'pending',
    },
    {
      id: 'copy-files',
      title: 'Copy Package Files',
      description: `Copying ${config.selectedPackage} to ${config.projectName}`,
      status: 'pending',
    },
    {
      id: 'setup-secrets',
      title: 'Configure Secrets',
      description: 'Setting up TD API tokens for prod, qa, dev environments',
      status: 'pending',
    },
    {
      id: 'setup-variables',
      title: 'Configure Variables',
      description: 'Setting up TD workflow configuration variables',
      status: 'pending',
    },
    {
      id: 'create-ruleset',
      title: 'Apply Branch Rules',
      description: 'Setting up branch name enforcement rules',
      status: 'pending',
    },
    {
      id: 'create-branch',
      title: 'Create Development Branch',
      description: 'Creating feat/dev branch',
      status: 'pending',
    },
  ]);

  const [repoUrl, setRepoUrl] = useState<string>('');
  const [deploymentStarted, setDeploymentStarted] = useState(false);
  const [currentError, setCurrentError] = useState<string>('');

  const updateStepStatus = (stepId: string, status: DeploymentStep['status'], error?: string) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, error }
        : step
    ));
    
    // If this is an error, set it as the current error to display prominently
    if (status === 'failed' && error) {
      setCurrentError(error);
    }
  };

  const runDeployment = async () => {
    // Clear any previous errors
    setCurrentError('');
    
    const githubService = new GitHubService(config.githubCredentials);
    let createdRepoUrl = '';

    try {
      // All steps handled by backend - start them all as running
      updateStepStatus('create-repo', 'running');
      updateStepStatus('copy-files', 'running');
      updateStepStatus('setup-secrets', 'running');
      updateStepStatus('setup-variables', 'running');
      updateStepStatus('create-ruleset', 'running');
      
      console.log('🚀 Starting full deployment:', {
        clientName: config.clientName,
        repository: `va-${config.clientName}`,
        package: config.selectedPackage,
        project: config.projectName,
        createRuleset: config.createRuleset,
        environmentSecrets: config.environmentSecrets,
        tdCredentials: config.tdCredentials
      });
      
      // Generate a session ID for progress tracking
      const sessionId = Date.now().toString();
      
      // Single call to backend handles everything: repo creation, file copy, secrets, variables, rulesets
      const deploymentResult = await githubService.copyPackageFiles(
        `va-${config.clientName}`, 
        config.selectedPackage, 
        config.projectName,
        sessionId,
        false,  // Don't use project prefix - place files at repository root
        config.createRuleset !== false,  // Default to true if not specified
        config.environmentSecrets,  // Pass environment secrets
        config.tdCredentials  // Pass TD credentials
      );
      
      console.log('📋 Full deployment result:', deploymentResult);
      
      if (deploymentResult.success) {
        console.log('✅ Full deployment completed successfully');
        
        // All backend operations completed successfully
        updateStepStatus('create-repo', 'completed');
        updateStepStatus('copy-files', 'completed');
        updateStepStatus('setup-secrets', 'completed');
        updateStepStatus('setup-variables', 'completed');
        updateStepStatus('create-ruleset', 'completed');
        
        // Set repository URL from deployment result
        if (deploymentResult.repository_url) {
          createdRepoUrl = deploymentResult.repository_url;
          setRepoUrl(createdRepoUrl);
        }
        
        // Log specific deployment details
        if (deploymentResult.ruleset) {
          console.log('🔒 Ruleset creation result:', deploymentResult.ruleset);
        }
        if (deploymentResult.secrets) {
          console.log('🔐 Secrets creation result:', deploymentResult.secrets);
        }
        if (deploymentResult.variables) {
          console.log('⚙️ Variables creation result:', deploymentResult.variables);
        }
        
        // Step 6: Create Development Branch (still handled separately)
        updateStepStatus('create-branch', 'running');
        try {
          console.log('🌿 Creating development branch: feat/dev');
          await githubService.createBranch(`va-${config.clientName}`, 'feat/dev');
          console.log('✅ Development branch created successfully');
          updateStepStatus('create-branch', 'completed');
          onComplete(true, createdRepoUrl);
        } catch (branchError: any) {
          console.error('❌ Branch creation failed:', branchError);
          const errorMessage = formatErrorMessage(branchError.message);
          updateStepStatus('create-branch', 'failed', errorMessage);
          // Still consider deployment successful even if branch creation fails
          onComplete(true, createdRepoUrl);
        }
        
      } else {
        console.error('❌ Deployment failed:', deploymentResult);
        
        // Mark all steps as failed if the deployment failed
        updateStepStatus('create-repo', 'failed', 'Backend deployment failed');
        updateStepStatus('copy-files', 'failed', 'Backend deployment failed');
        updateStepStatus('setup-secrets', 'failed', 'Backend deployment failed');
        updateStepStatus('setup-variables', 'failed', 'Backend deployment failed');
        updateStepStatus('create-ruleset', 'failed', 'Backend deployment failed');
        
        onComplete(false);
        return;
      }
      
    } catch (error: any) {
      console.error('❌ Full deployment failed:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });
      
      const errorMessage = formatErrorMessage(error.message);
      
      // Mark all steps as failed
      updateStepStatus('create-repo', 'failed', errorMessage);
      updateStepStatus('copy-files', 'failed', errorMessage);
      updateStepStatus('setup-secrets', 'failed', errorMessage);
      updateStepStatus('setup-variables', 'failed', errorMessage);
      updateStepStatus('create-ruleset', 'failed', errorMessage);
      
      onComplete(false);
    }
  };

  useEffect(() => {
    if (!deploymentStarted) {
      setDeploymentStarted(true);
      runDeployment();
    }
  }, []); // Empty dependency array to run only once

  const getStepIcon = (step: DeploymentStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <div className="w-5 h-5 border-2 border-slate-300 rounded-full" />;
    }
  };

  const getStepIconForId = (stepId: string) => {
    const iconMap = {
      'create-repo': <Github className="w-4 h-4" />,
      'copy-files': <FolderPlus className="w-4 h-4" />,
      'setup-secrets': <Key className="w-4 h-4" />,
      'setup-variables': <Settings className="w-4 h-4" />,
      'create-ruleset': <ShieldCheck className="w-4 h-4" />,
      'create-branch': <GitBranch className="w-4 h-4" />,
    };
    return iconMap[stepId as keyof typeof iconMap] || null;
  };

  return (
    <div className="space-y-6">
      {/* Error Alert - Show if deployment has failed */}
      {currentError && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Deployment Failed</AlertTitle>
          <AlertDescription className="mt-2">
            {currentError}
            <TroubleshootingGuide errorMessage={currentError} />
          </AlertDescription>
          <div className="mt-3">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                // Reset all steps to pending state
                setSteps(prev => prev.map(step => ({ ...step, status: 'pending', error: undefined })));
                setCurrentError('');
                setDeploymentStarted(false);
                // Restart deployment
                runDeployment();
              }}
              className="text-sm"
            >
              Try Again
            </Button>
          </div>
        </Alert>
      )}
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Github className="w-5 h-5" />
            Deploying to GitHub
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-start gap-4">
                <div className="flex flex-col items-center">
                  {getStepIcon(step)}
                  {index < steps.length - 1 && (
                    <div className={`w-px h-8 mt-2 ${
                      step.status === 'completed' ? 'bg-green-200' : 'bg-slate-200'
                    }`} />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {getStepIconForId(step.id)}
                    <h3 className={`font-medium ${
                      step.status === 'completed' ? 'text-green-700' :
                      step.status === 'running' ? 'text-blue-700' :
                      step.status === 'failed' ? 'text-red-700' :
                      'text-slate-700'
                    }`}>
                      {step.title}
                    </h3>
                  </div>
                  
                  <p className="text-sm text-slate-600 mb-2">
                    {step.description}
                  </p>
                  
                  {step.status === 'failed' && step.error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-sm text-red-700">
                        <strong>Error:</strong> {step.error}
                      </p>
                    </div>
                  )}
                  
                  {step.status === 'completed' && step.id === 'create-repo' && repoUrl && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-sm text-green-700 mb-2">
                        Repository created successfully!
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(repoUrl, '_blank')}
                        className="text-green-700 border-green-300 hover:bg-green-100"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        View Repository
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Repository Summary */}
      {repoUrl && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-800">Deployment Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-blue-700">Repository:</span>
                <span className="font-mono text-blue-900">va-{config.clientName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Project Folder:</span>
                <span className="font-mono text-blue-900">{config.projectName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Package:</span>
                <span className="font-mono text-blue-900">{config.selectedPackage}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Environments:</span>
                <span className="font-mono text-blue-900">prod, qa, dev</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Development Branch:</span>
                <span className="font-mono text-blue-900">feat/dev</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}