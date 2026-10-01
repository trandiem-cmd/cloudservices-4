from flask import Flask, jsonify, request
import os
import time
import json
import mysql.connector
import redis

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'appdb')
REDIS_HOST = os.getenv('REDIS_HOST', 'cache')

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "cache"),
    port=6379,
    decode_responses=True
)


@app.after_request
def log_request(response):
    duration = (time.time() - request.start_time) * 1000

    log_data = {
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "responseTimeMs": round(duration, 2)
    }

    print(json.dumps(log_data), flush=True)

    return response


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api')
def index():
    """Simple endpoint that greets from DB."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

    cur = conn.cursor()
    cur.execute("SELECT 'Hello from MySQL via Flask!'")
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(message=row[0])


@app.get('/api/time')
def mysql_time():
    """Return the current MySQL server time."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

    cur = conn.cursor()
    cur.execute("SELECT NOW()")
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(mysql_time=str(row[0]))


@app.post('/api/views')
def add_view():
    """Increment the persistent page-view counter."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

    cur = conn.cursor()

    cur.execute(
        "UPDATE page_views SET views = views + 1 WHERE id = 1"
    )

    conn.commit()

    cur.execute(
        "SELECT views FROM page_views WHERE id = 1"
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(views=row[0])


@app.get('/api/view')
def view():
    count = r.incr('view_count')
    return jsonify(view=count)


@app.get('/api/views')
def get_views():
    """Return the current page-view counter."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

    cur = conn.cursor()
    cur.execute(
        "SELECT views FROM page_views WHERE id = 1"
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(views=row[0])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)