import { useState, useEffect, useCallback } from 'react';
import { getTransactions, patchSplit, postAccount } from '../../api/client';
import { useAccounts } from '../../contexts/AccountsContext';
import { Select } from '../ui/Select';
import { formatAmountWithCurrency } from '../../utils/format';

function formatDate(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { dateStyle: 'short' }) + ' ' + d.toLocaleTimeString(undefined, { timeStyle: 'short' });
  } catch {
    return iso;
  }
}

export function Transactions() {
  const [status, setStatus] = useState('loading');
  const [data, setData] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [updatingSplitId, setUpdatingSplitId] = useState(null);
  const [newTagName, setNewTagName] = useState('');
  const [creatingTag, setCreatingTag] = useState(false);
  const [createTagError, setCreateTagError] = useState('');
  const { accounts, refetch: refetchAccounts } = useAccounts();

  const fetchTransactions = useCallback(() => {
    setStatus('loading');
    getTransactions()
      .then((rows) => {
        if (!rows || rows.length === 0) {
          setStatus('empty');
          setData([]);
        } else {
          setStatus('ok');
          setData(rows);
        }
      })
      .catch((err) => {
        setStatus('error');
        setErrorMessage(err.message || 'Could not load transactions');
      });
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const accountOptions = accounts.map((a) => ({ id: a.id, name: a.name }));

  async function onCreateTag(e) {
    e.preventDefault();
    const tag = newTagName.trim();
    if (!tag) return;
    setCreateTagError('');
    setCreatingTag(true);
    try {
      await postAccount({ account_type: 'expense', tag });
      setNewTagName('');
      await refetchAccounts();
    } catch (err) {
      setCreateTagError(err.message || 'Failed to create tag');
    } finally {
      setCreatingTag(false);
    }
  }

  async function onSplitAccountChange(split, newAccountId) {
    if (!newAccountId) return;
    setUpdatingSplitId(split.id);
    try {
      await patchSplit(split.id, { account_id: Number(newAccountId) });
      await fetchTransactions();
    } catch (_) {
      // keep previous state; could show toast
    } finally {
      setUpdatingSplitId(null);
    }
  }

  if (status === 'loading') {
    return (
      <div className="panel visible">
        <h2>Transactions</h2>
        <p className="hint">Edit splits to change expense category or account.</p>
        <div className="report-empty">Loading…</div>
      </div>
    );
  }

  if (status === 'empty') {
    return (
      <div className="panel visible">
        <h2>Transactions</h2>
        <p className="hint">Edit splits to change expense category or account.</p>
        <div className="report-empty">No transactions yet.</div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="panel visible">
        <h2>Transactions</h2>
        <p className="hint">Edit splits to change expense category or account.</p>
        <div className="report-empty">{errorMessage}</div>
      </div>
    );
  }

  return (
    <div className="panel visible">
      <h2>Transactions</h2>
      <p className="hint">All transactions and splits. Set expense tag to unify same-description transfers.</p>
      <form className="new-tag-form" onSubmit={onCreateTag}>
        <label htmlFor="new-expense-tag">New expense account</label>
        <input
          id="new-expense-tag"
          type="text"
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="e.g. subscriptions"
          disabled={creatingTag}
          autoComplete="off"
        />
        <button type="submit" className="btn btn-primary" disabled={creatingTag || !newTagName.trim()}>
          {creatingTag ? 'Creating…' : 'Create'}
        </button>
        {createTagError && <span className="form-error">{createTagError}</span>}
      </form>
      <div className="transactions-list">
        {data.map((tx) => (
          <div key={tx.id} className="transaction-block">
            <div className="transaction-header">
              <span className="tx-id">#{tx.id}</span>
              <span className="tx-date">{formatDate(tx.timestamp)}</span>
              {tx.currency && <span className="tx-currency">{tx.currency}</span>}
              <span className="tx-desc">{tx.description || '—'}</span>
            </div>
            <ul className="splits-list">
              {tx.splits.map((s) => (
                <li key={s.id} className="split-row">
                  <Select
                    options={accountOptions}
                    value={s.account_id}
                    onChange={(accountId) => onSplitAccountChange(s, accountId)}
                    placeholder="Account…"
                    disabled={updatingSplitId === s.id}
                  />
                  <span className={`split-amount ${parseFloat(s.amount) >= 0 ? 'debit' : 'credit'}`}>
                    {formatAmountWithCurrency(s.amount, tx.currency || 'EUR', { signed: true })}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
