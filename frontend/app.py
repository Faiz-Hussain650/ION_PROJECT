from flask import Flask
import psycopg2
import os

# Database connection parameters from environment
DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')

# Connect and fetch name
conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT,
    dbname=DB_NAME, user=DB_USER, password=DB_PASS
)
cursor = conn.cursor()
cursor.execute("SELECT name FROM users LIMIT 1;")
name = cursor.fetchone()[0]

app = Flask(__name__)

@app.route('/')
def hello():
    return f"hello world, {name}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)