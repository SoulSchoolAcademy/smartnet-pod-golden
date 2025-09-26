# SmartLedger (v3_1)

## Quick start
```bash
# in this folder
docker compose down -v --remove-orphans
docker compose up -d --build
docker compose logs -f smartledger
```

## Test
```bash
curl http://localhost:4000/health
curl -s -X POST http://localhost:4000/api/truth/register   -H "Content-Type: application/json"   -d '{"contentId":"demo:content:1","content":{"hello":"world"}}'

curl -s "http://localhost:4000/api/truth/verify?contentId=demo:content:1"
```
