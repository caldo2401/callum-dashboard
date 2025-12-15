import json
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data/app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
SEED_PATH = BASE_DIR / "seed/seed_data.json"

seeded_on_boot = False

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_seed_data():
    if not SEED_PATH.exists():
        return {}

    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def apply_seed(conn, seed_data):
    global seeded_on_boot
    inserted_any = False
    inserted_weeds = 0
    cur = conn.cursor()

    for entry in seed_data.get("weed_entries", []):
        cur.execute(
            """
            INSERT INTO weed_entries (date, strain_name, thc_percent, strain_type, terpenes, notes, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.get("date") or datetime.now().date().isoformat(),
                entry.get("strain_name", "").strip(),
                entry.get("thc_percent"),
                entry.get("strain_type", "").strip(),
                entry.get("terpenes", "").strip(),
                entry.get("notes", "").strip(),
                entry.get("rating"),
            ),
        )
        inserted_any = True
        inserted_weeds += 1

    for rec in seed_data.get("recommendations", []):
        cur.execute(
            "INSERT INTO recommendations (content) VALUES (?)",
            (str(rec).strip(),),
        )
        inserted_any = True

    for game in seed_data.get("games", []):
        cur.execute(
            "INSERT INTO games (title, category) VALUES (?, ?)",
            (game.get("title", "").strip(), game.get("category", "Finish")),
        )
        inserted_any = True

    for media in seed_data.get("media", []):
        cur.execute(
            "INSERT INTO media (title, category) VALUES (?, ?)",
            (media.get("title", "").strip(), media.get("category", "docs")),
        )
        inserted_any = True

    pc_data = seed_data.get("pc_setup")
    if pc_data:
        cur.execute("SELECT COUNT(*) as count FROM pc_setup")
        if cur.fetchone()["count"] == 0:
            cur.execute(
                """
                INSERT INTO pc_setup (id, cpu, gpu, monitors, psu, storage)
                VALUES (1, ?, ?, ?, ?, ?)
                """,
                (
                    pc_data.get("cpu", "").strip(),
                    pc_data.get("gpu", "").strip(),
                    pc_data.get("monitors", "").strip(),
                    pc_data.get("psu", "").strip(),
                    pc_data.get("storage", "").strip(),
                ),
            )
            inserted_any = True

    if inserted_any:
        conn.commit()
        seeded_on_boot = True

    return inserted_weeds


def ensure_pc_defaults(conn, seed_data):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM pc_setup")
    if cur.fetchone()["count"] == 0:
        pc_data = seed_data.get("pc_setup") or {
            "cpu": "Ryzen 7800X3D",
            "gpu": "RTX 3070",
            "monitors": "1080p 140Hz; 1080p 240Hz; 1440p 165Hz (main)",
            "psu": "Corsair ~1000W (E-series, TBC) — Case: Corsair (TBC)",
            "storage": "2× NVMe M.2, 2× SATA SSD",
        }
        cur.execute(
            """
            INSERT INTO pc_setup (id, cpu, gpu, monitors, psu, storage)
            VALUES (1, ?, ?, ?, ?, ?)
            """,
            (
                pc_data.get("cpu", "").strip(),
                pc_data.get("gpu", "").strip(),
                pc_data.get("monitors", "").strip(),
                pc_data.get("psu", "").strip(),
                pc_data.get("storage", "").strip(),
            ),
        )
        conn.commit()


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weed_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            strain_name TEXT NOT NULL,
            thc_percent REAL,
            strain_type TEXT,
            terpenes TEXT,
            notes TEXT,
            rating INTEGER
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pc_setup (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            cpu TEXT,
            gpu TEXT,
            monitors TEXT,
            psu TEXT,
            storage TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL
        )
        """
    )
    conn.commit()

    seed_data = load_seed_data()
    cur.execute("SELECT COUNT(*) as count FROM weed_entries")
    weed_count = cur.fetchone()["count"]
    if weed_count == 0:
        print("Seeding starter data…")
        inserted_weeds = apply_seed(conn, seed_data)
        print(f"Seed complete: inserted {inserted_weeds} weed entries")
    else:
        print(f"Seed skipped: weed_entries already populated ({weed_count} rows)")

    ensure_pc_defaults(conn, seed_data)
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/seed-status")
def seed_status():
    return jsonify({"seeded": seeded_on_boot})


@app.route("/api/weed", methods=["GET", "POST"])
def weed_entries():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.json
        cur.execute(
            """
            INSERT INTO weed_entries (date, strain_name, thc_percent, strain_type, terpenes, notes, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("date") or datetime.now().date().isoformat(),
                data.get("strain_name", "").strip(),
                data.get("thc_percent"),
                data.get("strain_type", "").strip(),
                data.get("terpenes", "").strip(),
                data.get("notes", "").strip(),
                data.get("rating"),
            ),
        )
        conn.commit()
    cur.execute("SELECT * FROM weed_entries ORDER BY date DESC, id DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/weed/<int:entry_id>", methods=["PUT", "DELETE"])
def weed_entry_detail(entry_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "PUT":
        data = request.json
        cur.execute(
            """
            UPDATE weed_entries
            SET date = ?, strain_name = ?, thc_percent = ?, strain_type = ?, terpenes = ?, notes = ?, rating = ?
            WHERE id = ?
            """,
            (
                data.get("date") or datetime.now().date().isoformat(),
                data.get("strain_name", "").strip(),
                data.get("thc_percent"),
                data.get("strain_type", "").strip(),
                data.get("terpenes", "").strip(),
                data.get("notes", "").strip(),
                data.get("rating"),
                entry_id,
            ),
        )
        conn.commit()
    elif request.method == "DELETE":
        cur.execute("DELETE FROM weed_entries WHERE id = ?", (entry_id,))
        conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/weed/stats")
def weed_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM weed_entries ORDER BY date DESC, id DESC LIMIT 2")
    recent = [dict(row) for row in cur.fetchall()]

    cur.execute(
        "SELECT strain_name, COUNT(*) as count FROM weed_entries GROUP BY strain_name ORDER BY count DESC"
    )
    counts = [dict(row) for row in cur.fetchall()]

    conn.close()
    return jsonify({"recent": recent, "counts": counts})


@app.route("/api/recommendations", methods=["GET", "POST"])
def recommendations():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO recommendations (content) VALUES (?)",
            (data.get("content", "").strip(),),
        )
        conn.commit()
    cur.execute("SELECT * FROM recommendations ORDER BY id DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/recommendations/<int:item_id>", methods=["DELETE"])
def delete_recommendation(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recommendations WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/pc", methods=["GET", "PUT"])
def pc_setup():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "PUT":
        data = request.json
        cur.execute(
            """
            UPDATE pc_setup
            SET cpu = ?, gpu = ?, monitors = ?, psu = ?, storage = ?
            WHERE id = 1
            """,
            (
                data.get("cpu", "").strip(),
                data.get("gpu", "").strip(),
                data.get("monitors", "").strip(),
                data.get("psu", "").strip(),
                data.get("storage", "").strip(),
            ),
        )
        conn.commit()
    cur.execute("SELECT * FROM pc_setup WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return jsonify(dict(row) if row else {})


@app.route("/api/games", methods=["GET", "POST"])
def games():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO games (title, category) VALUES (?, ?)",
            (data.get("title", "").strip(), data.get("category", "Finish")),
        )
        conn.commit()
    cur.execute("SELECT * FROM games ORDER BY id DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/games/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/media", methods=["GET", "POST"])
def media():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO media (title, category) VALUES (?, ?)",
            (data.get("title", "").strip(), data.get("category", "docs")),
        )
        conn.commit()
    cur.execute("SELECT * FROM media ORDER BY id DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/media/<int:media_id>", methods=["DELETE"])
def delete_media(media_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM media WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
