import { Card, CardContent, CardHeader, CardTitle } from '@/lib/ui-components/ui/card';
import { List, ExternalLink } from 'lucide-react';

interface TableOfContentsItem {
  id: string;
  title: string;
  level?: 1 | 2 | 3; // For nested sections if needed
}

interface TableOfContentsProps {
  items: TableOfContentsItem[];
  title?: string;
}

export function TableOfContents({ items, title = "Table of Contents" }: TableOfContentsProps) {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  return (
    <Card className="mb-6 bg-slate-50 border-slate-200">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <List className="w-5 h-5 text-slate-600" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <nav className="space-y-2">
          {items.filter(item => !item.level || item.level === 1).map((item) => (
            <button
              key={item.id}
              onClick={() => scrollToSection(item.id)}
              className="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors hover:bg-slate-100 hover:text-slate-900 flex items-center gap-2 text-slate-700 font-medium"
            >
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
              <span className="flex-1">{item.title}</span>
            </button>
          ))}
        </nav>
      </CardContent>
    </Card>
  );
}