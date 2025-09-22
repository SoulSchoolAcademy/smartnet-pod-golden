import Fastify from "fastify";
import pino from "pino";
import { NativeConnection, Worker } from "@temporalio/worker";
import { connect, StringCodec } from "nats";

const PORT = Number(process.env.PORT || 8765);
const NATS_URL = process.env.NATS_URL || "nats://nats:4222";
const TEMPORAL_ADDRESS = process.env.TEMPORAL_ADDRESS || "temporal:7233";

async function main() {
  const log = pino({ level: process.env.LOG_LEVEL || "info" });

  const temporal = await NativeConnection.connect({ address: TEMPORAL_ADDRESS });
  const worker = await Worker.create({
    connection: temporal,
    workflowsPath: require.resolve("./workflows/signup"),
    taskQueue: "smartnet-orchestrator"
  });
  worker.run().catch((err) => log.error({ err }, "temporal worker crashed"));

  const nc = await connect({ servers: NATS_URL });
  const sc = StringCodec();

  const app = Fastify({ logger: log });
  app.get("/health", async () => ({ ok: true }));
  app.post("/demo/signup", async (_req, reply) => {
    nc.publish("user.signup.v1", sc.encode(JSON.stringify({ ts: Date.now() })));
    reply.code(202).send({ accepted: true });
  });

  await app.listen({ port: PORT, host: "0.0.0.0" });
  log.info({ PORT, NATS_URL, TEMPORAL_ADDRESS }, "orchestrator up");
}

main().catch((e) => { console.error(e); process.exit(1); });
