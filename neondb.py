import os
from psycopg2 import pool
from dotenv import load_dotenv

# Load env locally (optional for dev)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Initialize connection pool
db_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def get_connection():
    return db_pool.getconn()

def release_connection(conn):
    db_pool.putconn(conn)

# ✅ Create the enquiries table if not exists
def create_enquiry_table():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enquiries (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone_number TEXT,
                    message TEXT,
                    submitted_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            conn.commit()
        print("✅ enquiries table created.")
    finally:
        release_connection(conn)

# ✅ Insert a new enquiry
def insert_enquiry(name: str, email: str, phone: str, message: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO enquiries (name, email, phone_number, message)
                VALUES (%s, %s, %s, %s);
            """, (name, email, phone, message))
            conn.commit()
    finally:
        release_connection(conn)
