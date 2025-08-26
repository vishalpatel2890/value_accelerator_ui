import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { Button } from '@/lib/ui-components/ui/button';
import { Input } from '@/lib/ui-components/ui/input';
import { Label } from '@/lib/ui-components/ui/label';
import { Alert, AlertDescription } from '@/lib/ui-components/ui/alert';
import { Checkbox } from '@/lib/ui-components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/lib/ui-components/ui/select';
import { useCredentials } from '@/contexts/CredentialsContext';
import { 
  Github, 
  Rocket, 
  AlertCircle, 
  CheckCircle,
  Package,
  Key,
  Building,
  FolderOpen,
  Shield,
  Eye,
  EyeOff
} from 'lucide-react';

interface DeploymentFormData {
  githubToken: string;
  repoName: string;
  sourcePackage: string;
  projectName: string;
  organization: string;
  createRulesets: boolean;
}

interface DeploymentFormProps {
  onDeploy: (data: any) => void;
}

export function SimpleDeploymentForm({ onDeploy }: DeploymentFormProps) {
  const { credentials: tdCredentials } = useCredentials();
  const [packages, setPackages] = useState<Array<{id: string, name: string}>>([]);
  const [showToken, setShowToken] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isValidating, setIsValidating] = useState(false);
  
  const [formData, setFormData] = useState<DeploymentFormData>({
    githubToken: '',
    repoName: '',
    sourcePackage: '',
    projectName: '',
    organization: '',
    createRulesets: true
  });

  // Load available packages
  useEffect(() => {
    fetch('http://localhost:8000/api/deploy/packages')
      .then(res => res.json())
      .then(data => setPackages(data.packages || []))
      .catch(err => console.error('Failed to load packages:', err));
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.githubToken) {
      newErrors.githubToken = 'GitHub token is required';
    } else if (!formData.githubToken.startsWith('ghp_') && !formData.githubToken.startsWith('github_pat_')) {
      newErrors.githubToken = 'Invalid token format. Should start with ghp_ or github_pat_';
    }
    
    if (!formData.repoName) {
      newErrors.repoName = 'Repository name is required';
    } else if (!/^[a-zA-Z0-9-_]+$/.test(formData.repoName)) {
      newErrors.repoName = 'Repository name can only contain letters, numbers, hyphens, and underscores';
    }
    
    if (!formData.sourcePackage) {
      newErrors.sourcePackage = 'Please select a starter package';
    }
    
    if (!formData.projectName) {
      newErrors.projectName = 'Project name is required';
    } else if (!/^[a-zA-Z0-9-_]+$/.test(formData.projectName)) {
      newErrors.projectName = 'Project name can only contain letters, numbers, hyphens, and underscores';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Build the deployment request
    const deploymentRequest = {
      github_token: formData.githubToken,
      repo_name: formData.repoName,
      source_package: formData.sourcePackage,
      project_name: formData.projectName,
      organization: formData.organization || undefined,
      create_rulesets: formData.createRulesets,
      td_api_key: tdCredentials?.apiKey,
      td_region: tdCredentials?.region || 'us01',
      env_tokens: {
        ...(tdCredentials?.environmentTokens?.prod && { prod: tdCredentials.environmentTokens.prod }),
        ...(tdCredentials?.environmentTokens?.qa && { qa: tdCredentials.environmentTokens.qa }),
        ...(tdCredentials?.environmentTokens?.dev && { dev: tdCredentials.environmentTokens.dev })
      }
    };
    
    onDeploy(deploymentRequest);
  };

  const updateField = (field: keyof DeploymentFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const hasEnvironmentTokens = tdCredentials?.environmentTokens && 
    (tdCredentials.environmentTokens.prod || 
     tdCredentials.environmentTokens.qa || 
     tdCredentials.environmentTokens.dev);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Github className="w-5 h-5" />
          Deploy to GitHub
        </CardTitle>
        <CardDescription>
          Create a new GitHub repository with your selected starter package
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* GitHub Token */}
          <div className="space-y-2">
            <Label htmlFor="githubToken" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              GitHub Personal Access Token
            </Label>
            <div className="relative">
              <Input
                id="githubToken"
                type={showToken ? "text" : "password"}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                value={formData.githubToken}
                onChange={(e) => updateField('githubToken', e.target.value)}
                className={errors.githubToken ? 'border-red-500' : ''}
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.githubToken && (
              <p className="text-sm text-red-500">{errors.githubToken}</p>
            )}
            <p className="text-xs text-slate-600">
              Required scopes: repo, workflow, admin:repo_hook
            </p>
          </div>

          {/* Repository Name */}
          <div className="space-y-2">
            <Label htmlFor="repoName" className="flex items-center gap-2">
              <FolderOpen className="w-4 h-4" />
              Repository Name
            </Label>
            <Input
              id="repoName"
              placeholder="my-td-project"
              value={formData.repoName}
              onChange={(e) => updateField('repoName', e.target.value)}
              className={errors.repoName ? 'border-red-500' : ''}
            />
            {errors.repoName && (
              <p className="text-sm text-red-500">{errors.repoName}</p>
            )}
          </div>

          {/* Organization (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="organization" className="flex items-center gap-2">
              <Building className="w-4 h-4" />
              GitHub Organization (Optional)
            </Label>
            <Input
              id="organization"
              placeholder="Leave empty for personal account"
              value={formData.organization}
              onChange={(e) => updateField('organization', e.target.value)}
            />
            <p className="text-xs text-slate-600">
              Create the repository in an organization instead of your personal account
            </p>
          </div>

          {/* Starter Package */}
          <div className="space-y-2">
            <Label htmlFor="sourcePackage" className="flex items-center gap-2">
              <Package className="w-4 h-4" />
              Starter Package
            </Label>
            <Select 
              value={formData.sourcePackage} 
              onValueChange={(value) => updateField('sourcePackage', value)}
            >
              <SelectTrigger className={errors.sourcePackage ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select a starter package" />
              </SelectTrigger>
              <SelectContent>
                {packages.map(pkg => (
                  <SelectItem key={pkg.id} value={pkg.id}>
                    {pkg.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.sourcePackage && (
              <p className="text-sm text-red-500">{errors.sourcePackage}</p>
            )}
          </div>

          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="projectName" className="flex items-center gap-2">
              <FolderOpen className="w-4 h-4" />
              Project Folder Name
            </Label>
            <Input
              id="projectName"
              placeholder="customer-analytics"
              value={formData.projectName}
              onChange={(e) => updateField('projectName', e.target.value)}
              className={errors.projectName ? 'border-red-500' : ''}
            />
            {errors.projectName && (
              <p className="text-sm text-red-500">{errors.projectName}</p>
            )}
            <p className="text-xs text-slate-600">
              This will be the folder name inside your repository
            </p>
          </div>

          {/* Branch Protection */}
          <div className="flex items-start space-x-3 p-4 bg-slate-50 rounded-lg">
            <Checkbox
              id="createRulesets"
              checked={formData.createRulesets}
              onCheckedChange={(checked) => updateField('createRulesets', checked as boolean)}
            />
            <div className="space-y-1">
              <Label htmlFor="createRulesets" className="flex items-center gap-2 cursor-pointer">
                <Shield className="w-4 h-4" />
                Enable branch protection rules
              </Label>
              <p className="text-xs text-slate-600">
                Enforces branch naming (feat/*, fix/*, etc.) and protects main branch
              </p>
            </div>
          </div>

          {/* TD Credentials Status */}
          {!hasEnvironmentTokens && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No environment tokens configured. Secrets won't be created.
                Configure them in Step 1 to enable automated deployments.
              </AlertDescription>
            </Alert>
          )}

          {hasEnvironmentTokens && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Environment tokens detected. Secrets will be created for:
                {tdCredentials?.environmentTokens?.prod && ' Production'}
                {tdCredentials?.environmentTokens?.qa && ' QA'}
                {tdCredentials?.environmentTokens?.dev && ' Development'}
              </AlertDescription>
            </Alert>
          )}

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full" 
            size="lg"
            disabled={isValidating}
          >
            <Rocket className="w-4 h-4 mr-2" />
            Deploy to GitHub
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}