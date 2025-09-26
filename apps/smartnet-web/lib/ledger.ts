export const LEDGER = process.env.LEDGER_BASE_URL || 'http://localhost:4000';

export async function registerTruth(payload: any, idempotencyKey?: string) {
  const res = await fetch(`${LEDGER}/api/truth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {})
    },
    body: JSON.stringify(payload),
    cache: 'no-store'
  });
  if (!res.ok) throw new Error(`Ledger register failed: ${res.status}`);
  return res.json();
}

export async function verifyByContentId(contentId: string) {
  const res = await fetch(`${LEDGER}/api/truth/verify?contentId=${encodeURIComponent(contentId)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Ledger verify failed: ${res.status}`);
  return res.json();
}

export async function manifestByHash(hash: string) {
  const res = await fetch(`${LEDGER}/api/truth/manifest?hash=${encodeURIComponent(hash)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Ledger manifest failed: ${res.status}`);
  return res.json();
}
