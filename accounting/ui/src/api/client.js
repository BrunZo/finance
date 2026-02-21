const API_BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg || JSON.stringify(d)).join(' ')
      : data.detail || res.statusText;
    throw new Error(msg);
  }
  return data;
}

export async function getAccounts() {
  return request('/accounts');
}

export async function postAccount(body) {
  return request('/accounts', { method: 'POST', body: JSON.stringify(body) });
}

export async function patchAccount(accountId, body) {
  return request(`/accounts/${accountId}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

export async function deleteAccount(accountId) {
  return request(`/accounts/${accountId}`, { method: 'DELETE' });
}

export async function getExpensesReport() {
  return request('/reports/expenses');
}

export async function getExpensesTreeReport() {
  return request('/reports/expenses-tree');
}

export async function getTransactions() {
  return request('/transactions');
}

export async function getUncategorizedTransactions() {
  return request('/transactions/uncategorized');
}

export async function patchSplit(splitId, body) {
  return request(`/transactions/splits/${splitId}`, { method: 'PATCH', body: JSON.stringify(body) });
}

export async function getDescriptionTagMappings() {
  return request('/description-tags');
}

export async function postDescriptionTagMapping(body) {
  return request('/description-tags', { method: 'POST', body: JSON.stringify(body) });
}

export async function patchDescriptionTagMapping(mappingId, body) {
  return request(`/description-tags/${mappingId}`, { method: 'PATCH', body: JSON.stringify(body) });
}

export async function deleteDescriptionTagMapping(mappingId) {
  return request(`/description-tags/${mappingId}`, { method: 'DELETE' });
}

