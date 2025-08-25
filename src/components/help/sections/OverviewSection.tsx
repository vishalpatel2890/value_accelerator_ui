import { Card, CardContent, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { HelpCircle } from 'lucide-react';
import { TableOfContents } from '../shared/TableOfContents';

export function OverviewSection() {
  const tocItems = [
    { id: 'what-is-td-value-accelerator', title: 'What is the TD Value Accelerator?' },
    { id: 'getting-started', title: 'Getting Started' }
  ];

  return (
    <div className="space-y-6">
      <TableOfContents items={tocItems} />
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <HelpCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">TD Value Accelerator</h1>
            <p className="text-slate-600 mt-1">
              Deploy Treasure Data starter pack workflows with automated CI/CD
            </p>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle id="what-is-td-value-accelerator">What is the TD Value Accelerator?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-700">
            The TD Value Accelerator is a web application that simplifies the deployment of Treasure Data starter pack workflows. 
            It provides a guided interface to:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-slate-700">
            <li>Configure your Treasure Data connection and credentials</li>
            <li>Deploy retail or QSR starter pack workflows to your TD instance</li>
            <li>Set up automated CI/CD pipelines using GitHub Actions</li>
            <li>Configure GitHub repository rulesets for branch protection</li>
            <li>Monitor deployment progress with real-time logs</li>
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle id="getting-started">Getting Started</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold">1</div>
                <h3 className="font-medium">Configure</h3>
              </div>
              <p className="text-sm text-slate-600">Set up your TD credentials and test connectivity</p>
            </div>
            <div className="p-4 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold">2</div>
                <h3 className="font-medium">Deploy</h3>
              </div>
              <p className="text-sm text-slate-600">Deploy starter pack workflows to your GitHub repository</p>
            </div>
            <div className="p-4 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold">3</div>
                <h3 className="font-medium">Ingest</h3>
              </div>
              <p className="text-sm text-slate-600">Set up data ingestion for your workflows</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}