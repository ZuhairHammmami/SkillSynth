'use client';

import { useEffect } from 'react';
import arMessages from '@/i18n/messages/ar.json';
import enMessages from '@/i18n/messages/en.json';

interface ErrorMessages {
  title: string;
  description: string;
  retry: string;
}

function pickErrorMessages(): ErrorMessages {
  const lang = typeof document !== 'undefined' ? document.documentElement.lang : 'en';
  const messages = lang === 'ar' ? arMessages : enMessages;
  return (messages as { error: ErrorMessages }).error;
}

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  const t = pickErrorMessages();

  return (
    <html lang={typeof document !== 'undefined' ? document.documentElement.lang || 'en' : 'en'}>
      <body
        style={{
          margin: 0,
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '16px',
          padding: '16px',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          color: '#09090b',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '9999px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f4f4f5',
            fontSize: '22px',
          }}
        >
          !
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 600, margin: 0 }}>{t.title}</h1>
          <p style={{ fontSize: '14px', color: '#71717a', maxWidth: '28rem', margin: 0 }}>
            {t.description}
          </p>
        </div>
        <button
          type="button"
          onClick={reset}
          style={{
            border: '1px solid #e4e4e7',
            borderRadius: '8px',
            padding: '8px 16px',
            fontSize: '14px',
            fontWeight: 500,
            backgroundColor: '#18181b',
            color: '#fafafa',
            cursor: 'pointer',
          }}
        >
          {t.retry}
        </button>
      </body>
    </html>
  );
}
