import { useState, useEffect, useMemo } from 'react';
import { getExpensesTreeReport } from '../../api/client';
import { ExpenseTable } from '../report/ExpenseTable';
import { ExpenseChart } from '../report/ExpenseChart';

function sumTotalsFromTree(children) {
  const totals = {};
  for (const node of children || []) {
    for (const [curr, amt] of Object.entries(node.total_amounts_by_currency || {})) {
      totals[curr] = (totals[curr] || 0) + amt;
    }
  }
  return totals;
}

/** Flatten top-level tree nodes for pie chart: [{ account_name, currency, amount }] */
function treeToPieRows(children) {
  const rows = [];
  for (const node of children || []) {
    for (const [curr, amt] of Object.entries(node.total_amounts_by_currency || {})) {
      if (amt > 0) rows.push({ account_name: node.full_name, currency: curr, amount: amt });
    }
  }
  return rows;
}

export function Reports() {
  const [status, setStatus] = useState('loading'); // 'loading' | 'empty' | 'error' | 'ok'
  const [tree, setTree] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    setStatus('loading');
    getExpensesTreeReport()
      .then((data) => {
        if (!data?.children?.length) {
          setStatus('empty');
          setTree(null);
        } else {
          setStatus('ok');
          setTree(data);
        }
      })
      .catch((err) => {
        setStatus('error');
        setErrorMessage(err.message || 'Could not load report');
      });
  }, []);

  const totalsByCurrency = useMemo(
    () => (tree?.children ? sumTotalsFromTree(tree.children) : {}),
    [tree]
  );

  const pieRows = useMemo(
    () => (tree?.children ? treeToPieRows(tree.children) : []),
    [tree]
  );

  if (status === 'loading') {
    return (
      <div className="panel visible">
        <h2>Reports</h2>
        <p className="hint">Expense totals by category (your share of spending only).</p>
        <div className="report-empty">Loading…</div>
      </div>
    );
  }

  if (status === 'empty') {
    return (
      <div className="panel visible">
        <h2>Reports</h2>
        <p className="hint">Expense totals by category (your share of spending only).</p>
        <div className="report-empty">No expense data yet.</div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="panel visible">
        <h2>Reports</h2>
        <p className="hint">Expense totals by category (your share of spending only).</p>
        <div className="report-empty">{errorMessage}</div>
      </div>
    );
  }

  return (
    <div className="panel visible">
      <h2>Reports</h2>
      <p className="hint">Expense totals by category (your share of spending only).</p>
      <ExpenseTable tree={tree} totalsByCurrency={totalsByCurrency} />
      <ExpenseChart rows={pieRows} />
    </div>
  );
}
