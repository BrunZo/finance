import { useState } from 'react';
import { formatAmount, formatAmountsByCurrency } from '../../utils/format';

export { formatAmount, formatAmountsByCurrency };

/** Aggregate rows by account_name into { account_name, amountsByCurrency } */
export function aggregateByCategory(rows) {
  const map = {};
  for (const row of rows) {
    if (!map[row.account_name]) map[row.account_name] = { account_name: row.account_name, amountsByCurrency: {} };
    map[row.account_name].amountsByCurrency[row.currency] =
      (map[row.account_name].amountsByCurrency[row.currency] || 0) + row.amount;
  }
  return Object.values(map);
}

function TreeNodeRow({ node, depth, expanded, onToggle }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expanded.has(node.full_name);

  return (
    <>
      <tr
        key={node.full_name}
        className={hasChildren ? 'tree-row-parent' : 'tree-row-leaf'}
        style={{ '--tree-depth': depth }}
      >
        <td className="tree-cell">
          {hasChildren ? (
            <button
              type="button"
              className="tree-toggle"
              onClick={() => onToggle(node.full_name)}
              aria-expanded={isExpanded}
            >
              {isExpanded ? '−' : '+'}
            </button>
          ) : (
            <span className="tree-toggle-placeholder" />
          )}
          <span className="tree-label">{node.name}</span>
        </td>
        <td className="amount">{formatAmountsByCurrency(node.total_amounts_by_currency)}</td>
      </tr>
      {hasChildren && isExpanded &&
        node.children.map((child) => (
          <TreeNodeRow
            key={child.full_name}
            node={child}
            depth={depth + 1}
            expanded={expanded}
            onToggle={onToggle}
          />
        ))}
    </>
  );
}

export function ExpenseTable({ tree, totalsByCurrency }) {
  const [expanded, setExpanded] = useState(new Set());

  const toggle = (fullName) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(fullName)) next.delete(fullName);
      else next.add(fullName);
      return next;
    });
  };

  const children = tree?.children ?? [];

  return (
    <table className="report-table report-tree-table">
      <thead>
        <tr>
          <th>Category</th>
          <th className="amount">Amount</th>
        </tr>
      </thead>
      <tbody>
        {children.map((node) => (
          <TreeNodeRow
            key={node.full_name}
            node={node}
            depth={0}
            expanded={expanded}
            onToggle={toggle}
          />
        ))}
      </tbody>
      <tfoot>
        <tr className="report-total">
          <td>Total</td>
          <td className="amount">
            {totalsByCurrency && formatAmountsByCurrency(totalsByCurrency)}
          </td>
        </tr>
      </tfoot>
    </table>
  );
}
