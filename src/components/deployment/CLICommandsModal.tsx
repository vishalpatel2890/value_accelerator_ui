import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/lib/ui-components/ui/dialog';
import { Button } from '@/lib/ui-components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/lib/ui-components/ui/tabs';
import { Terminal, Copy, Check, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/lib/ui-components/ui/alert';
import type { EnvironmentSecrets, TDCredentials } from '@/types/deployment';

interface CLICommandsModalProps {
  clientName: string;
  projectName: string;
  selectedPackage: string;
  githubOrg?: string;
  githubPAT: string;
  createRuleset: boolean;
  environmentSecrets: EnvironmentSecrets;
  tdCredentials?: TDCredentials;
}

export function CLICommandsModal({ 
  clientName, 
  projectName, 
  selectedPackage, 
  githubOrg, 
  githubPAT,
  createRuleset,
  environmentSecrets,
  tdCredentials
}: CLICommandsModalProps) {
  const [copiedStep, setCopiedStep] = useState<string | null>(null);

  const repoName = `va-${clientName.toLowerCase().replace(/[^a-z0-9-]/g, '-')}`;
  const repoOwner = githubOrg || '<YOUR_GITHUB_OWNER>';
  const fullRepoName = githubOrg ? `${githubOrg}/${repoName}` : repoName;
  
  // TD Workflow API endpoint based on region
  const getWorkflowEndpoint = (region?: string) => {
    if (!region || region === 'us01') return 'https://api-workflow.treasuredata.com';
    return `https://api-workflow.${region}.treasuredata.com`;
  };
  
  const tdApiEndpoint = getWorkflowEndpoint(tdCredentials?.region);

  const copyToClipboard = async (text: string, stepId: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedStep(stepId);
    setTimeout(() => setCopiedStep(null), 2000);
  };

  const bashCommands = `#!/bin/bash
# TD Value Accelerator Manual Deployment Script
# Generated for: ${clientName} - ${projectName}

# Set variables
REPO_NAME="${repoName}"
PROJECT_NAME="${projectName}"
PACKAGE_NAME="${selectedPackage}"
GITHUB_TOKEN="${githubPAT}"
GITHUB_OWNER="${githubOrg || '<YOUR_GITHUB_OWNER>'}"

# Step 1: Create GitHub repository
echo "Creating GitHub repository..."
gh auth login --with-token <<< "$GITHUB_TOKEN"
gh repo create "${githubOrg ? `$GITHUB_OWNER/$REPO_NAME` : `$REPO_NAME`}" --public --description "TD Value Accelerator deployment for ${clientName}"

# Step 2: Clone the source repository
echo "Cloning source repository..."
git clone https://github.com/treasure-data/se-starter-pack.git temp-source
cd temp-source

# Step 3: Copy package files
echo "Copying package files..."
mkdir -p ../$REPO_NAME/$PROJECT_NAME
cp -r $PACKAGE_NAME/* ../$REPO_NAME/$PROJECT_NAME/

# Copy GitHub Actions to repository root
if [ -d ".github" ]; then
  cp -r .github ../$REPO_NAME/
fi

# Step 4: Initialize and push to GitHub
cd ../$REPO_NAME
git init
git add .
git commit -m "Deploy $PACKAGE_NAME to $PROJECT_NAME

- Package: $PACKAGE_NAME
- Project: $PROJECT_NAME

🤖 Generated with TD Value Accelerator"

git branch -M main
git remote add origin https://github.com/$GITHUB_OWNER/$REPO_NAME.git
git push -u origin main

# Cleanup
cd ..
rm -rf temp-source

echo "✅ Deployment complete!"
echo "Repository URL: https://github.com/$GITHUB_OWNER/$REPO_NAME"

# Step 5: Set environment secrets
echo "Setting up GitHub environment secrets..."
${Object.entries(environmentSecrets).filter(([_, token]) => token).map(([env, token]) => `
# Create ${env} environment and set TD_API_TOKEN secret
gh api repos/$GITHUB_OWNER/$REPO_NAME/environments/${env} --method PUT
echo "${token}" | gh secret set TD_API_TOKEN --env ${env} --repo $GITHUB_OWNER/$REPO_NAME`).join('')}

echo "✅ Environment secrets configured!"

# Step 6: Set repository variables
echo "Setting up GitHub repository variables..."
gh api repos/$GITHUB_OWNER/$REPO_NAME/actions/variables --method POST --field name="TD_WF_API_ENDPOINT" --field value="${tdApiEndpoint}"
gh api repos/$GITHUB_OWNER/$REPO_NAME/actions/variables --method POST --field name="TD_WF_PROJS" --field value="$PROJECT_NAME"

echo "✅ Repository variables configured!"`;

  const rulesetCommands = createRuleset ? `
# Step 7: Create repository rulesets (requires GitHub CLI)
echo "Creating repository rulesets..."

# Create branch naming ruleset
cat > branch_ruleset.json << 'EOF'
{
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
        "pattern": "^(feat|fix|hot)\\\\/[a-z0-9._-]+$",
        "negate": false,
        "name": "Enforce feature branch naming convention"
      }
    }
  ],
  "bypass_actors": []
}
EOF

# Create main branch protection ruleset
cat > main_ruleset.json << 'EOF'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": [
        "~DEFAULT_BRANCH"
      ]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "automatic_copilot_code_review_enabled": false,
        "allowed_merge_methods": [
          "merge",
          "squash",
          "rebase"
        ]
      }
    }
  ],
  "bypass_actors": []
}
EOF

# Create branch naming ruleset
curl -X POST \\
  -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  -d @branch_ruleset.json \\
  "https://api.github.com/repos/$GITHUB_OWNER/$REPO_NAME/rulesets"

# Create main branch protection ruleset
curl -X POST \\
  -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  -d @main_ruleset.json \\
  "https://api.github.com/repos/$GITHUB_OWNER/$REPO_NAME/rulesets"

# Clean up
rm branch_ruleset.json main_ruleset.json` : '';

  const manualSteps = [
    {
      id: 'set-variables',
      title: 'Set Variables',
      command: `# Set variables
REPO_NAME="${repoName}"
PROJECT_NAME="${projectName}"
PACKAGE_NAME="${selectedPackage}"
GITHUB_TOKEN="${githubPAT}"${githubOrg ? `
GITHUB_OWNER="${githubOrg}"` : `
GITHUB_OWNER="<YOUR_GITHUB_OWNER>"`}`,
      note: 'Replace placeholder values with your actual credentials'
    },
    {
      id: 'create-repo',
      title: 'Create GitHub Repository',
      command: `gh repo create "${githubOrg ? `$GITHUB_OWNER/$REPO_NAME` : `$REPO_NAME`}" --public --description "TD Value Accelerator deployment for ${clientName}"`,
      note: 'Or create manually at github.com/new'
    },
    {
      id: 'clone-source',
      title: 'Clone Source Repository',
      command: `git clone https://github.com/treasure-data/se-starter-pack.git temp-source`,
    },
    {
      id: 'copy-files',
      title: 'Copy Package Files',
      command: `mkdir -p $REPO_NAME/$PROJECT_NAME
cp -r temp-source/$PACKAGE_NAME/* $REPO_NAME/$PROJECT_NAME/
cp -r temp-source/.github $REPO_NAME/`,
    },
    {
      id: 'push-to-github',
      title: 'Initialize and Push to GitHub',
      command: `cd $REPO_NAME
git init
git add .
git commit -m "Deploy $PACKAGE_NAME to $PROJECT_NAME"
git branch -M main
git remote add origin https://github.com/$GITHUB_OWNER/$REPO_NAME.git
git push -u origin main`,
    },
  ];

  // Add environment secrets setup steps
  const environmentEntries = Object.entries(environmentSecrets).filter(([_, token]) => token);
  if (environmentEntries.length > 0) {
    environmentEntries.forEach(([env, token]) => {
      manualSteps.push({
        id: `setup-${env}-env`,
        title: `Setup ${env.toUpperCase()} Environment`,
        command: `# Create ${env} environment
gh api repos/$GITHUB_OWNER/$REPO_NAME/environments/${env} --method PUT

# Set TD_API_TOKEN secret for ${env} environment
echo "${token}" | gh secret set TD_API_TOKEN --env ${env} --repo $GITHUB_OWNER/$REPO_NAME`,
        note: `Sets up TD_API_TOKEN secret for ${env} environment`
      });
    });
  }

  // Add repository variables setup step
  manualSteps.push({
    id: 'setup-variables',
    title: 'Setup Repository Variables',
    command: `# Set TD Workflow API endpoint
gh api repos/$GITHUB_OWNER/$REPO_NAME/actions/variables --method POST --field name="TD_WF_API_ENDPOINT" --field value="${tdApiEndpoint}"

# Set TD Workflow project name
gh api repos/$GITHUB_OWNER/$REPO_NAME/actions/variables --method POST --field name="TD_WF_PROJS" --field value="$PROJECT_NAME"`,
    note: 'Sets up TD Workflow configuration variables for GitHub Actions'
  });

  if (createRuleset) {
    manualSteps.push({
      id: 'create-rulesets',
      title: 'Create Repository Rulesets (Optional)',
      command: `# Create branch naming ruleset
cat > branch_ruleset.json << 'EOF'
{
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
        "pattern": "^(feat|fix|hot)\\\\/[a-z0-9._-]+$",
        "negate": false,
        "name": "Enforce feature branch naming convention"
      }
    }
  ],
  "bypass_actors": []
}
EOF

# Create main branch protection ruleset
cat > main_ruleset.json << 'EOF'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": [
        "~DEFAULT_BRANCH"
      ]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "automatic_copilot_code_review_enabled": false,
        "allowed_merge_methods": [
          "merge",
          "squash",
          "rebase"
        ]
      }
    }
  ],
  "bypass_actors": []
}
EOF

# Create both rulesets using GitHub API
curl -X POST \\
  -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  -d @branch_ruleset.json \\
  "https://api.github.com/repos/$GITHUB_OWNER/$REPO_NAME/rulesets"

curl -X POST \\
  -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  -d @main_ruleset.json \\
  "https://api.github.com/repos/$GITHUB_OWNER/$REPO_NAME/rulesets"

# Clean up
rm branch_ruleset.json main_ruleset.json`,
      note: 'Creates two rulesets: branch naming enforcement and main branch protection with required pull requests'
    });
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Terminal className="w-4 h-4" />
          CLI Commands
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Manual Deployment Commands</DialogTitle>
          <DialogDescription>
            Use these commands to manually deploy your package via command line
          </DialogDescription>
        </DialogHeader>
        
        <Alert className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Prerequisites:</strong> GitHub CLI (gh) and Git must be installed. 
            Replace placeholder values with your actual credentials.
          </AlertDescription>
        </Alert>

        <Tabs defaultValue="script" className="flex-1 flex flex-col mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="script">Full Script</TabsTrigger>
            <TabsTrigger value="steps">Step by Step</TabsTrigger>
          </TabsList>
          
          <TabsContent value="script" className="flex-1 overflow-auto">
            <div className="relative">
              <div className="absolute top-2 right-2 z-10">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(bashCommands + rulesetCommands, 'full-script')}
                >
                  {copiedStep === 'full-script' ? (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 mr-2" />
                      Copy Script
                    </>
                  )}
                </Button>
              </div>
              <div className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-auto max-h-[50vh]">
                <pre className="text-sm font-mono whitespace-pre">
                  <code>{bashCommands + rulesetCommands}</code>
                </pre>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="steps" className="flex-1 overflow-auto">
            <div className="space-y-4 pr-2">
              {manualSteps.map((step) => (
                <div key={step.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold">{step.title}</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => copyToClipboard(step.command, step.id)}
                    >
                      {copiedStep === step.id ? (
                        <>
                          <Check className="w-4 h-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded font-mono text-sm overflow-x-auto">
                    <pre className="whitespace-pre">{step.command}</pre>
                  </div>
                  {step.note && (
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">{step.note}</p>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}