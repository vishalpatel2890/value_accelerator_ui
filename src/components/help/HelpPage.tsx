import { HelpCircle, Workflow, Shield, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { OverviewSection } from './sections/OverviewSection';
import { CiCdSection } from './sections/CiCdSection';
import { RulesetsSection } from './sections/RulesetsSection';

interface NavigationGroup {
  id: string;
  label: string;
  icon: React.ReactNode;
  sections: NavigationSection[];
}

interface NavigationSection {
  id: string;
  label: string;
  icon: React.ReactNode;
  group?: string;
}

export function HelpPage() {
  const [activeSection, setActiveSection] = useState('overview');
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['cicd']);

  const navigationGroups: NavigationGroup[] = [
    {
      id: 'getting-started',
      label: 'Getting Started',
      icon: <HelpCircle className="w-4 h-4" />,
      sections: [
        { id: 'overview', label: 'Overview', icon: <HelpCircle className="w-4 h-4" /> },
      ]
    },
    {
      id: 'cicd',
      label: 'CI/CD & Deployment',
      icon: <Workflow className="w-4 h-4" />,
      sections: [
        { id: 'cicd', label: 'Workflows & Actions', icon: <Workflow className="w-4 h-4" /> },
        { id: 'rulesets', label: 'GitHub Rulesets', icon: <Shield className="w-4 h-4" /> },
      ]
    }
  ];

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupId) 
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  return (
    <div className="flex h-full">
      {/* Sidebar Navigation */}
      <div className="w-64 border-r border-slate-200 bg-slate-50 p-4">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Help & Support</h2>
          <p className="text-sm text-slate-600">Documentation and guides</p>
        </div>
        
        <nav className="space-y-1">
          {navigationGroups.map((group) => (
            <div key={group.id}>
              {/* Group Header */}
              <button
                onClick={() => toggleGroup(group.id)}
                className="w-full flex items-center gap-2 px-2 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                {expandedGroups.includes(group.id) ? (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                )}
                {group.icon}
                <span className="flex-1 text-left">{group.label}</span>
              </button>

              {/* Group Sections */}
              {expandedGroups.includes(group.id) && (
                <div className="ml-6 mt-1 space-y-1">
                  {group.sections.map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                        activeSection === section.id
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {section.icon}
                      {section.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {activeSection === 'overview' && <OverviewSection />}

        {activeSection === 'cicd' && <CiCdSection />}

        {activeSection === 'rulesets' && <RulesetsSection />}
      </div>
    </div>
  );
}