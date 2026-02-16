export function formatAmount(n) {
  return Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

const CURRENCY_PREFIX = { ARS: '$', USD: 'U$S', EUR: '€' };

export function formatAmountWithCurrency(amount, currency, { signed = false } = {}) {
  const n = typeof amount === 'number' ? amount : parseFloat(amount);
  const prefix = CURRENCY_PREFIX[currency] || `${currency} `;
  const sign = signed ? (n >= 0 ? '+' : '-') : '';
  return `${prefix} ${sign}${formatAmount(Math.abs(n))}`;
}

export function formatAmountsByCurrency(amountsByCurrency, { signed = false } = {}) {
  return Object.entries(amountsByCurrency)
    .filter(([, amt]) => amt !== 0)
    .map(([curr, amt]) => formatAmountWithCurrency(amt, curr, { signed }))
    .join(' + ');
}
