import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to default postgres database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="1234",  # Updated password
    host="localhost",
    port="5433"
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Create database if it doesn't exist
cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'agnodb'")
exists = cursor.fetchone()
if not exists:
    cursor.execute("CREATE DATABASE agnodb")
    print("Database 'agnodb' created successfully")
else:
    print("Database 'agnodb' already exists")

cursor.close()
conn.close()

print("Database setup complete")
print("Now run: uvicorn app.main:app --reload")