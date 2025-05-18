from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

load_dotenv()
DBNAME   = os.getenv("PG_DBNAME")
USER     = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASSWORD")
HOST     = os.getenv("PG_HOST")
PORT     = os.getenv("PG_PORT")

conn = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

query = "SELECT * FROM predictions where id=189;"
df = pd.read_sql(query, conn)
print(df)
conn.close()

