// SmartNet-web/app/api/truth/register/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const base = process.env.LEDGER_BASE_URL || 'http://localhost:4000';
  const url = `${base}/api/truth/register`;
  const idk = req.headers.get('idempotency-key') || undefined;
  const body = await req.json();
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(idk ? {'Idempotency-Key': idk} : {}) },
    body: JSON.stringify(body),
    cache: 'no-store',
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
