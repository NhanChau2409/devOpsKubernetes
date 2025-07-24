import uuid
import os
import psycopg2
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pingpong")
DB_USER = os.getenv("DB_USER", "pingpong_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "pingpong_password")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def init_database():
    """Initialize database table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ping_counter (
                id SERIAL PRIMARY KEY,
                counter INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert initial record if table is empty
        cursor.execute("SELECT COUNT(*) FROM ping_counter")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO ping_counter (counter) VALUES (0)")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


def get_counter():
    """Get current counter value from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT counter FROM ping_counter ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting counter: {e}")
        return 0


def increment_counter():
    """Increment counter in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ping_counter SET counter = counter + 1, updated_at = CURRENT_TIMESTAMP WHERE id = (SELECT id FROM ping_counter ORDER BY id DESC LIMIT 1)"
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error incrementing counter: {e}")


@app.route("/", methods=["GET"])
def pingpong():
    """Main ping-pong endpoint - now on root path"""
    increment_counter()
    ping_counter = get_counter()
    timestamp = datetime.utcnow().isoformat() + "Z"
    random_string = str(uuid.uuid4())
    response = f"pong {ping_counter}"
    print(f"{timestamp}: {ping_counter}: {random_string}")
    return response, 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    ping_counter = get_counter()
    return {
        "service": "pingpong",
        "status": "healthy",
        "current_pings": ping_counter,
        "message": "Ping-pong service is running. Use / to increment counter.",
    }, 200


@app.route("/pings", methods=["GET"])
def get_pings():
    """Return the current ping count without incrementing"""
    ping_counter = get_counter()
    return {"pings": ping_counter}, 200


if __name__ == "__main__":
    # Initialize database on startup
    init_database()
    app.run(host="0.0.0.0", port=8080)
