import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CredentialsProvider } from './contexts/CredentialsContext';
import { GitHubProvider } from './contexts/GitHubContext';
import { SidebarLayout } from './components/shared/SidebarLayout';
import { ConfigurationPage } from './components/configuration/ConfigurationPage';
import { StarterPackSelection } from './components/selection/StarterPackSelection';
import { DeploymentPage } from './components/deployment/DeploymentPage';
import { IngestionPage } from './components/ingestion/IngestionPage';
import { HelpPage } from './components/help/HelpPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CredentialsProvider>
        <GitHubProvider>
          <Router>
            <SidebarLayout>
              <Routes>
                <Route path="/" element={<Navigate to="/configuration" replace />} />
                <Route path="/configuration" element={<ConfigurationPage />} />
                <Route path="/selection" element={<StarterPackSelection />} />
                <Route path="/deployment" element={<DeploymentPage />} />
                <Route path="/ingestion" element={<IngestionPage />} />
                <Route path="/help" element={<HelpPage />} />
              </Routes>
            </SidebarLayout>
          </Router>
        </GitHubProvider>
      </CredentialsProvider>
    </QueryClientProvider>
  );
}

export default App;