const http = require("http");
const PORT = process.env.PORT || 3101;
const NATS_URL = process.env.NATS_URL || "nats://nats:4222";

const server = http.createServer((req, res) => {
  res.writeHead(200, {"Content-Type":"application/json"});
  res.end(JSON.stringify({service:"api-gateway", ok:true, nats:NATS_URL}));
});

server.listen(PORT, () => {
  console.log(`[api-gateway] listening on ${PORT}`);
});
