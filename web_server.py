"""
Fantasy World Newspaper – a lightweight Flask web server that serves the latest
event as a fantasy newspaper tabloid page.
"""

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Optional, List

from flask import Flask, render_template, send_from_directory, jsonify, abort

_SCRIPT_DIR = Path(__file__).parent

app = Flask(
    __name__,
    template_folder=str(_SCRIPT_DIR / "templates"),
    static_folder=str(_SCRIPT_DIR / "static"),
)

# Will be set by start_web_server()
_db_path: str = ""
_world_name: str = ""
_images_dir: str = ""


def _get_latest_event() -> Optional[dict]:
    """Fetch the most recent event from the database, including its details."""
    if not _db_path or not Path(_db_path).exists():
        return None

    try:
        conn = sqlite3.connect(_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT e.id, e.timestamp, e.category, e.event_text, e.headline,
                   e.location, e.characters, e.factions, e.image_path,
                   d.hidden_details, d.connections, d.plot_hooks, d.consequences
            FROM events e
            LEFT JOIN event_details d ON d.event_id = e.id
            ORDER BY e.id DESC
            LIMIT 1
        """)
        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        # Grab world time from latest world_state
        cur.execute("SELECT state_json FROM world_state ORDER BY id DESC LIMIT 1")
        ws_row = cur.fetchone()
        world_time = {}
        if ws_row:
            try:
                ws = json.loads(ws_row["state_json"])
                world_time = ws.get("time", {})
            except (json.JSONDecodeError, KeyError):
                pass

        conn.close()

        # Parse characters JSON
        chars = []
        try:
            chars = json.loads(row["characters"]) if row["characters"] else []
        except (json.JSONDecodeError, TypeError):
            pass

        # Resolve image path to a URL-friendly relative path
        image_url = None
        img = row["image_path"]
        if img and Path(img).exists():
            image_url = "/event_image/" + Path(img).name

        # Build clean headline and body (strip the "[timestamp] Event #N (Category):" header line)
        raw_lines = [l for l in (row["event_text"] or "").split("\n") if l.strip()]
        body_lines = [l for l in raw_lines if not l.startswith("[")]
        body_text = "\n".join(body_lines)
        db_headline = (row["headline"] or "").strip()
        if db_headline:
            display_headline = db_headline
        elif body_lines:
            first = body_lines[0]
            display_headline = first if len(first) <= 120 else first[:117] + "..."
        else:
            display_headline = f"Breaking news from {row['location'] or 'the Realm'}"

        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "category": row["category"],
            "event_text": row["event_text"],
            "headline": display_headline,
            "body_text": body_text,
            "location": row["location"] or "Unknown",
            "characters": chars,
            "image_url": image_url,
            "hidden_details": row["hidden_details"] or "",
            "connections": row["connections"] or "",
            "plot_hooks": row["plot_hooks"] or "",
            "consequences": row["consequences"] or "",
            "world_time": world_time,
        }
    except Exception as e:
        print(f"[web_server] Error fetching latest event: {e}")
        return None


def _get_recent_events(count: int = 10) -> List[dict]:
    """Fetch the N most recent events (summary only) for the sidebar."""
    if not _db_path or not Path(_db_path).exists():
        return []
    try:
        conn = sqlite3.connect(_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.timestamp, e.category, e.event_text, e.headline,
                   e.location, e.image_path,
                   d.hidden_details
            FROM events e
            LEFT JOIN event_details d ON d.event_id = e.id
            ORDER BY e.id DESC
            LIMIT ?
        """, (count,))
        rows = cur.fetchall()
        conn.close()

        events = []
        for r in rows:
            img = r["image_path"]
            image_url = None
            if img and Path(img).exists():
                image_url = "/event_image/" + Path(img).name
            raw_lines = [l for l in (r["event_text"] or "").split("\n") if l.strip()]
            body_lines = [l for l in raw_lines if not l.startswith("[")]
            db_hl = (r["headline"] or "").strip()
            if db_hl:
                hl = db_hl
            elif body_lines:
                first = body_lines[0]
                hl = first if len(first) <= 80 else first[:77] + "..."
            else:
                hl = r["category"].capitalize() + " event"
            events.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "category": r["category"],
                "event_text": r["event_text"],
                "headline": hl,
                "location": r["location"] or "Unknown",
                "image_url": image_url,
            })
        return events
    except Exception as e:
        print(f"[web_server] Error fetching recent events: {e}")
        return []


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    event = _get_latest_event()
    recent = _get_recent_events(10)
    return render_template(
        "newspaper.html",
        event=event,
        recent=recent,
        world_name=_world_name,
    )


@app.route("/api/latest")
def api_latest():
    event = _get_latest_event()
    if not event:
        return jsonify({"error": "No events yet"}), 404
    return jsonify(event)


@app.route("/event/<int:event_id>")
def event_page(event_id: int):
    """Show a specific event by ID."""
    if not _db_path or not Path(_db_path).exists():
        abort(404)
    try:
        conn = sqlite3.connect(_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.timestamp, e.category, e.event_text, e.headline,
                   e.location, e.characters, e.factions, e.image_path,
                   d.hidden_details, d.connections, d.plot_hooks, d.consequences
            FROM events e
            LEFT JOIN event_details d ON d.event_id = e.id
            WHERE e.id = ?
        """, (event_id,))
        row = cur.fetchone()

        # World time
        cur.execute("SELECT state_json FROM world_state ORDER BY id DESC LIMIT 1")
        ws_row = cur.fetchone()
        world_time = {}
        if ws_row:
            try:
                ws = json.loads(ws_row["state_json"])
                world_time = ws.get("time", {})
            except (json.JSONDecodeError, KeyError):
                pass

        conn.close()

        if not row:
            abort(404)

        chars = []
        try:
            chars = json.loads(row["characters"]) if row["characters"] else []
        except (json.JSONDecodeError, TypeError):
            pass

        image_url = None
        img = row["image_path"]
        if img and Path(img).exists():
            image_url = "/event_image/" + Path(img).name

        raw_lines = [l for l in (row["event_text"] or "").split("\n") if l.strip()]
        body_lines = [l for l in raw_lines if not l.startswith("[")]
        body_text = "\n".join(body_lines)
        db_headline = (row["headline"] or "").strip()
        if db_headline:
            display_headline = db_headline
        elif body_lines:
            first = body_lines[0]
            display_headline = first if len(first) <= 120 else first[:117] + "..."
        else:
            display_headline = f"Breaking news from {row['location'] or 'the Realm'}"

        event = {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "category": row["category"],
            "event_text": row["event_text"],
            "headline": display_headline,
            "body_text": body_text,
            "location": row["location"] or "Unknown",
            "characters": chars,
            "image_url": image_url,
            "hidden_details": row["hidden_details"] or "",
            "connections": row["connections"] or "",
            "plot_hooks": row["plot_hooks"] or "",
            "consequences": row["consequences"] or "",
            "world_time": world_time,
        }
    except Exception:
        abort(404)

    recent = _get_recent_events(10)
    return render_template(
        "newspaper.html",
        event=event,
        recent=recent,
        world_name=_world_name,
    )


@app.route("/event_image/<path:filename>")
def event_image(filename: str):
    """Serve event images from the world images directory."""
    if not _images_dir or not Path(_images_dir).exists():
        abort(404)
    return send_from_directory(_images_dir, filename)


# ── Server lifecycle ──────────────────────────────────────────────────────────

def start_web_server(db_path: str, world_name: str, images_dir: str,
                     host: str = "0.0.0.0", port: int = 5000) -> threading.Thread:
    """Start the Flask web server in a daemon thread.

    Returns the thread object (already started).
    """
    global _db_path, _world_name, _images_dir
    _db_path = db_path
    _world_name = world_name
    _images_dir = images_dir

    # Suppress Flask/Werkzeug request logs to keep the console clean
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)

    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    t.start()
    print(f"\n📰 Fantasy Newspaper is live at http://localhost:{port}\n")
    return t
