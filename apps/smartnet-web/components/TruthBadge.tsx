// SmartNet-web/components/TruthBadge.tsx
'use client';
import React from 'react';

export default function TruthBadge({ hash }: { hash: string }) {
  const origin = process.env.NEXT_PUBLIC_SITE_ORIGIN || '';
  const href = `/verify/${hash}`;
  return (
    <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full border px-3 py-1">
      <svg width="18" height="18" viewBox="0 0 120 120"><circle cx="60" cy="60" r="56" fill="currentColor"/><path d="M36 62l12 12 32-32" stroke="#fff" strokeWidth="12" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
      <span>SmartLedger • Verified</span>
    </a>
  );
}
