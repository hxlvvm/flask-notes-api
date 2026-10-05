from flask import Blueprint, abort, jsonify, request

from .db import get_db

bp = Blueprint("notes", __name__)


def _row(r) -> dict:
    d = dict(r)
    d["tags"] = [t for t in d["tags"].split(",") if t]
    return d


def _validated(payload: dict, partial: bool = False) -> dict:
    """Minimal validation without extra libraries: title required (unless partial), tags must be a list of str."""
    if not isinstance(payload, dict):
        abort(400, description="JSON object expected")
    out = {}
    if "title" in payload or not partial:
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            abort(400, description="title must be a non-empty string")
        out["title"] = title.strip()
    if "body" in payload:
        if not isinstance(payload["body"], str):
            abort(400, description="body must be a string")
        out["body"] = payload["body"]
    if "tags" in payload:
        tags = payload["tags"]
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            abort(400, description="tags must be a list of strings")
        out["tags"] = ",".join(sorted({t.strip().lower() for t in tags if t.strip()}))
    return out


@bp.post("/notes")
def create_note():
    data = _validated(request.get_json(silent=True))
    db = get_db()
    cur = db.execute("INSERT INTO notes (title, body, tags) VALUES (?, ?, ?)",
                     (data["title"], data.get("body", ""), data.get("tags", "")))
    db.commit()
    row = db.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(_row(row)), 201


@bp.get("/notes")
def list_notes():
    q, tag = request.args.get("q", ""), request.args.get("tag", "")
    sql, params = "SELECT * FROM notes WHERE 1=1", []
    if q:
        sql += " AND (title LIKE ? OR body LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if tag:
        sql += " AND (',' || tags || ',') LIKE ?"
        params.append(f"%,{tag.lower()},%")
    rows = get_db().execute(sql + " ORDER BY id DESC", params).fetchall()
    return jsonify([_row(r) for r in rows])


@bp.get("/notes/<int:note_id>")
def get_note(note_id: int):
    row = get_db().execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        abort(404, description="note not found")
    return jsonify(_row(row))


@bp.patch("/notes/<int:note_id>")
def update_note(note_id: int):
    data = _validated(request.get_json(silent=True), partial=True)
    db = get_db()
    if db.execute("SELECT 1 FROM notes WHERE id = ?", (note_id,)).fetchone() is None:
        abort(404, description="note not found")
    if data:
        cols = ", ".join(f"{k} = ?" for k in data)
        db.execute(f"UPDATE notes SET {cols} WHERE id = ?", (*data.values(), note_id))
        db.commit()
    return get_note(note_id)


@bp.delete("/notes/<int:note_id>")
def delete_note(note_id: int):
    db = get_db()
    if db.execute("DELETE FROM notes WHERE id = ?", (note_id,)).rowcount == 0:
        abort(404, description="note not found")
    db.commit()
    return "", 204


@bp.errorhandler(400)
@bp.errorhandler(404)
def _error(e):
    return jsonify(error=e.description), e.code
