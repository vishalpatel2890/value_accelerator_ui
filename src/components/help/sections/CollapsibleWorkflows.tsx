import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { GitBranch, ChevronDown, ChevronRight, Info, CheckCircle } from 'lucide-react';
import { useState } from 'react';

export function CollapsibleWorkflows() {
  const [expandedWorkflows, setExpandedWorkflows] = useState<string[]>([]);

  const toggleWorkflow = (workflowId: string) => {
    setExpandedWorkflows(prev => 
      prev.includes(workflowId) 
        ? prev.filter(id => id !== workflowId)
        : [...prev, workflowId]
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle id="available-workflows">Available Workflows</CardTitle>
        <CardDescription>
          The starter pack includes several GitHub Actions workflows for automated deployment
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          {/* Branch Deploy Workflow */}
          <div className="border border-slate-200 rounded-lg">
            <button
              onClick={() => toggleWorkflow('branch-deploy')}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
            >
              {expandedWorkflows.includes('branch-deploy') ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <GitBranch className="w-5 h-5 text-green-600" />
              <div className="flex-1">
                <h3 id="branch-deploy" className="font-semibold text-slate-900">Branch Deploy (branch_deploy.yml)</h3>
                <p className="text-slate-600 text-sm mt-1">Automatic deployment and testing for feature development branches</p>
              </div>
            </button>
            
            {expandedWorkflows.includes('branch-deploy') && (
              <div className="px-4 pb-4 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="bg-green-50 p-3 rounded border border-green-200">
                    <p className="text-sm font-medium text-green-800 mb-1">🚀 Triggers</p>
                    <ul className="text-xs text-green-700 space-y-1">
                      <li>• Push to <code className="bg-green-100 px-1 rounded">feat/*</code> branches</li>
                      <li>• Push to <code className="bg-green-100 px-1 rounded">fix/*</code> branches</li>
                      <li>• Push to <code className="bg-green-100 px-1 rounded">hot/*</code> branches</li>
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-1">✅ Outcomes</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• Deploys workflows to qa/dev environment</li>
                      <li>• Runs automated tests (workflow & SQL)</li>
                      <li>• Sends Slack notifications</li>
                      <li>• Creates branch-specific TD projects</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded border mb-3">
                  <p className="text-sm font-medium text-slate-800 mb-2">Key Features:</p>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• Incremental deployments (only changed project directories)</li>
                    <li>• Branch naming determines project suffix</li>
                    <li>• Environment detection via commit message</li>
                    <li>• Automated quality assurance testing</li>
                  </ul>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-yellow-600 font-medium text-sm">📋 Usage Instructions:</span>
                  </div>
                  <ul className="text-sm text-yellow-800 space-y-2 mt-2">
                    <li><strong>Environment Selection:</strong> Include <code className="bg-yellow-100 px-1 rounded">dply_dev</code> in your commit message to deploy to dev environment. Without this keyword, deployment goes to qa environment by default.</li>
                    <li><strong>Deployment Type:</strong> Include <code className="bg-yellow-100 px-1 rounded">dplytp_full</code> in commit message to force full deployment. Otherwise, only project directories with changes since last successful workflow run are deployed.</li>
                    <li><strong>Branch Naming:</strong> Use <code className="bg-yellow-100 px-1 rounded">feat/feature-name</code>, <code className="bg-yellow-100 px-1 rounded">fix/bug-name</code>, or <code className="bg-yellow-100 px-1 rounded">hot/hotfix-name</code> patterns.</li>
                    <li><strong>Project Names:</strong> TD projects follow the pattern <code className="bg-yellow-100 px-1 rounded">&#123;base-project&#125;_&#123;environment&#125;_br-&#123;branch-name&#125;</code> for isolation. Base project comes from directory name (e.g., "retail-starter-pack"), environment is qa/dev, and branch name is extracted from the last part after splitting on "/".</li>
                  </ul>
                  <div className="mt-3 p-3 bg-yellow-100 rounded border">
                    <p className="text-xs font-medium text-yellow-800 mb-1">Example Project Names:</p>
                    <ul className="text-xs text-yellow-700 space-y-1">
                      <li>• Branch <code>feat/user-auth</code> → <code>retail-starter-pack_qa_br-user-auth</code></li>
                      <li>• Branch <code>fix/login-bug</code> with dply_dev → <code>retail-starter-pack_dev_br-login-bug</code></li>
                      <li>• Branch <code>hot/critical-fix</code> → <code>qsr-starter-pack_qa_br-critical-fix</code></li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Production Deploy Workflow */}
          <div className="border border-slate-200 rounded-lg">
            <button
              onClick={() => toggleWorkflow('production-deploy')}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
            >
              {expandedWorkflows.includes('production-deploy') ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <GitBranch className="w-5 h-5 text-purple-600" />
              <div className="flex-1">
                <h3 id="production-deploy" className="font-semibold text-slate-900">Production Deploy (deploy.yml)</h3>
                <p className="text-slate-600 text-sm mt-1">Manual production deployment with version control and environment targeting</p>
              </div>
            </button>
            
            {expandedWorkflows.includes('production-deploy') && (
              <div className="px-4 pb-4 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="bg-purple-50 p-3 rounded border border-purple-200">
                    <p className="text-sm font-medium text-purple-800 mb-1">🚀 Triggers</p>
                    <ul className="text-xs text-purple-700 space-y-1">
                      <li>• Manual workflow dispatch only</li>
                      <li>• Requires environment selection</li>
                      <li>• Optional version specification</li>
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-1">✅ Outcomes</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• Deploys to prod/qa/dev environments</li>
                      <li>• Creates versioned deployments</li>
                      <li>• Tracks deployment history</li>
                      <li>• Supports rollback scenarios</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded border mb-3">
                  <p className="text-sm font-medium text-slate-800 mb-2">Required Inputs:</p>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• <code className="bg-slate-200 px-1 rounded">version</code>: Git tag/version to deploy (optional)</li>
                    <li>• <code className="bg-slate-200 px-1 rounded">env</code>: Target environment (prod/qa/dev)</li>
                    <li>• <code className="bg-slate-200 px-1 rounded">deploy_type</code>: Full or incremental deployment</li>
                  </ul>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-blue-600 font-medium text-sm">📋 Usage Instructions:</span>
                  </div>
                  <ol className="text-sm text-blue-800 space-y-2 mt-2 list-decimal list-inside">
                    <li><strong>Navigate to Actions:</strong> Go to your repository's Actions tab</li>
                    <li><strong>Select Workflow:</strong> Find "deploy" workflow and click "Run workflow"</li>
                    <li><strong>Fill Parameters:</strong>
                      <ul className="ml-4 mt-1 space-y-1 text-xs">
                        <li>• Leave <code className="bg-blue-100 px-1 rounded">version</code> empty for latest main branch</li>
                        <li>• Choose <code className="bg-blue-100 px-1 rounded">env</code>: prod (production), qa (testing), or dev (development)</li>
                        <li>• Select <code className="bg-blue-100 px-1 rounded">deploy_type</code>: "full" (complete) or "inc" (incremental)</li>
                      </ul>
                    </li>
                    <li><strong>Environment Setup:</strong> Ensure target environment has required secrets and variables configured</li>
                  </ol>
                  <div className="mt-3 p-3 bg-blue-100 rounded border">
                    <p className="text-xs font-medium text-blue-800 mb-1">Environment Notes:</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• <strong>prod:</strong> No environment protection (direct deploy)</li>
                      <li>• <strong>qa/dev:</strong> Uses environment-specific protection rules</li>
                      <li>• <strong>Incremental:</strong> Only deploys changes since last successful run</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Branch TD Pull Workflow */}
          <div className="border border-slate-200 rounded-lg">
            <button
              onClick={() => toggleWorkflow('branch-td-pull')}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
            >
              {expandedWorkflows.includes('branch-td-pull') ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <GitBranch className="w-5 h-5 text-orange-600" />
              <div className="flex-1">
                <h3 id="branch-td-pull" className="font-semibold text-slate-900">Branch TD Pull (branch_td_pull.yml)</h3>
                <p className="text-slate-600 text-sm mt-1">Pull changes from TD environment back to repository for synchronization</p>
              </div>
            </button>
            
            {expandedWorkflows.includes('branch-td-pull') && (
              <div className="px-4 pb-4 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="bg-orange-50 p-3 rounded border border-orange-200">
                    <p className="text-sm font-medium text-orange-800 mb-1">🚀 Triggers</p>
                    <ul className="text-xs text-orange-700 space-y-1">
                      <li>• Manual workflow dispatch only</li>
                      <li>• Requires environment selection</li>
                      <li>• Requires commit message input</li>
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-1">✅ Outcomes</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• Downloads workflows from TD</li>
                      <li>• Commits changes to current branch</li>
                      <li>• Syncs repository with TD state</li>
                      <li>• Can trigger downstream deployments</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded border mb-3">
                  <p className="text-sm font-medium text-slate-800 mb-2">Use Cases:</p>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• Sync manual changes made in TD console</li>
                    <li>• Backup production workflows to repository</li>
                    <li>• Recover from repository/TD drift</li>
                    <li>• Chain with deployment workflows via commit message</li>
                  </ul>
                </div>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-orange-600 font-medium text-sm">📋 Usage Instructions:</span>
                  </div>
                  <ol className="text-sm text-orange-800 space-y-2 mt-2 list-decimal list-inside">
                    <li><strong>Navigate to Actions:</strong> Go to repository Actions → "branch td pull"</li>
                    <li><strong>Run Workflow:</strong> Click "Run workflow" on your current branch</li>
                    <li><strong>Select Environment:</strong> Choose which TD environment to pull from (prod/qa/dev)</li>
                    <li><strong>Commit Message:</strong> Provide descriptive message for the sync commit</li>
                  </ol>
                  <div className="mt-3 p-3 bg-orange-100 rounded border">
                    <p className="text-xs font-medium text-orange-800 mb-1">Important Notes:</p>
                    <ul className="text-xs text-orange-700 space-y-1">
                      <li>• <strong>Chaining:</strong> Include <code className="bg-orange-200 px-1 rounded">dply_dev</code> in commit message to trigger dev deployment after pull</li>
                      <li>• <strong>Branch Sync:</strong> Only pulls workflows matching current branch pattern</li>
                      <li>• <strong>Auto Commit:</strong> Changes are automatically committed with your message</li>
                      <li>• <strong>Conflicts:</strong> Review pulled changes before merging to main</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Releases Workflow */}
          <div className="border border-slate-200 rounded-lg">
            <button
              onClick={() => toggleWorkflow('releases')}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
            >
              {expandedWorkflows.includes('releases') ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <GitBranch className="w-5 h-5 text-indigo-600" />
              <div className="flex-1">
                <h3 id="releases" className="font-semibold text-slate-900">Releases (releases.yml)</h3>
                <p className="text-slate-600 text-sm mt-1">Automated release management with conventional changelog generation</p>
              </div>
            </button>
            
            {expandedWorkflows.includes('releases') && (
              <div className="px-4 pb-4 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="bg-indigo-50 p-3 rounded border border-indigo-200">
                    <p className="text-sm font-medium text-indigo-800 mb-1">🚀 Triggers</p>
                    <ul className="text-xs text-indigo-700 space-y-1">
                      <li>• Push to <code className="bg-indigo-100 px-1 rounded">main</code> branch</li>
                      <li>• Conventional commit analysis</li>
                      <li>• Automatic version detection</li>
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-1">✅ Outcomes</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• Creates GitHub releases</li>
                      <li>• Generates version tags</li>
                      <li>• Updates CHANGELOG.md</li>
                      <li>• Sends release notifications</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded border mb-3">
                  <p className="text-sm font-medium text-slate-800 mb-2">Conventional Commits:</p>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• <code className="bg-slate-200 px-1 rounded">feat:</code> New features (minor version bump)</li>
                    <li>• <code className="bg-slate-200 px-1 rounded">fix:</code> Bug fixes (patch version bump)</li>
                    <li>• <code className="bg-slate-200 px-1 rounded">BREAKING CHANGE:</code> Major version bump</li>
                    <li>• Automatic changelog and release notes generation</li>
                  </ul>
                </div>

                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-indigo-600 font-medium text-sm">📋 Usage Instructions:</span>
                  </div>
                  <div className="text-sm text-indigo-800 space-y-2 mt-2">
                    <p><strong>Automatic Triggering:</strong> This workflow runs automatically when commits are pushed to main branch.</p>
                    <div className="mt-3">
                      <p className="font-medium mb-2">Follow Conventional Commit Format:</p>
                      <ul className="space-y-1 text-xs ml-4">
                        <li>• <code className="bg-indigo-100 px-1 rounded">feat(scope): description</code> - New features</li>
                        <li>• <code className="bg-indigo-100 px-1 rounded">fix(scope): description</code> - Bug fixes</li>
                        <li>• <code className="bg-indigo-100 px-1 rounded">docs: update README</code> - Documentation</li>
                        <li>• <code className="bg-indigo-100 px-1 rounded">refactor: improve code structure</code> - Code improvements</li>
                      </ul>
                    </div>
                  </div>
                  <div className="mt-3 p-3 bg-indigo-100 rounded border">
                    <p className="text-xs font-medium text-indigo-800 mb-1">Example Workflow:</p>
                    <ol className="text-xs text-indigo-700 space-y-1 list-decimal list-inside">
                      <li>Create feature branch: <code className="bg-indigo-200 px-1 rounded">feat/user-authentication</code></li>
                      <li>Make commits with conventional format</li>
                      <li>Create PR to main with conventional commit title</li>
                      <li>Merge PR → Release workflow triggers automatically</li>
                      <li>New version tag and GitHub release created</li>
                    </ol>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Clean Up Workflow */}
          <div className="border border-slate-200 rounded-lg">
            <button
              onClick={() => toggleWorkflow('clean-up')}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
            >
              {expandedWorkflows.includes('clean-up') ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <GitBranch className="w-5 h-5 text-red-600" />
              <div className="flex-1">
                <h3 id="clean-up" className="font-semibold text-slate-900">Clean Up (clean_up.yml)</h3>
                <p className="text-slate-600 text-sm mt-1">Automatic cleanup of TD resources when feature branches are deleted</p>
              </div>
            </button>
            
            {expandedWorkflows.includes('clean-up') && (
              <div className="px-4 pb-4 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="bg-red-50 p-3 rounded border border-red-200">
                    <p className="text-sm font-medium text-red-800 mb-1">🚀 Triggers</p>
                    <ul className="text-xs text-red-700 space-y-1">
                      <li>• Branch deletion events</li>
                      <li>• Automatic detection of deleted branches</li>
                      <li>• Only triggers for branch deletions (not tags)</li>
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-1">✅ Outcomes</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• Deletes branch-specific TD projects</li>
                      <li>• Cleans up dev and qa environments</li>
                      <li>• Removes associated databases/tables</li>
                      <li>• Sends cleanup completion notifications</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded border mb-3">
                  <p className="text-sm font-medium text-slate-800 mb-2">Cleanup Process:</p>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• Sequential cleanup: dev environment first, then qa</li>
                    <li>• Extracts branch name from deletion event</li>
                    <li>• Removes workflows and databases matching branch pattern</li>
                    <li>• Prevents resource accumulation from deleted branches</li>
                  </ul>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-red-600 font-medium text-sm">📋 Usage Instructions:</span>
                  </div>
                  <div className="text-sm text-red-800 space-y-2 mt-2">
                    <p><strong>Automatic Operation:</strong> This workflow runs automatically when you delete branches - no manual action required.</p>
                    <div className="mt-3">
                      <p className="font-medium mb-2">What Gets Cleaned:</p>
                      <ul className="space-y-1 text-xs ml-4">
                        <li>• TD workflow projects with <code className="bg-red-100 px-1 rounded">br-&#123;branch-name&#125;</code> pattern</li>
                        <li>• Associated databases and tables in dev/qa environments</li>
                        <li>• Temporary resources created during feature development</li>
                      </ul>
                    </div>
                  </div>
                  <div className="mt-3 p-3 bg-red-100 rounded border">
                    <p className="text-xs font-medium text-red-800 mb-1">Best Practices:</p>
                    <ul className="text-xs text-red-700 space-y-1">
                      <li>• Delete feature branches after merging to main</li>
                      <li>• Monitor Actions tab to verify successful cleanup</li>
                      <li>• Check Slack notifications for cleanup status</li>
                      <li>• Only production resources are preserved</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}