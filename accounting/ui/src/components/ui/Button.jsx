export function Button({ variant = 'primary', children, className = '', ...props }) {
  return (
    <button type="button" className={`btn btn-${variant} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function SubmitButton({ children, ...props }) {
  return (
    <button type="submit" className="btn btn-primary" {...props}>
      {children}
    </button>
  );
}
