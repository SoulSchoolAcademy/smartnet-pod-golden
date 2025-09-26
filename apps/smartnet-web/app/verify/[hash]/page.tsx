// SmartNet-web/app/verify/[hash]/page.tsx
import { manifestByHash } from '@/lib/ledger';
import React from 'react';

export default async function Page({ params }: { params: { hash: string } }) {
  const manifest = await manifestByHash(params.hash).catch(() => null);
  if (!manifest) return <div className="p-8">Not found</div>;
  return (
    <div className="max-w-3xl mx-auto p-8">
      <h1 className="text-2xl font-semibold">Verification</h1>
      <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
        <div><div className="opacity-70">Content ID</div><div className="font-mono">{manifest.contentId}</div></div>
        <div><div className="opacity-70">Creator DID</div><div className="font-mono">{manifest.creatorDid}</div></div>
        <div><div className="opacity-70">Media Type</div><div>{manifest.mediaType}</div></div>
        <div><div className="opacity-70">Created</div><div className="font-mono">{manifest.createdAtISO}</div></div>
        <div className="col-span-2"><div className="opacity-70">Current Hash</div><div className="font-mono">{manifest.chain?.currHash}</div></div>
      </div>
    </div>
  );
}
