import re

from app import db
from tests.support import AppTestCase


class FeaturesTest(AppTestCase):
    def setUp(self):
        conn = db.connect()
        try:
            with conn:
                conn.execute("DELETE FROM features")
        finally:
            conn.close()

    def rows(self):
        conn = db.connect()
        try:
            return conn.execute("SELECT id, name, module, notes FROM features ORDER BY id").fetchall()
        finally:
            conn.close()

    def add(self, name, module, notes=""):
        return self.post_form("/features", {"name": name, "module": module, "notes": notes})

    def test_get_renders_form(self):
        status, headers, body = self.get("/features")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn('<form method="post" action="/features">', body)
        self.assertIn('name="name"', body)
        self.assertIn('name="module"', body)
        self.assertIn('<textarea name="notes">', body)

    def test_nav_links_to_features_on_every_page(self):
        self.assertIn('<a href="/features">Features</a>', self.get("/")[2])
        self.assertIn('<a href="/features">Features</a>', self.get("/features")[2])

    def test_post_stores_row_and_redirects(self):
        notes = "Scan the delivery note, then book the pallets."
        status, headers, _ = self.add("Goods receipt", "Warehouse", notes)
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], f"/features/{rows[0]['id']}")
        self.assertEqual((rows[0]["name"], rows[0]["module"], rows[0]["notes"]),
                         ("Goods receipt", "Warehouse", notes))

    def test_list_shows_feature_under_module_heading_with_link(self):
        self.add("Goods receipt", "Warehouse")
        fid = self.rows()[0]["id"]
        body = self.get("/features")[2]
        self.assertIn("<h2>Warehouse</h2>", body)
        self.assertIn(f'<a href="/features/{fid}">Goods receipt</a>', body)

    def test_features_group_by_module(self):
        self.add("Order", "Purchasing")
        self.add("Goods receipt", "Warehouse")
        self.add("Putaway", "Warehouse")
        body = self.get("/features")[2]
        self.assertEqual(body.count("<h2>Warehouse</h2>"), 1)
        self.assertEqual(body.count("<h2>Purchasing</h2>"), 1)
        sections = re.findall(r"<section>(.*?)</section>", body, re.S)
        by_module = {re.search(r"<h2>(.*?)</h2>", s).group(1): s for s in sections}
        self.assertIn("Order", by_module["Purchasing"])
        self.assertNotIn("Goods receipt", by_module["Purchasing"])
        self.assertIn("Goods receipt", by_module["Warehouse"])
        self.assertIn("Putaway", by_module["Warehouse"])
        self.assertNotIn("Order", by_module["Warehouse"])
        self.assertLess(by_module["Warehouse"].index("Goods receipt"), by_module["Warehouse"].index("Putaway"))

    def test_blank_name_is_refused_and_form_keeps_values(self):
        for name in ("", "   "):
            status, _, body = self.add(name, "Warehouse", "keep me")
            self.assertEqual(status, 400)
            self.assertIn('<p class="error" role="alert">Name is required.</p>', body)
            self.assertIn('name="module" value="Warehouse"', body)
            self.assertIn('<textarea name="notes">keep me</textarea>', body)
        self.assertEqual(self.rows(), [])

    def test_blank_module_is_refused(self):
        status, _, body = self.add("Goods receipt", "")
        self.assertEqual(status, 400)
        self.assertIn("Module is required.", body)
        self.assertIn('name="name" value="Goods receipt"', body)
        self.assertEqual(self.rows(), [])

    def test_missing_fields_are_refused_not_500(self):
        status, _, body = self.post_form("/features", {})
        self.assertEqual(status, 400)
        self.assertIn("Name is required.", body)

    def test_empty_notes_are_accepted(self):
        status, _, _ = self.add("Goods receipt", "Warehouse", "")
        self.assertEqual(status, 303)
        self.assertEqual(self.rows()[0]["notes"], "")

    def test_user_values_are_escaped(self):
        self.add("<script>alert(1)</script>", "<b>Sales</b>")
        body = self.get("/features")[2]
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertIn("&lt;b&gt;Sales&lt;/b&gt;", body)
        self.assertNotIn("<script>alert(1)", body)
        self.assertNotIn("<b>Sales</b>", body)

    def test_error_rerender_escapes_typed_values(self):
        _, _, body = self.add("", '"><script>x</script>', "<i>n</i>")
        self.assertNotIn("<script>x</script>", body)
        self.assertNotIn("<i>n</i>", body)

    def test_empty_list_message(self):
        status, _, body = self.get("/features")
        self.assertEqual(status, 200)
        self.assertIn("No features yet.", body)
