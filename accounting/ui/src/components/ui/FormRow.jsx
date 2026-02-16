export function FormRow({ label, children, className = '' }) {
  return (
    <div className={`form-row ${className}`}>
      {label && <label>{label}</label>}
      {children}
    </div>
  );
}
