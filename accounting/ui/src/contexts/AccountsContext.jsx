import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getAccounts } from '../api/client';

const AccountsContext = createContext(null);

export function AccountsProvider({ children }) {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(() => {
    setLoading(true);
    setError(null);
    getAccounts()
      .then(setAccounts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  const byType = (type) => accounts.filter((a) => a.account_type === type);
  const assets = byType('asset');
  const liabilities = byType('liability');
  const expenses = byType('expense');
  const receivableAccounts = accounts.filter(
    (a) => a.account_type === 'asset' && (a.tag === 'receivables' || a.tag.startsWith('receivables:'))
  );
  const bankOrReceivable = receivableAccounts.length ? receivableAccounts : assets;

  return (
    <AccountsContext.Provider
      value={{
        accounts,
        loading,
        error,
        refetch,
        assets,
        liabilities,
        expenses,
        receivableAccounts: bankOrReceivable,
      }}
    >
      {children}
    </AccountsContext.Provider>
  );
}

export function useAccounts() {
  const ctx = useContext(AccountsContext);
  if (!ctx) throw new Error('useAccounts must be used within AccountsProvider');
  return ctx;
}
