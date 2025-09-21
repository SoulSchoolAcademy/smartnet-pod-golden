# repo: smartnet-pod-golden
# path: 30-services/smartmail-api/app/db_init.py
import os, psycopg, uuid
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/smartnet")
with psycopg.connect(DATABASE_URL, autocommit=True) as c, c.cursor() as cur:
    for u in ["naya","alice","bob","carol","dave"]:
        cur.execute("insert into users(id, username, email) values (%s,%s,%s) on conflict (username) do nothing;",
                    (uuid.uuid4(), u, f"{u}@example.com"))
    print("Seeded users: naya, alice, bob, carol, dave")
