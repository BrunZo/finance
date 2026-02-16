export function Select({ options, value, onChange, placeholder = '— Select —', ...props }) {
  return (
    <select value={value ?? ''} onChange={(e) => onChange?.(e.target.value)} {...props}>
      <option value="">{placeholder}</option>
      {options.map((opt) => (
        <option key={opt.id} value={opt.id}>
          {opt.name}
        </option>
      ))}
    </select>
  );
}
