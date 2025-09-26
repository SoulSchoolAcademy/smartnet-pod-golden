import { Pool } from "pg";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  console.error("DATABASE_URL not set");
  process.exit(1);
}

// Allow SSL when hosted DBs (e.g., Supabase) set PGSSLMODE=require
const ssl = process.env.PGSSLMODE === "require" ? { rejectUnauthorized: false } : undefined;

const pool = new Pool({ connectionString, ssl });

export async function register(contentId: string, content: any) {
  const sql = `
    INSERT INTO truths (content_id, content)
    VALUES ($1, $2::jsonb)
    ON CONFLICT (content_id) DO UPDATE SET content = EXCLUDED.content
    RETURNING *;
  `;
  const { rows } = await pool.query(sql, [contentId, JSON.stringify(content ?? {})]);
  return rows[0];
}

export async function verify(contentId: string) {
  const { rows } = await pool.query("SELECT * FROM truths WHERE content_id = $1", [contentId]);
  return { exists: rows.length > 0, record: rows[0] ?? null };
}
