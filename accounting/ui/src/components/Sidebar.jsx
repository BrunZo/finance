import { NavButton } from './NavButton';

const PANELS = [
  { id: 'reports', label: 'Reports' },
  { id: 'accounts', label: 'Accounts' },
  { id: 'description-tags', label: 'Description tags' },
  { id: 'transactions', label: 'Transactions' },
];

export function Sidebar({ currentPanel, onSelect }) {
  return (
    <aside className="sidebar">
      <h1>Ledger</h1>
      {PANELS.map(({ id, label }) => (
        <NavButton
          key={id}
          active={currentPanel === id}
          onClick={() => onSelect(id)}
        >
          {label}
        </NavButton>
      ))}
    </aside>
  );
}
