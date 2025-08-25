import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { Workflow, Info, CheckCircle } from 'lucide-react';
import { TableOfContents } from '../shared/TableOfContents';
import { CollapsibleWorkflows } from './CollapsibleWorkflows';

export function CiCdSection() {
  const tocItems = [
    { id: 'available-workflows', title: 'Available Workflows' },
    { id: 'branch-deploy', title: 'Branch Deploy', level: 2 },
    { id: 'production-deploy', title: 'Production Deploy', level: 2 },
    { id: 'branch-td-pull', title: 'Branch TD Pull', level: 2 },
    { id: 'releases', title: 'Releases', level: 2 },
    { id: 'clean-up', title: 'Clean Up', level: 2 },
    { id: 'custom-actions', title: 'Custom Actions' },
    { id: 'setting-up-cicd', title: 'Setting Up CI/CD in Your Repository' }
  ];

  return (
    <div className="space-y-6">
      <TableOfContents items={tocItems} />
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
            <Workflow className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">CI/CD Documentation</h1>
            <p className="text-slate-600 mt-1">
              Understanding and using the GitHub Actions workflows
            </p>
          </div>
        </div>
      </div>

      <CollapsibleWorkflows />

      <Card>
        <CardHeader>
          <CardTitle id="custom-actions">Custom Actions</CardTitle>
          <CardDescription>
            Reusable actions included with the starter pack
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium text-slate-900 mb-2">td_push</h4>
              <p className="text-sm text-slate-600 mb-2">Pushes workflows to TD instances</p>
              <ul className="text-xs text-slate-500 space-y-1">
                <li>• Handles project directory management</li>
                <li>• Supports branching and versioning</li>
                <li>• API token management</li>
              </ul>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium text-slate-900 mb-2">td_test_wf</h4>
              <p className="text-sm text-slate-600 mb-2">Automated workflow testing</p>
              <ul className="text-xs text-slate-500 space-y-1">
                <li>• Runs test workflows in TD</li>
                <li>• Validates deployment success</li>
                <li>• Integration testing support</li>
              </ul>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium text-slate-900 mb-2">td_test_sql</h4>
              <p className="text-sm text-slate-600 mb-2">SQL-based testing automation</p>
              <ul className="text-xs text-slate-500 space-y-1">
                <li>• Executes SQL test scripts</li>
                <li>• Data validation checks</li>
                <li>• Query result verification</li>
              </ul>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium text-slate-900 mb-2">td_delete</h4>
              <p className="text-sm text-slate-600 mb-2">Cleanup and deletion utilities</p>
              <ul className="text-xs text-slate-500 space-y-1">
                <li>• Removes test environments</li>
                <li>• Cleans up temporary resources</li>
                <li>• Branch-specific cleanup</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle id="setting-up-cicd">Setting Up CI/CD in Your Repository</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-blue-800">After Deployment</h3>
                <p className="text-blue-700 text-sm mt-1">
                  Once you deploy the starter pack to your repository, the workflows will be automatically available.
                </p>
              </div>
            </div>
          </div>

          <ol className="space-y-4">
            <li className="flex gap-4">
              <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">1</div>
              <div>
                <h3 className="font-medium text-slate-900">Repository Secrets (Auto-Configured)</h3>
                <p className="text-slate-600 text-sm mt-1">Environment secrets are automatically configured during deployment:</p>
                <div className="mt-2 bg-green-50 p-3 rounded border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Automatically Configured</span>
                  </div>
                  <ul className="text-sm space-y-1 text-green-700">
                    <li><code className="bg-green-100 px-1 rounded">TD_API_TOKEN</code>: Set for each environment (prod/qa/dev) based on your TD credentials</li>
                  </ul>
                </div>
                <div className="mt-3 bg-slate-50 p-3 rounded border">
                  <p className="text-sm font-medium text-slate-800 mb-2">Optional Manual Secrets:</p>
                  <ul className="text-sm space-y-1 text-slate-600">
                    <li><code className="bg-slate-200 px-1 rounded">SLACK_WEBHOOK_URL</code>: (Optional) For deployment notifications</li>
                  </ul>
                </div>
              </div>
            </li>

            <li className="flex gap-4">
              <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">2</div>
              <div>
                <h3 className="font-medium text-slate-900">Repository Variables (Auto-Configured)</h3>
                <p className="text-slate-600 text-sm mt-1">The following variables are automatically set during deployment:</p>
                <div className="mt-2 bg-green-50 p-3 rounded border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Automatically Configured</span>
                  </div>
                  <ul className="text-sm space-y-1 text-green-700">
                    <li><code className="bg-green-100 px-1 rounded">TD_WF_PROJS</code>: Project directory name (set to your project name)</li>
                    <li><code className="bg-green-100 px-1 rounded">TD_WF_API_ENDPOINT</code>: Regional TD workflow API endpoint</li>
                  </ul>
                </div>
                <div className="mt-3 bg-blue-50 p-3 rounded border border-blue-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Info className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Multiple Projects Support</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    As your project evolves, you can update <code className="bg-blue-100 px-1 rounded">TD_WF_PROJS</code> to include multiple project directories separated by pipes (|). 
                    Example: <code className="bg-blue-100 px-1 rounded">retail-project|qsr-project|analytics-project</code>
                  </p>
                </div>
              </div>
            </li>

            <li className="flex gap-4">
              <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">3</div>
              <div>
                <h3 className="font-medium text-slate-900">Run Manual Deployment</h3>
                <p className="text-slate-600 text-sm mt-1">Use the "Deploy Workflow" action for manual deployments:</p>
                <div className="mt-2 bg-slate-50 p-3 rounded border">
                  <p className="text-sm">Go to Actions → Deploy Workflow → Run workflow</p>
                </div>
              </div>
            </li>
          </ol>

          <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-purple-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-purple-800">Managing Multiple Value Accelerators</h3>
                <p className="text-purple-700 text-sm mt-1">
                  You can deploy multiple value accelerators (retail, QSR, etc.) to the same repository by organizing them in separate project directories. 
                  Update the <code className="bg-purple-100 px-1 rounded">TD_WF_PROJS</code> variable to include all project directories you want to deploy.
                </p>
                <div className="mt-3 p-3 bg-purple-100 rounded border">
                  <p className="text-xs font-medium text-purple-800 mb-1">Example Repository Structure:</p>
                  <div className="text-xs text-purple-700 font-mono space-y-1">
                    <div>├── retail-analytics/</div>
                    <div>├── qsr-insights/</div>
                    <div>├── custom-workflows/</div>
                    <div>└── .github/workflows/</div>
                  </div>
                  <p className="text-xs text-purple-700 mt-2">
                    Set <code className="bg-purple-200 px-1 rounded">TD_WF_PROJS</code> to: <code className="bg-purple-200 px-1 rounded">retail-analytics|qsr-insights|custom-workflows</code>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}