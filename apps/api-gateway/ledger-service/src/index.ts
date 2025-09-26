import { connect, StringCodec } from "nats";
import { Client } from "pg";
import pino from "pino";

const log = pino({ level: process.env.LOG_LEVEL || "info" });
const NATS_URL = process.env.NATS_URL || "nats://nats:4222";
const DATABASE_URL = process.env.DATABASE_URL || "postgres://postgres:postgres@app-db:5432/postgres";

async function ensureSchema(db: Client) {
  await db.query(`
    CREATE TABLE IF NOT EXISTS ledger_entries (
      id UUID PRIMARY KEY,
      account_id UUID NOT NULL,
      amount NUMERIC(20,8) NOT NULL,
      kind TEXT NOT NULL CHECK (kind IN ('credit','debit')),
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS outbox_events (
      id UUID PRIMARY KEY,
      aggregate_id UUID NOT NULL,
      topic TEXT NOT NULL,
      payload JSONB NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      published_at TIMESTAMPTZ
    );
  `);
}

async function run() {
  const db = new Client({ connectionString: DATABASE_URL });
  await db.connect();
  await ensureSchema(db);

  const nc = await connect({ servers: NATS_URL });
  const sc = StringCodec();

  // Consumers for credit/debit events
  const makeHandler = (kind: "credit" | "debit") => async (data: any) => {
    const { id, accountId, amount } = data;
    await db.query("INSERT INTO ledger_entries(id,account_id,amount,kind) VALUES ($1,$2,$3,$4) ON CONFLICT DO NOTHING",
      [id, accountId, amount, kind]);
    log.info({ id, accountId, amount, kind }, "ledger entry recorded");
  };

  (async () => {
    const s1 = nc.subscribe("ledger.credit.v1");
    for await (const m of s1) {
      const data = JSON.parse(sc.decode(m.data) || "{}");
      await makeHandler("credit")(data);
    }
  })().catch(err => log.error({ err }, "credit sub error"));

  (async () => {
    const s2 = nc.subscribe("ledger.debit.v1");
    for await (const m of s2) {
      const data = JSON.parse(sc.decode(m.data) || "{}");
      await makeHandler("debit")(data);
    }
  })().catch(err => log.error({ err }, "debit sub error"));

  log.info("ledger-service up");
}

run().catch(err => { console.error(err); process.exit(1); });
