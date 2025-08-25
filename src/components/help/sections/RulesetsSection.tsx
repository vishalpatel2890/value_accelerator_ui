import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { Button } from '@/lib/ui-components/ui/button';
import { Shield, Copy, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { TableOfContents } from '../shared/TableOfContents';

export function RulesetsSection() {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const tocItems = [
    { id: 'branch-naming-enforcement', title: 'Branch Naming Enforcement' },
    { id: 'main-branch-protection', title: 'Main Branch Protection' },
    { id: 'workflow-integration', title: 'CI/CD Workflow Integration' },
    { id: 'repository-protection', title: 'Additional Protection Rules' }
  ];

  return (
    <div className="space-y-6">
      <TableOfContents items={tocItems} />
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-600 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Repository Rulesets</h1>
            <p className="text-slate-600 mt-1">
              Automated branch protection for TD Value Accelerator workflows
            </p>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle id="branch-naming-enforcement">Branch Naming Enforcement</CardTitle>
          <CardDescription>
            Ensures proper branch naming for CI/CD workflow triggers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-blue-800">Intelligent Branch Naming Enforcement</h3>
                <p className="text-blue-700 text-sm mt-1">
                  The TD Value Accelerator automatically attempts to create branch naming pattern enforcement. 
                  If your repository doesn't support advanced patterns (free plans), it creates basic branch protection instead.
                </p>
              </div>
            </div>
          </div>
          
          <p className="text-slate-700">
            The TD Value Accelerator enforces specific branch naming patterns to ensure CI/CD workflows 
            trigger correctly. The system uses intelligent fallback to provide protection based on your repository's capabilities.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-800 mb-3">Required Branch Pattern</h3>
            <div className="bg-white p-3 rounded border border-blue-200">
              <code className="text-sm font-mono text-blue-700">^(feat|fix|hot)\/[a-z0-9._-]+$</code>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-blue-600">Regex pattern for branch names</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard('^(feat|fix|hot)\\/[a-z0-9._-]+$')}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-green-200 bg-green-50 rounded-lg p-3">
              <h4 className="font-medium text-green-800 mb-2">feat/* branches</h4>
              <ul className="text-xs text-green-700 space-y-1">
                <li>• <code>feat/user-auth</code></li>
                <li>• <code>feat/new-dashboard</code></li>
                <li>• <code>feat/api-integration</code></li>
              </ul>
            </div>

            <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-3">
              <h4 className="font-medium text-yellow-800 mb-2">fix/* branches</h4>
              <ul className="text-xs text-yellow-700 space-y-1">
                <li>• <code>fix/login-bug</code></li>
                <li>• <code>fix/query-error</code></li>
                <li>• <code>fix/data-validation</code></li>
              </ul>
            </div>

            <div className="border border-red-200 bg-red-50 rounded-lg p-3">
              <h4 className="font-medium text-red-800 mb-2">hot/* branches</h4>
              <ul className="text-xs text-red-700 space-y-1">
                <li>• <code>hot/critical-fix</code></li>
                <li>• <code>hot/security-patch</code></li>
                <li>• <code>hot/prod-issue</code></li>
              </ul>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="font-medium text-slate-800">Repository Capability Levels</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-green-200 bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-800 mb-2">Advanced Protection</h4>
                <p className="text-sm text-green-700 mb-2">GitHub Pro/Team/Enterprise plans</p>
                <ul className="text-xs text-green-600 space-y-1">
                  <li>• ✅ Branch naming pattern enforcement</li>
                  <li>• ✅ Regex pattern matching</li>
                  <li>• ✅ Force push protection</li>
                  <li>• ✅ Full workflow integration</li>
                </ul>
              </div>
              
              <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">Basic Protection</h4>
                <p className="text-sm text-blue-700 mb-2">GitHub Free plan (fallback)</p>
                <ul className="text-xs text-blue-600 space-y-1">
                  <li>• ✅ Force push protection</li>
                  <li>• ✅ Main branch protection</li>
                  <li>• ⚠️ Manual branch naming compliance required</li>
                  <li>• ✅ Workflow integration still works</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle id="main-branch-protection">Main Branch Protection</CardTitle>
          <CardDescription>
            Comprehensive protection for your main/default branch
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-700">
            The TD Value Accelerator automatically creates a dedicated ruleset to protect your main branch from 
            accidental changes and enforces proper code review processes.
          </p>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-medium text-red-800 mb-3">Deletion Protection</h3>
            <div className="bg-white p-3 rounded border border-red-200">
              <p className="text-sm text-red-700 mb-2">
                <strong>Prevents:</strong> Accidental deletion of the main branch
              </p>
              <ul className="text-xs text-red-600 space-y-1">
                <li>• Protects against <code className="bg-red-100 px-1 rounded">git push origin --delete main</code></li>
                <li>• Prevents repository history loss</li>
                <li>• Maintains deployment stability</li>
                <li>• Preserves production branch integrity</li>
              </ul>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-800 mb-3">Pull Request Requirements</h3>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded border border-blue-200">
                <h4 className="font-medium text-blue-700 mb-2">Review Requirements</h4>
                <ul className="text-sm text-blue-600 space-y-1">
                  <li>• <strong>Required approvals:</strong> 1 approving review minimum</li>
                  <li>• <strong>Code owner reviews:</strong> Required when CODEOWNERS file exists</li>
                  <li>• <strong>Stale reviews:</strong> Not dismissed on new pushes (preserves approval history)</li>
                  <li>• <strong>Last push approval:</strong> Not required (allows quick fixes)</li>
                </ul>
              </div>

              <div className="bg-white p-3 rounded border border-blue-200">
                <h4 className="font-medium text-blue-700 mb-2">Merge Options</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div className="text-center p-2 bg-blue-50 rounded">
                    <code className="text-xs font-mono text-blue-700">merge</code>
                    <p className="text-xs text-blue-600 mt-1">Merge commit</p>
                  </div>
                  <div className="text-center p-2 bg-blue-50 rounded">
                    <code className="text-xs font-mono text-blue-700">squash</code>
                    <p className="text-xs text-blue-600 mt-1">Squash & merge</p>
                  </div>
                  <div className="text-center p-2 bg-blue-50 rounded">
                    <code className="text-xs font-mono text-blue-700">rebase</code>
                    <p className="text-xs text-blue-600 mt-1">Rebase & merge</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-green-800">Default Branch Targeting</h3>
                <p className="text-green-700 text-sm mt-1">
                  Uses <code className="bg-green-100 px-1 rounded">~DEFAULT_BRANCH</code> to automatically 
                  protect your repository's default branch, whether it's named "main", "master", or something else.
                </p>
                <ul className="text-green-600 text-sm mt-2 space-y-1">
                  <li>• Works with any default branch name</li>
                  <li>• Automatically adapts to repository settings</li>
                  <li>• No manual configuration needed</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle id="workflow-integration">CI/CD Workflow Integration</CardTitle>
          <CardDescription>
            How branch naming directly controls workflow execution
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-700">
            The branch naming ruleset ensures that only properly named branches can trigger the automated 
            CI/CD workflows. This prevents accidental deployments and maintains clean project organization in TD.
          </p>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-medium text-green-800 mb-3">Workflow Trigger Logic</h3>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded border border-green-200">
                <h4 className="font-medium text-green-700 mb-2">Branch Deploy Workflow (branch_deploy.yml)</h4>
                <div className="text-sm text-green-600 space-y-1">
                  <p><strong>Triggers on:</strong></p>
                  <ul className="ml-4 space-y-1">
                    <li>• Push to <code className="bg-green-100 px-1 rounded">feat/*</code> branches</li>
                    <li>• Push to <code className="bg-green-100 px-1 rounded">fix/*</code> branches</li>
                    <li>• Push to <code className="bg-green-100 px-1 rounded">hot/*</code> branches</li>
                  </ul>
                  <p className="mt-2"><strong>Creates TD projects:</strong> <code className="bg-green-100 px-1 rounded">&#123;project&#125;_&#123;env&#125;_br-&#123;branch-name&#125;</code></p>
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-green-200">
                <h4 className="font-medium text-green-700 mb-2">Clean Up Workflow (clean_up.yml)</h4>
                <div className="text-sm text-green-600">
                  <p><strong>Triggers on:</strong> Branch deletion</p>
                  <p><strong>Cleans up:</strong> TD projects matching <code className="bg-green-100 px-1 rounded">br-&#123;branch-name&#125;</code> pattern</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-amber-800">Why This Matters</h3>
                <ul className="text-amber-700 text-sm mt-2 space-y-1">
                  <li>• <strong>Prevents conflicts:</strong> Wrong branch names could create conflicting TD projects</li>
                  <li>• <strong>Ensures cleanup:</strong> Only properly named branches get automatically cleaned up</li>
                  <li>• <strong>Team consistency:</strong> Everyone follows the same naming convention</li>
                  <li>• <strong>Workflow reliability:</strong> Guaranteed trigger patterns for CI/CD automation</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle id="repository-protection">Additional Protection Rules</CardTitle>
          <CardDescription>
            Supplementary protections for repository integrity
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-700">
            Beyond branch naming enforcement and main branch protection, the TD Value Accelerator applies 
            additional rules to maintain repository integrity and prevent common Git issues.
          </p>
          
          <div className="space-y-4">
            <div className="border border-slate-200 rounded-lg p-4">
              <h3 className="font-semibold text-slate-900 mb-3">Non-Fast-Forward Protection</h3>
              <div className="bg-slate-50 p-3 rounded border">
                <p className="text-sm font-medium text-slate-800 mb-2">Prevents force pushes that could:</p>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>• Overwrite other developers' work</li>
                  <li>• Lose commit history and break traceability</li>
                  <li>• Cause deployment workflow failures</li>
                  <li>• Create inconsistencies between local and remote branches</li>
                </ul>
              </div>
            </div>

            <div className="border border-slate-200 rounded-lg p-4">
              <h3 className="font-semibold text-slate-900 mb-3">Branch Targeting Rules</h3>
              <div className="bg-slate-50 p-3 rounded border">
                <p className="text-sm font-medium text-slate-800 mb-2">Ruleset applies to:</p>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>• <strong>Includes:</strong> All branches (<code className="bg-slate-200 px-1 rounded">~ALL</code>)</li>
                  <li>• <strong>Excludes:</strong> Main branch (<code className="bg-slate-200 px-1 rounded">refs/heads/main</code>)</li>
                  <li>• <strong>Reason:</strong> Main branch uses different protection rules</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}