import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [message, setMessage] = useState(null);
  const [variant, setVariant] = useState('success');

  const show = useCallback((msg, type = 'success') => {
    setMessage(msg);
    setVariant(type);
  }, []);

  const hide = useCallback(() => {
    setMessage(null);
  }, []);

  useEffect(() => {
    if (!message) return;
    const t = setTimeout(hide, 3500);
    return () => clearTimeout(t);
  }, [message, hide]);

  return (
    <ToastContext.Provider value={{ show, hide }}>
      {children}
      {message && (
        <div className={`toast ${variant}`} role="alert" aria-live="polite">
          {message}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
