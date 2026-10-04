"""Features: what the consultant records about the customer's software."""

from __future__ import annotations

import sqlite3

from app import db
from app.layout import NAV, page
from app.web import Request, Response, h, html_response, redirect, route

db.migration(
    "features_001_create",
    "CREATE TABLE IF NOT EXISTS features ("
    "id INTEGER PRIMARY KEY, name TEXT NOT NULL, module TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '')",
)
db.migration(
    "features_002_prep_items",
    "CREATE TABLE IF NOT EXISTS prep_items ("
    "id INTEGER PRIMARY KEY, feature_id INTEGER NOT NULL REFERENCES features(id), "
    "text TEXT NOT NULL, ready INTEGER NOT NULL DEFAULT 0)",
)
NAV.append(("/features", "Features"))


def _grouped_features() -> dict[str, list[tuple[int, str]]]:
    conn = db.connect()
    try:
        rows = conn.execute("SELECT id, name, module FROM features ORDER BY id").fetchall()
    finally:
        conn.close()
    groups: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        groups.setdefault(row["module"], []).append((row["id"], row["name"]))
    return groups


SQLITE_MAX_ID = 2**63 - 1
MAX_ID_DIGITS = len(str(SQLITE_MAX_ID))


def _load_feature(raw_id: str) -> sqlite3.Row | None:
    if not raw_id.isascii() or not raw_id.isdigit():
        return None
    digits = raw_id.lstrip("0") or "0"
    # Length check first: int() raises ValueError on strings past 4300 digits.
    if len(digits) > MAX_ID_DIGITS or int(digits) > SQLITE_MAX_ID:
        return None
    conn = db.connect()
    try:
        return conn.execute(
            "SELECT id, name, module, notes FROM features WHERE id = ?", (int(digits),)
        ).fetchone()
    finally:
        conn.close()


def _render(values: dict[str, str], error: str = "", status: int = 200) -> Response:
    message = f'<p class="error">{h(error)}</p>' if error else ""
    form = f"""<form method="post" action="/features">
{message}
<label>Name <input type="text" name="name" value="{h(values.get("name", ""))}"></label>
<label>Module <input type="text" name="module" value="{h(values.get("module", ""))}"></label>
<label>Notes <textarea name="notes">{h(values.get("notes", ""))}</textarea></label>
<button type="submit">Add feature</button>
</form>"""
    groups = _grouped_features()
    if groups:
        listing = "".join(
            f"<h2>{h(module)}</h2><ul>"
            + "".join(f'<li><a href="/features/{fid}">{h(name)}</a></li>' for fid, name in items)
            + "</ul>"
            for module, items in groups.items()
        )
    else:
        listing = "<p>No features yet.</p>"
    return html_response(page("Features", f"<h1>Features</h1>{form}{listing}"), status)


@route("GET", "/features")
def show_features(req: Request) -> Response:
    return _render({})


@route("POST", "/features")
def add_feature(req: Request) -> Response:
    values = req.form
    if not values.get("name"):
        return _render(values, "Name is required.", 400)
    if not values.get("module"):
        return _render(values, "Module is required.", 400)
    conn = db.connect()
    try:
        cur = conn.execute(
            "INSERT INTO features (name, module, notes) VALUES (?, ?, ?)",
            (values["name"], values["module"], values.get("notes", "")),
        )
        conn.commit()
        new_id = cur.lastrowid
    finally:
        conn.close()
    return redirect(f"/features/{new_id}")


def _prep_items(feature_id: int) -> list[str]:
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT text FROM prep_items WHERE feature_id = ? ORDER BY id", (feature_id,)
        ).fetchall()
    finally:
        conn.close()
    return [row["text"] for row in rows]


def _render_feature(feature: sqlite3.Row, error: str = "", status: int = 200) -> Response:
    items = _prep_items(feature["id"])
    if items:
        listing = "<ol>" + "".join(f"<li>{h(text)}</li>" for text in items) + "</ol>"
    else:
        listing = "<p>No preparation items yet.</p>"
    message = f'<p class="error">{h(error)}</p>' if error else ""
    body = (
        f"<h1>{h(feature['name'])}</h1>"
        f"<p>Module: {h(feature['module'])}</p>"
        f'<div class="notes" style="white-space: pre-wrap">{h(feature["notes"])}</div>'
        "<h2>Preparation</h2>"
        f"{listing}"
        f'<form method="post" action="/features/{feature["id"]}/prep">'
        f"{message}"
        '<label>Item <input type="text" name="text"></label>'
        '<button type="submit">Add item</button>'
        "</form>"
        '<p><a href="/features">Back to features</a></p>'
    )
    return html_response(page(feature["name"], body), status)


def _not_found() -> Response:
    return html_response(page("Not found", "<h1>Not found</h1>"), 404)


@route("GET", "/features/{feature_id}")
def show_feature(req: Request) -> Response:
    feature = _load_feature(req.params["feature_id"])
    if feature is None:
        return _not_found()
    return _render_feature(feature)


@route("POST", "/features/{feature_id}/prep")
def add_prep_item(req: Request) -> Response:
    feature = _load_feature(req.params["feature_id"])
    if feature is None:
        return _not_found()
    text = req.form.get("text", "").strip()
    if not text:
        return _render_feature(feature, "Preparation item is required.", 400)
    conn = db.connect()
    try:
        conn.execute("INSERT INTO prep_items (feature_id, text) VALUES (?, ?)", (feature["id"], text))
        conn.commit()
    finally:
        conn.close()
    return redirect(f"/features/{feature['id']}")
