export function NavButton({ active, onClick, children }) {
  return (
    <button
      type="button"
      className={`nav-btn ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
