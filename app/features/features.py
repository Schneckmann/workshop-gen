"""Features: the consultant's notes on each feature, listed grouped by module."""

from __future__ import annotations

from itertools import groupby

from app import db
from app.layout import NAV, page
from app.web import Request, Response, h, html_response, redirect, route

db.migration(
    "features_001_create",
    "CREATE TABLE IF NOT EXISTS features ("
    "id INTEGER PRIMARY KEY, name TEXT NOT NULL, module TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '')",
)
NAV.append(("/features", "Features"))


def _list_features() -> list[dict]:
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT id, name, module FROM features ORDER BY module COLLATE NOCASE, module, id"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def _insert_feature(name: str, module: str, notes: str) -> int:
    conn = db.connect()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO features (name, module, notes) VALUES (?, ?, ?)", (name, module, notes)
            )
        return int(cur.lastrowid)
    finally:
        conn.close()


def _grouped_list(features: list[dict]) -> str:
    if not features:
        return '<p class="empty">No features yet. Add the first one above.</p>'
    sections = []
    for module, items in groupby(features, key=lambda f: f["module"]):
        rows = "".join(
            f'<li><a href="/features/{f["id"]}">{h(f["name"])}</a></li>' for f in items
        )
        sections.append(f'<section class="card"><h2>{h(module)}</h2><ul>{rows}</ul></section>')
    return "".join(sections)


def _form(values: dict[str, str], error: str = "") -> str:
    message = f'<p class="error" role="alert">{h(error)}</p>' if error else ""
    return f"""{message}<form method="post" action="/features">
<label>Name <input type="text" name="name" value="{h(values.get("name", ""))}" required></label>
<label>Module <input type="text" name="module" value="{h(values.get("module", ""))}" required></label>
<label>Notes <textarea name="notes" rows="6">{h(values.get("notes", ""))}</textarea></label>
<button type="submit">Add feature</button>
</form>"""


def _render(values: dict[str, str], error: str = "", status: int = 200) -> Response:
    body = f"<h1>Features</h1>{_form(values, error)}{_grouped_list(_list_features())}"
    return html_response(page("Features", body), status)


@route("GET", "/features")
def show_features(req: Request) -> Response:
    return _render({})


@route("POST", "/features")
def add_feature(req: Request) -> Response:
    values = req.form
    name, module = values.get("name", ""), values.get("module", "")
    if not name:
        return _render(values, "Name is required.", 400)
    if not module:
        return _render(values, "Module is required.", 400)
    feature_id = _insert_feature(name, module, values.get("notes", ""))
    return redirect(f"/features/{feature_id}")
