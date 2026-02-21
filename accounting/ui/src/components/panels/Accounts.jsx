import { useState, useEffect, useCallback } from 'react';
import {
  getAccounts,
  postAccount,
  patchAccount,
  deleteAccount,
} from '../../api/client';
import { useAccounts } from '../../contexts/AccountsContext';
import { useToast } from '../../contexts/ToastContext';
import { formatAmountsByCurrency } from '../../utils/format';

const ACCOUNT_TYPES = [
  { value: 'asset', label: 'Asset' },
  { value: 'liability', label: 'Liability' },
  { value: 'income', label: 'Income' },
  { value: 'expense', label: 'Expense' },
];

function isNetDebit(balanceByCurrency) {
  if (!balanceByCurrency || Object.keys(balanceByCurrency).length === 0) return true;
  const amounts = Object.values(balanceByCurrency);
  return amounts.every((a) => parseFloat(a) >= 0);
}

export function Accounts() {
  const [status, setStatus] = useState('loading');
  const [accounts, setAccounts] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [newAccountType, setNewAccountType] = useState('expense');
  const [newTag, setNewTag] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editType, setEditType] = useState('');
  const [editTag, setEditTag] = useState('');
  const [deletingId, setDeletingId] = useState(null);
  const { refetch: refetchAccounts } = useAccounts();
  const { show } = useToast();

  const fetchAccounts = useCallback(() => {
    setStatus('loading');
    getAccounts()
      .then((rows) => {
        setStatus('ok');
        setAccounts(rows || []);
      })
      .catch((err) => {
        setStatus('error');
        setErrorMessage(err.message || 'Could not load accounts');
      });
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  async function handleCreate(e) {
    e.preventDefault();
    const tag = newTag.trim();
    if (!tag) return;
    setCreateError('');
    setCreating(true);
    try {
      await postAccount({ account_type: newAccountType, tag });
      setNewTag('');
      await refetchAccounts();
      fetchAccounts();
      show('Account created', 'success');
    } catch (err) {
      setCreateError(err.message || 'Failed to create account');
    } finally {
      setCreating(false);
    }
  }

  function startEdit(account) {
    setEditingId(account.id);
    setEditType(account.account_type);
    setEditTag(account.tag);
  }

  function cancelEdit() {
    setEditingId(null);
    setEditType('');
    setEditTag('');
  }

  async function saveEdit() {
    const tag = editTag.trim();
    if (!tag) return;
    try {
      await patchAccount(editingId, { account_type: editType, tag });
      await refetchAccounts();
      fetchAccounts();
      show('Account updated', 'success');
      cancelEdit();
    } catch (err) {
      show(err.message || 'Failed to update account', 'error');
    }
  }

  async function handleDelete(account) {
    if (!window.confirm(`Delete account "${account.name}"? This may fail if it has transactions.`)) return;
    setDeletingId(account.id);
    try {
      await deleteAccount(account.id);
      await refetchAccounts();
      fetchAccounts();
      show('Account deleted', 'success');
    } catch (err) {
      show(err.message || 'Failed to delete account', 'error');
    } finally {
      setDeletingId(null);
    }
  }

  const accountsByType = ACCOUNT_TYPES.reduce((acc, { value }) => {
    acc[value] = accounts.filter((a) => a.account_type === value);
    return acc;
  }, {});

  if (status === 'loading') {
    return (
      <div className="panel visible">
        <h2>Accounts</h2>
        <p className="hint">Create, edit, or delete ledger accounts.</p>
        <div className="report-empty">Loading…</div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="panel visible">
        <h2>Accounts</h2>
        <p className="hint">Create, edit, or delete ledger accounts.</p>
        <div className="report-empty">{errorMessage}</div>
      </div>
    );
  }

  return (
    <div className="panel visible">
      <h2>Accounts</h2>
      <p className="hint">Create, edit, or delete ledger accounts.</p>

      <form className="accounts-create-form" onSubmit={handleCreate}>
        <div className="accounts-create-row">
          <label htmlFor="new-account-type">Type</label>
          <select
            id="new-account-type"
            value={newAccountType}
            onChange={(e) => setNewAccountType(e.target.value)}
            disabled={creating}
          >
            {ACCOUNT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div className="accounts-create-row">
          <label htmlFor="new-account-tag">Tag</label>
          <input
            id="new-account-tag"
            type="text"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="e.g. bank-main, subscriptions"
            disabled={creating}
            autoComplete="off"
          />
        </div>
        <div className="accounts-create-row">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={creating || !newTag.trim()}
          >
            {creating ? 'Creating…' : 'Create account'}
          </button>
        </div>
        {createError && <span className="form-error">{createError}</span>}
      </form>

      <div className="accounts-list">
        {ACCOUNT_TYPES.map(({ value, label }) => {
          const list = accountsByType[value] || [];
          if (list.length === 0) return null;
          return (
            <div key={value} className="accounts-type-group">
              <h3 className="accounts-type-label">{label}</h3>
              <table className="report-table accounts-table">
                <thead>
                  <tr>
                    <th>Account</th>
                    <th>Tag</th>
                    <th className="accounts-balance-col">Balance</th>
                    <th className="accounts-actions-col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((account) => (
                    <tr key={account.id}>
                      {editingId === account.id ? (
                        <>
                          <td>
                            <select
                              value={editType}
                              onChange={(e) => setEditType(e.target.value)}
                              className="accounts-edit-select"
                            >
                              {ACCOUNT_TYPES.map((t) => (
                                <option key={t.value} value={t.value}>
                                  {t.label}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td>
                            <input
                              type="text"
                              value={editTag}
                              onChange={(e) => setEditTag(e.target.value)}
                              className="accounts-edit-input"
                              placeholder="Tag"
                              autoFocus
                            />
                          </td>
                          <td className="accounts-balance-col">—</td>
                          <td className="accounts-actions-col">
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              onClick={saveEdit}
                              disabled={!editTag.trim()}
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-sm"
                              onClick={cancelEdit}
                            >
                              Cancel
                            </button>
                          </td>
                        </>
                      ) : (
                        <>
                          <td className="accounts-name">{account.name}</td>
                          <td className="accounts-tag">{account.tag}</td>
                          <td
                            className={`accounts-balance amount ${isNetDebit(account.balance_by_currency) ? 'debit' : 'credit'}`}
                          >
                            {formatAmountsByCurrency(account.balance_by_currency ?? {}, {
                              signed: true,
                            }) || '—'}
                          </td>
                          <td className="accounts-actions-col">
                            <button
                              type="button"
                              className="btn btn-ghost btn-sm"
                              onClick={() => startEdit(account)}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-sm accounts-delete-btn"
                              onClick={() => handleDelete(account)}
                              disabled={deletingId === account.id}
                            >
                              {deletingId === account.id ? 'Deleting…' : 'Delete'}
                            </button>
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>

      {accounts.length === 0 && (
        <div className="report-empty">No accounts yet. Create one above.</div>
      )}
    </div>
  );
}
