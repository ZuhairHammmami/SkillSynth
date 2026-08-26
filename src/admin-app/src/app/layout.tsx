import type { Metadata } from 'next';
import { Providers } from './providers';
import { Toaster } from 'sonner';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'SkillSynth Admin',
  description: 'Admin panel for SkillSynth — Adaptive Learning OS',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <Providers>{children}</Providers>
        <Toaster position="top-center" closeButton />
      </body>
    </html>
  );
}
