# SmartNet-web — SmartLedger Integration

Drop these files into your Next.js app (App Router).

## Setup
1) Copy `.env.local.example` → `.env.local` and set `LEDGER_BASE_URL` to your SmartLedger service.
2) Keep `next.config.mjs` rewrites to forward `/truth/*` and `/verify/*` to the ledger.
3) Use `<TruthBadge hash={txId} />` anywhere you want to show the verified badge.
