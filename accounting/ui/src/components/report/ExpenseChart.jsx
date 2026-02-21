import { formatAmount, formatAmountWithCurrency } from '../../utils/format';

const CURRENCY_PREFIX = { ARS: '$', USD: 'U$S', EUR: '€' };

const PIE_COLORS = [
  '#7c3aed', '#22c55e', '#3b82f6', '#f59e0b', '#ec4899', '#06b6d4',
  '#8b5cf6', '#14b8a6', '#f97316',
];

/** Group rows by currency: { ARS: [{ account_name, amount }], USD: [...] } */
function groupByCurrency(rows) {
  const byCurrency = {};
  for (const row of rows) {
    if (!byCurrency[row.currency]) byCurrency[row.currency] = {};
    byCurrency[row.currency][row.account_name] =
      (byCurrency[row.currency][row.account_name] || 0) + row.amount;
  }
  return Object.entries(byCurrency).map(([currency, amounts]) => ({
    currency,
    segments: Object.entries(amounts)
      .filter(([, amt]) => amt > 0)
      .sort((a, b) => b[1] - a[1])
      .map(([name, amount], i) => ({
        name,
        amount,
        color: PIE_COLORS[i % PIE_COLORS.length],
      })),
  })).filter((c) => c.segments.length > 0);
}

function PieChart({ currency, segments }) {
  const total = segments.reduce((s, seg) => s + seg.amount, 0);
  let deg = 0;
  const conicParts = segments.map((seg) => {
    const pct = (seg.amount / total) * 360;
    const part = `${seg.color} ${deg}deg ${deg + pct}deg`;
    deg += pct;
    return part;
  }).join(', ');

  return (
    <div className="pie-chart-card">
      <h4 className="pie-chart-title">
        {CURRENCY_PREFIX[currency] || currency} {formatAmount(total)}
      </h4>
      <div className="pie-chart-wrap">
        <div
          className="pie-chart"
          style={{ background: `conic-gradient(${conicParts})` }}
        />
        <div className="pie-chart-hole" />
      </div>
      <ul className="pie-chart-legend">
        {segments.map((seg) => (
          <li key={seg.name}>
            <span className="legend-dot" style={{ background: seg.color }} />
            <span className="legend-label">{seg.name}</span>
            <span className="legend-value">{formatAmountWithCurrency(seg.amount, currency)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ExpenseChart({ rows }) {
  const byCurrency = groupByCurrency(rows);
  if (byCurrency.length === 0) return null;

  return (
    <div className="report-chart report-pie-charts">
      {byCurrency.map(({ currency, segments }) => (
        <PieChart key={currency} currency={currency} segments={segments} />
      ))}
    </div>
  );
}
