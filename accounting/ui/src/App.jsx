import { useEffect } from 'react';
import { AccountsProvider, useAccounts } from './contexts/AccountsContext';
import { ToastProvider, useToast } from './contexts/ToastContext';
import { Layout } from './components/Layout';

function AccountsErrorToaster() {
  const { error } = useAccounts();
  const { show } = useToast();
  useEffect(() => {
    if (error) show('Could not load accounts', 'error');
  }, [error, show]);
  return null;
}

export function App() {
  return (
    <ToastProvider>
      <AccountsProvider>
        <AccountsErrorToaster />
        <Layout />
      </AccountsProvider>
    </ToastProvider>
  );
}
