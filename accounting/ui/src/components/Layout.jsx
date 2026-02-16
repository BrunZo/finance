import { Sidebar } from './Sidebar';
import { Reports } from './panels/Reports';
import { Transactions } from './panels/Transactions';
import { DescriptionTags } from './panels/DescriptionTags';
import { Accounts } from './panels/Accounts';
import { useState } from 'react';

const PANEL_MAP = {
  reports: Reports,
  accounts: Accounts,
  transactions: Transactions,
  'description-tags': DescriptionTags,
};

export function Layout() {
  const [currentPanel, setCurrentPanel] = useState('reports');
  const PanelComponent = PANEL_MAP[currentPanel];

  return (
    <div className="layout">
      <Sidebar currentPanel={currentPanel} onSelect={setCurrentPanel} />
      <main className="main">
        {PanelComponent && <PanelComponent />}
      </main>
    </div>
  );
}
