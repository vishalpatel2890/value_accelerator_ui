import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/lib/ui-components/ui/alert';
import { Button } from '@/lib/ui-components/ui/button';
import { 
  CheckCircle, 
  XCircle, 
  Loader2, 
  ExternalLink,
  AlertCircle,
  RefreshCw,
  Github,
  FolderPlus,
  Key,
  Shield,
  Settings
} from 'lucide-react';

interface DeploymentStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'warning';
}

interface DeploymentProgressProps {
  deploymentRequest: any;
  onComplete: (success: boolean, repoUrl?: string) => void;
  onRetry: () => void;
}

export function SimpleDeploymentProgress({ deploymentRequest, onComplete, onRetry }: DeploymentProgressProps) {
  const [steps, setSteps] = useState<DeploymentStep[]>([
    {
      id: 'validate',
      name: 'Validating GitHub Token',
      description: 'Checking token permissions and access',
      icon: <Github className="w-4 h-4" />,
      status: 'pending'
    },
    {
      id: 'create-repo',
      name: 'Creating Repository',
      description: `Creating ${deploymentRequest.repo_name}`,
      icon: <FolderPlus className="w-4 h-4" />,
      status: 'pending'
    },
    {
      id: 'push-files',
      name: 'Pushing Files',
      description: `Copying ${deploymentRequest.source_package} to repository`,
      icon: <FolderPlus className="w-4 h-4" />,
      status: 'pending'
    },
    {
      id: 'create-secrets',
      name: 'Creating Secrets',
      description: 'Setting up environment secrets',
      icon: <Key className="w-4 h-4" />,
      status: 'pending'
    },
    {
      id: 'create-variables',
      name: 'Creating Variables',
      description: 'Configuring repository variables',
      icon: <Settings className="w-4 h-4" />,
      status: 'pending'
    },
    {
      id: 'create-rulesets',
      name: 'Applying Branch Rules',
      description: 'Setting up branch protection',
      icon: <Shield className="w-4 h-4" />,
      status: 'pending'
    }
  ]);

  const [error, setError] = useState<string>('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [isDeploying, setIsDeploying] = useState(true);
  const [deploymentDetails, setDeploymentDetails] = useState<any>({});
  const deploymentStartedRef = useRef(false);

  const updateStepStatus = (stepId: string, status: DeploymentStep['status']) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, status } : step
    ));
  };

  const getStepIndex = (stepId: string) => {
    return steps.findIndex(step => step.id === stepId);
  };

  const runDeployment = async () => {
    // Prevent duplicate deployments
    if (deploymentStartedRef.current) {
      return;
    }

    deploymentStartedRef.current = true;
    setIsDeploying(true);
    setError('');
    setWarnings([]);

    // Start all steps as running since backend handles everything
    steps.forEach(step => updateStepStatus(step.id, 'running'));

    try {
      const response = await fetch('http://localhost:8000/api/deploy/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deploymentRequest),
      });

      const result = await response.json();

      // Handle both HTTP errors and success: false responses
      if (!response.ok || !result.success) {
        // Handle specific HTTP errors
        const errorMessage = result.detail || result.message || (result.errors && result.errors[0]) || 'Deployment failed';
        setError(errorMessage);
        
        // Mark steps as failed based on error
        if (response.status === 401) {
          updateStepStatus('validate', 'failed');
          // Other steps remain pending
          for (let i = 1; i < steps.length; i++) {
            updateStepStatus(steps[i].id, 'pending');
          }
        } else if (response.status === 422 && errorMessage.includes('already exists')) {
          updateStepStatus('validate', 'completed');
          updateStepStatus('create-repo', 'failed');
          // Other steps remain pending
          for (let i = 2; i < steps.length; i++) {
            updateStepStatus(steps[i].id, 'pending');
          }
        } else if (result.details) {
          // We have details about what was completed - update statuses accordingly
          updateStepStatus('validate', 'completed');
          updateStepStatus('create-repo', 'completed');
          updateStepStatus('push-files', 'completed');
          
          // Check which step failed based on the error message
          if (errorMessage.includes('secrets')) {
            updateStepStatus('create-secrets', 'failed');
            updateStepStatus('create-variables', 'pending');
            updateStepStatus('create-rulesets', 'pending');
          } else if (errorMessage.includes('variables')) {
            updateStepStatus('create-secrets', 'completed');
            updateStepStatus('create-variables', 'failed');
            updateStepStatus('create-rulesets', 'pending');
          } else if (errorMessage.includes('rulesets')) {
            updateStepStatus('create-secrets', 'completed');
            updateStepStatus('create-variables', 'completed');
            updateStepStatus('create-rulesets', 'failed');
          }
        } else {
          // Generic failure - mark all as failed
          steps.forEach(step => updateStepStatus(step.id, 'failed'));
        }
        
        // Set warnings if any
        if (result.warnings && result.warnings.length > 0) {
          setWarnings(result.warnings);
        }
        
        onComplete(false);
        return;
      }

      // Process successful response
      if (result.success) {
        setRepoUrl(result.repository_url);
        setDeploymentDetails(result.details || {});
        
        // Update step statuses based on what was completed
        updateStepStatus('validate', 'completed');
        updateStepStatus('create-repo', 'completed');
        updateStepStatus('push-files', 'completed');
        
        // Check secrets status
        if (deploymentRequest.env_tokens && Object.keys(deploymentRequest.env_tokens).length > 0) {
          const secretsStatus = result.details?.secrets;
          if (secretsStatus) {
            const failedSecrets = secretsStatus.filter((s: any) => s.status === 'failed');
            if (failedSecrets.length > 0) {
              updateStepStatus('create-secrets', 'warning');
              warnings.push(`${failedSecrets.length} secrets failed to create`);
            } else {
              updateStepStatus('create-secrets', 'completed');
            }
          }
        } else {
          // No secrets to create - mark as completed
          updateStepStatus('create-secrets', 'completed');
        }
        
        // Check variables status
        if (deploymentRequest.td_api_key) {
          const varsStatus = result.details?.variables;
          if (varsStatus) {
            const failedVars = varsStatus.filter((v: any) => v.status === 'failed');
            if (failedVars.length > 0) {
              updateStepStatus('create-variables', 'warning');
              warnings.push(`${failedVars.length} variables failed to create`);
            } else {
              updateStepStatus('create-variables', 'completed');
            }
          }
        } else {
          updateStepStatus('create-variables', 'completed');
        }
        
        // Check rulesets status
        if (deploymentRequest.create_rulesets) {
          const rulesetsStatus = result.details?.rulesets;
          if (rulesetsStatus) {
            const failedRulesets = rulesetsStatus.filter((r: any) => r.status === 'failed');
            if (failedRulesets.length > 0) {
              updateStepStatus('create-rulesets', 'warning');
              warnings.push(`${failedRulesets.length} rulesets failed to create`);
            } else {
              updateStepStatus('create-rulesets', 'completed');
            }
          }
        } else {
          updateStepStatus('create-rulesets', 'completed');
        }
        
        // Set any warnings from the response
        if (result.warnings && result.warnings.length > 0) {
          setWarnings(prev => [...prev, ...result.warnings]);
        }
        
        onComplete(true, result.repository_url);
      } else {
        // Deployment marked as failed by backend
        setError(result.message || 'Deployment failed');
        if (result.errors && result.errors.length > 0) {
          setError(result.errors.join('; '));
        }
        steps.forEach(step => updateStepStatus(step.id, 'failed'));
        onComplete(false);
      }
      
    } catch (error: any) {
      setError(error.message || 'Network error: Unable to connect to deployment API');
      steps.forEach(step => updateStepStatus(step.id, 'failed'));
      onComplete(false);
    } finally {
      setIsDeploying(false);
    }
  };

  useEffect(() => {
    const abortController = new AbortController();
    
    const startDeployment = async () => {
      await runDeployment();
    };

    startDeployment();
    
    return () => {
      abortController.abort();
    };
  }, []);

  const getStepIcon = (step: DeploymentStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-amber-600" />;
      default:
        return <div className="w-5 h-5 border-2 border-slate-300 rounded-full" />;
    }
  };

  const progress = steps.filter(s => s.status === 'completed' || s.status === 'warning').length / steps.length * 100;

  const getTroubleshootingSteps = (errorMsg: string) => {
    if (errorMsg.includes('Invalid GitHub token') || errorMsg.includes('401')) {
      return [
        'Go to GitHub Settings → Developer settings → Personal access tokens',
        'Generate a new token with scopes: repo, workflow, admin:repo_hook',
        'Copy the token and try again'
      ];
    }
    
    if (errorMsg.includes('already exists')) {
      return [
        'Choose a different repository name, or',
        'Delete the existing repository on GitHub first',
        'Make sure the repository name is unique'
      ];
    }
    
    if (errorMsg.includes('Organization') && errorMsg.includes('not found')) {
      return [
        'Check the organization name spelling',
        'Ensure you have access to the organization',
        'Try leaving the organization field empty to use your personal account'
      ];
    }
    
    return [
      'Check your GitHub token has the correct permissions',
      'Verify your internet connection',
      'Try with a different repository name'
    ];
  };

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Deployment Failed</AlertTitle>
          <AlertDescription className="mt-2">
            <p className="mb-4">{error}</p>
            
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
              <h4 className="font-medium text-red-900 mb-2">How to fix this:</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm text-red-800">
                {getTroubleshootingSteps(error).map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
            
            <Button 
              onClick={onRetry} 
              variant="outline" 
              size="sm" 
              className="mt-4"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings */}
      {warnings.length > 0 && !error && (
        <Alert className="border-amber-200 bg-amber-50">
          <AlertCircle className="h-4 w-4 text-amber-600" />
          <AlertTitle className="text-amber-900">Deployment completed with warnings</AlertTitle>
          <AlertDescription className="text-amber-800">
            <ul className="list-disc list-inside mt-2 space-y-1">
              {warnings.map((warning, i) => (
                <li key={i}>{warning}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Progress Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Github className="w-5 h-5" />
              Deployment Progress
            </span>
            {!isDeploying && progress === 100 && (
              <span className="text-sm font-normal text-green-600">
                Completed successfully!
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-slate-600 text-center">
              {Math.round(progress)}% Complete
            </p>
          </div>

          {/* Steps */}
          <div className="space-y-3">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-start gap-3">
                <div className="flex flex-col items-center">
                  {getStepIcon(step)}
                  {index < steps.length - 1 && (
                    <div className={`w-px h-8 mt-1 ${
                      step.status === 'completed' || step.status === 'warning' 
                        ? 'bg-green-200' 
                        : 'bg-slate-200'
                    }`} />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {step.icon}
                    <h3 className={`font-medium ${
                      step.status === 'completed' ? 'text-green-700' :
                      step.status === 'running' ? 'text-blue-700' :
                      step.status === 'failed' ? 'text-red-700' :
                      step.status === 'warning' ? 'text-amber-700' :
                      'text-slate-700'
                    }`}>
                      {step.name}
                    </h3>
                  </div>
                  <p className="text-sm text-slate-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Success Actions */}
          {repoUrl && !error && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-medium text-green-900 mb-2">
                🎉 Deployment Successful!
              </h3>
              <p className="text-sm text-green-800 mb-3">
                Your repository has been created and configured.
              </p>
              <Button
                onClick={() => window.open(repoUrl, '_blank')}
                className="bg-green-600 hover:bg-green-700"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Repository
              </Button>
            </div>
          )}

          {/* Deployment Details (for debugging) */}
          {process.env.NODE_ENV === 'development' && Object.keys(deploymentDetails).length > 0 && (
            <details className="mt-4 text-xs">
              <summary className="cursor-pointer text-slate-500">Deployment Details</summary>
              <pre className="mt-2 p-2 bg-slate-50 rounded overflow-auto">
                {JSON.stringify(deploymentDetails, null, 2)}
              </pre>
            </details>
          )}
        </CardContent>
      </Card>
    </div>
  );
}