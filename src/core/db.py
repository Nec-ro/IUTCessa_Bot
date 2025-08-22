import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)

# example usage:
# with get_conn() as conn, conn.cursor() as cur:
#     cur.execute("SELECT 1")
#     print(cur.fetchone())