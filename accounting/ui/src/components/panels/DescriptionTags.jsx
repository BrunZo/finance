import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  getDescriptionTagMappings,
  getUncategorizedTransactions,
  postDescriptionTagMapping,
  patchDescriptionTagMapping,
  postAccount,
} from '../../api/client';
import { useAccounts } from '../../contexts/AccountsContext';
import { Select } from '../ui/Select';
import { formatAmountsByCurrency } from '../../utils/format';

function isUncategorizedAccount(account) {
  if (!account) return false;
  const tag = account.tag || '';
  return tag === 'uncategorized' || tag.startsWith('uncategorized:');
}

export function DescriptionTags() {
  const [status, setStatus] = useState('loading');
  const [mappings, setMappings] = useState([]);
  const [uncategorizedTx, setUncategorizedTx] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [updatingDescription, setUpdatingDescription] = useState(null);
  const [newTagName, setNewTagName] = useState('');
  const [newAccountType, setNewAccountType] = useState('expense');
  const [creatingTag, setCreatingTag] = useState(false);
  const [createTagError, setCreateTagError] = useState('');
  const { accounts, refetch: refetchAccounts } = useAccounts();

  const uncategorizedAccountIds = useMemo(
    () => new Set(accounts.filter(isUncategorizedAccount).map((a) => a.id)),
    [accounts]
  );

  const uncategorizedByDescription = useMemo(() => {
    const byDesc = {};
    for (const tx of uncategorizedTx) {
      const desc = tx.description || '';
      const currency = tx.currency || 'EUR';
      for (const s of tx.splits || []) {
        if (uncategorizedAccountIds.has(s.account_id)) {
          if (!byDesc[desc]) byDesc[desc] = { description: desc, amountsByCurrency: {}, count: 0 };
          byDesc[desc].amountsByCurrency[currency] =
            (byDesc[desc].amountsByCurrency[currency] || 0) + (parseFloat(s.amount) || 0);
          byDesc[desc].count += 1;
        }
      }
    }
    return Object.values(byDesc);
  }, [uncategorizedTx, uncategorizedAccountIds]);

  const mappingByDescription = useMemo(() => {
    const byDesc = {};
    for (const m of mappings) {
      byDesc[m.description] = m;
    }
    return byDesc;
  }, [mappings]);

  const rows = useMemo(() => {
    const seen = new Set();
    const out = [];
    for (const m of mappings) {
      if (!seen.has(m.description)) {
        seen.add(m.description);
        out.push({
          description: m.description,
          mapping: m,
          uncategorized: null,
        });
      }
    }
    for (const u of uncategorizedByDescription) {
      if (!seen.has(u.description)) {
        seen.add(u.description);
        out.push({
          description: u.description,
          mapping: null,
          uncategorized: u,
        });
      }
    }
    return out.sort((a, b) => {
      const aUncategorized = !a.mapping;
      const bUncategorized = !b.mapping;
      if (aUncategorized !== bUncategorized) return aUncategorized ? -1 : 1;
      return a.description.localeCompare(b.description);
    });
  }, [mappings, uncategorizedByDescription]);

  const categoryOptions = accounts
    .filter((a) => !isUncategorizedAccount(a))
    .map((a) => ({ id: a.id, name: a.name }));

  const fetchAll = useCallback(() => {
    setStatus('loading');
    Promise.all([getDescriptionTagMappings(), getUncategorizedTransactions()])
      .then(([mapRows, txRows]) => {
        setStatus('ok');
        setMappings(mapRows || []);
        setUncategorizedTx(txRows || []);
      })
      .catch((err) => {
        setStatus('error');
        setErrorMessage(err.message || 'Could not load data');
      });
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  async function onCreateTag(e) {
    e.preventDefault();
    const tag = newTagName.trim();
    if (!tag) return;
    setCreateTagError('');
    setCreatingTag(true);
    try {
      await postAccount({ account_type: newAccountType, tag });
      setNewTagName('');
      await refetchAccounts();
    } catch (err) {
      setCreateTagError(err.message || 'Failed to create account');
    } finally {
      setCreatingTag(false);
    }
  }

  async function onAccountChange(row, newAccountId) {
    if (!newAccountId) return;
    setUpdatingDescription(row.description);
    try {
      if (row.mapping) {
        await patchDescriptionTagMapping(row.mapping.id, {
          description: row.description,
          account_id: Number(newAccountId),
        });
      } else {
        await postDescriptionTagMapping({
          description: row.description,
          account_id: Number(newAccountId),
        });
      }
      await fetchAll();
    } catch (_) {
      // keep previous state; could show toast
    } finally {
      setUpdatingDescription(null);
    }
  }

  if (status === 'loading') {
    return (
      <div className="panel visible">
        <h2>Description → account</h2>
        <p className="hint">Map descriptions to any account. Changes apply to all matching transfers.</p>
        <div className="report-empty">Loading…</div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="panel visible">
        <h2>Description → account</h2>
        <p className="hint">Map descriptions to any account. Changes apply to all matching transfers.</p>
        <div className="report-empty">{errorMessage}</div>
      </div>
    );
  }

  return (
    <div className="panel visible">
      <h2>Description → account</h2>
      <p className="hint">Map descriptions to any account (expense, income, asset, liability). Changes apply to all matching transfers.</p>
      <form className="new-tag-form" onSubmit={onCreateTag}>
        <label htmlFor="new-account-type">Account type</label>
        <select
          id="new-account-type"
          value={newAccountType}
          onChange={(e) => setNewAccountType(e.target.value)}
          disabled={creatingTag}
        >
          <option value="expense">Expense</option>
          <option value="income">Income</option>
          <option value="asset">Asset</option>
          <option value="liability">Liability</option>
        </select>
        <label htmlFor="new-account-tag">Tag</label>
        <input
          id="new-account-tag"
          type="text"
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="e.g. subscriptions, salary, savings"
          disabled={creatingTag}
          autoComplete="off"
        />
        <button type="submit" className="btn btn-primary" disabled={creatingTag || !newTagName.trim()}>
          {creatingTag ? 'Creating…' : 'Create'}
        </button>
        {createTagError && <span className="form-error">{createTagError}</span>}
      </form>
      {rows.length === 0 ? (
        <div className="report-empty">No descriptions yet. Import transactions to see uncategorized ones.</div>
      ) : (
        <div className="description-tags-table-wrap">
          <table className="description-tags-table">
            <thead>
              <tr>
                <th>Description</th>
                <th className="amount-col">Amount</th>
                <th>Account</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.description || '(empty)'}>
                  <td className="desc-col">{row.description || '—'}</td>
                  <td className="amount-col">
                    {row.uncategorized ? formatAmountsByCurrency(row.uncategorized.amountsByCurrency) : '—'}
                  </td>
                  <td className="account-col">
                    <Select
                      options={categoryOptions}
                      value={row.mapping ? row.mapping.account_id : ''}
                      onChange={(accountId) => onAccountChange(row, accountId)}
                      placeholder="Choose account…"
                      disabled={updatingDescription === row.description}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
