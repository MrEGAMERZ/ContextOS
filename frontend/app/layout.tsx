import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ContextOS — Caregiver Trust Dashboard & Alexa+ Voice Harness',
  description: 'Ambient Contextual Intelligence Platform for Independent Living',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
