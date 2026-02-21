# Ledger — React frontend

React app for the Ledger (transfers & splits), built with Vite.

## Structure

- `src/api/client.js` — API client (accounts, reports, transactions)
- `src/contexts/` — `AccountsContext`, `ToastContext`
- `src/components/`
  - `Layout.jsx` — layout + panel routing
  - `Sidebar.jsx`, `NavButton.jsx` — navigation
  - `ui/` — `FormRow`, `Select`, `Button`, `FriendRows`
  - `panels/` — `Reports`, `Transactions`, `DescriptionTags`
  - `report/` — `ExpenseTable`, `ExpenseChart`

## Run

1. Start the API (from repo root):
   ```bash
   PYTHONPATH=. uvicorn accounting.rest_api.app:app --reload --port 8000
   ```

2. From this directory:
   ```bash
   npm run dev
   ```
   Open http://localhost:5173 . Vite proxies `/api` to the backend.

## Build

```bash
npm run build
```
Output is in `dist/`. Serve it with the API or any static server.
