import express from "express";
import cors from "cors";
import { register, verify } from "./services/db";

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.status(200).send("ok"));

app.post("/api/truth/register", async (req, res) => {
  try {
    const { contentId, content } = req.body ?? {};
    if (!contentId) return res.status(400).json({ error: "contentId required" });
    const record = await register(String(contentId), content ?? {});
    return res.json({ ok: true, record });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: "db_error" });
  }
});

app.get("/api/truth/verify", async (req, res) => {
  try {
    const contentId = String(req.query.contentId ?? "");
    if (!contentId) return res.status(400).json({ error: "contentId required" });
    const { exists, record } = await verify(contentId);
    return res.json({ exists, record });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: "db_error" });
  }
});

const port = Number(process.env.PORT ?? 4000);
const host = String(process.env.HOST ?? "0.0.0.0");

app.listen(port, host, () => {
  console.log(`smartledger listening on http://${host}:${port}`);
});
