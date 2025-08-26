import React, { useState } from 'react';
import { SimpleDeploymentForm } from './SimpleDeploymentForm';
import { SimpleDeploymentProgress } from './SimpleDeploymentProgress';
import { Button } from '@/lib/ui-components/ui/button';
import { ArrowLeft, CheckCircle } from 'lucide-react';

export function DeploymentPage() {
  const [currentStep, setCurrentStep] = useState<'form' | 'progress' | 'complete'>('form');
  const [deploymentRequest, setDeploymentRequest] = useState<any>(null);
  const [deploymentResult, setDeploymentResult] = useState<{ success: boolean; repoUrl?: string } | null>(null);

  const handleDeploy = (request: any) => {
    setDeploymentRequest(request);
    setCurrentStep('progress');
  };

  const handleDeploymentComplete = (success: boolean, repoUrl?: string) => {
    setDeploymentResult({ success, repoUrl });
    if (success) {
      setCurrentStep('complete');
    }
  };

  const handleRetry = () => {
    setCurrentStep('form');
    setDeploymentResult(null);
  };

  const handleNewDeployment = () => {
    setCurrentStep('form');
    setDeploymentRequest(null);
    setDeploymentResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header with back button */}
      {currentStep !== 'form' && (
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={currentStep === 'complete' ? handleNewDeployment : handleRetry}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {currentStep === 'complete' ? 'New Deployment' : 'Back'}
          </Button>
        </div>
      )}

      {/* Form Step */}
      {currentStep === 'form' && (
        <SimpleDeploymentForm onDeploy={handleDeploy} />
      )}

      {/* Progress Step */}
      {currentStep === 'progress' && deploymentRequest && (
        <SimpleDeploymentProgress
          deploymentRequest={deploymentRequest}
          onComplete={handleDeploymentComplete}
          onRetry={handleRetry}
        />
      )}

      {/* Complete Step */}
      {currentStep === 'complete' && deploymentResult?.success && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Deployment Complete!
          </h2>
          
          <p className="text-slate-600 mb-6">
            Your repository has been successfully created and configured.
          </p>

          <div className="flex gap-4 justify-center">
            {deploymentResult.repoUrl && (
              <Button
                onClick={() => window.open(deploymentResult.repoUrl, '_blank')}
              >
                View Repository
              </Button>
            )}
            
            <Button
              variant="outline"
              onClick={handleNewDeployment}
            >
              Deploy Another Package
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}