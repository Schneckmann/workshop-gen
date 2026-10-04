"""Features of the customer's software: what the consultant records, grouped by module."""

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


def _render_page(values: dict[str, str] | None = None, error: str = "", status: int = 200) -> Response:
    values = values or {}
    conn = db.connect()
    try:
        rows = conn.execute("SELECT id, name, module FROM features ORDER BY module, id").fetchall()
    finally:
        conn.close()

    if rows:
        groups = "".join(
            f"<section><h2>{h(module)}</h2><ul>"
            + "".join(f'<li><a href="/features/{r["id"]}">{h(r["name"])}</a></li>' for r in members)
            + "</ul></section>"
            for module, members in groupby(rows, key=lambda r: r["module"])
        )
    else:
        groups = "<p>No features yet.</p>"

    error_html = f'<p class="error" role="alert">{h(error)}</p>' if error else ""
    body = f"""<h1>Features</h1>
<form method="post" action="/features">
{error_html}
<label>Name <input type="text" name="name" value="{h(values.get("name", ""))}" required></label>
<label>Module <input type="text" name="module" value="{h(values.get("module", ""))}" required></label>
<label>Notes <textarea name="notes">{h(values.get("notes", ""))}</textarea></label>
<button type="submit">Add feature</button>
</form>
{groups}"""
    return html_response(page("Features", body), status)


@route("GET", "/features")
def list_features(req: Request) -> Response:
    return _render_page()


@route("POST", "/features")
def create_feature(req: Request) -> Response:
    values = {key: req.form.get(key, "") for key in ("name", "module", "notes")}
    if not values["name"]:
        return _render_page(values, "Name is required.", 400)
    if not values["module"]:
        return _render_page(values, "Module is required.", 400)
    conn = db.connect()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO features (name, module, notes) VALUES (?, ?, ?)",
                (values["name"], values["module"], values["notes"]),
            )
        feature_id = cur.lastrowid
    finally:
        conn.close()
    return redirect(f"/features/{feature_id}")
