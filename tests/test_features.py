import os
import re
import sqlite3

from tests.support import AppTestCase

NOTES = "Scan the delivery note, then book the pallets."


class FeaturesTest(AppTestCase):
    def setUp(self):
        conn = sqlite3.connect(os.environ["APP_DATABASE"])
        try:
            conn.execute("DELETE FROM features")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()
        self.get("/features")

    def count(self):
        conn = sqlite3.connect(os.environ["APP_DATABASE"])
        try:
            return conn.execute("SELECT COUNT(*) FROM features").fetchone()[0]
        finally:
            conn.close()

    def add(self, name, module, notes=""):
        return self.post_form("/features", {"name": name, "module": module, "notes": notes})

    def test_get_renders_form(self):
        status, headers, body = self.get("/features")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn('<form method="post" action="/features">', body)
        self.assertIn('<input type="text" name="name"', body)
        self.assertIn('<input type="text" name="module"', body)
        self.assertIn('<textarea name="notes">', body)

    def test_nav_links_to_features(self):
        self.assertIn('<a href="/features">Features</a>', self.get("/")[2])

    def test_post_valid_redirects_and_stores_one_row(self):
        status, headers, _ = self.add("Goods receipt", "Warehouse", NOTES)
        self.assertEqual(status, 303)
        self.assertRegex(headers["Location"], r"^/features/\d+$")
        self.assertEqual(self.count(), 1)
        row_id = int(headers["Location"].rsplit("/", 1)[1])
        conn = sqlite3.connect(os.environ["APP_DATABASE"])
        try:
            row = conn.execute(
                "SELECT name, module, notes FROM features WHERE id = ?", (row_id,)
            ).fetchone()
        finally:
            conn.close()
        self.assertEqual(row, ("Goods receipt", "Warehouse", NOTES))

    def test_list_shows_feature_under_module_with_link(self):
        _, headers, _ = self.add("Goods receipt", "Warehouse", NOTES)
        body = self.get("/features")[2]
        self.assertIn("<h2>Warehouse</h2>", body)
        self.assertIn(f'<a href="{headers["Location"]}">Goods receipt</a>', body)

    def test_features_grouped_by_module(self):
        self.add("Orders", "Purchasing")
        self.add("Goods receipt", "Warehouse")
        self.add("Stock count", "Warehouse")
        body = self.get("/features")[2]
        self.assertEqual(body.count("<h2>Warehouse</h2>"), 1)
        self.assertEqual(body.count("<h2>Purchasing</h2>"), 1)
        sections = re.split(r"<h2>", body)[1:]
        by_module = {s.split("</h2>")[0]: s for s in sections}
        self.assertIn("Orders", by_module["Purchasing"])
        self.assertNotIn("Goods receipt", by_module["Purchasing"])
        self.assertIn("Goods receipt", by_module["Warehouse"])
        self.assertIn("Stock count", by_module["Warehouse"])
        self.assertNotIn("Orders", by_module["Warehouse"])

    def test_empty_name_rejected_and_values_kept(self):
        for name in ("", "   "):
            status, _, body = self.add(name, "Warehouse", NOTES)
            self.assertEqual(status, 400)
            self.assertIn('class="error">Name is required.', body)
            self.assertIn('value="Warehouse"', body)
            self.assertIn(NOTES, body)
        self.assertEqual(self.count(), 0)

    def test_empty_module_rejected(self):
        status, _, body = self.add("Goods receipt", "", NOTES)
        self.assertEqual(status, 400)
        self.assertIn('class="error">Module is required.', body)
        self.assertIn('value="Goods receipt"', body)
        self.assertIn(NOTES, body)
        self.assertEqual(self.count(), 0)

    def test_missing_fields_rejected_not_500(self):
        status, _, body = self.post_form("/features", {})
        self.assertEqual(status, 400)
        self.assertIn("Name is required.", body)

    def test_empty_notes_accepted(self):
        self.assertEqual(self.add("Goods receipt", "Warehouse", "")[0], 303)
        self.assertEqual(self.count(), 1)

    def test_user_values_are_escaped(self):
        self.add("<script>alert(1)</script>", "<b>Sales</b>")
        body = self.get("/features")[2]
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertIn("&lt;b&gt;Sales&lt;/b&gt;", body)
        self.assertNotIn("<script>alert(1)", body)
        self.assertNotIn("<b>Sales</b>", body)

    def test_empty_list_message(self):
        status, _, body = self.get("/features")
        self.assertEqual(status, 200)
        self.assertIn("No features yet.", body)

    def feature_url(self, *args):
        return self.add(*args)[1]["Location"]

    def test_detail_shows_name_module_notes_and_back_link(self):
        status, headers, body = self.get(self.feature_url("Goods receipt", "Warehouse", NOTES))
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("<h1>Goods receipt</h1>", body)
        self.assertIn("Warehouse", body)
        self.assertIn(NOTES, body)
        self.assertIn('<a href="/features">', body)

    def test_detail_keeps_line_breaks_in_notes(self):
        body = self.get(self.feature_url("Goods receipt", "Warehouse", "one\ntwo"))[2]
        self.assertIn("white-space: pre-wrap", body)
        self.assertIn("one\ntwo", body)

    def test_detail_escapes_user_values(self):
        body = self.get(self.feature_url("<i>n</i>", "<b>m</b>", "<script>x</script>"))[2]
        self.assertIn("&lt;i&gt;n&lt;/i&gt;", body)
        self.assertIn("&lt;b&gt;m&lt;/b&gt;", body)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", body)
        self.assertNotIn("<script>x", body)
        self.assertNotIn("<b>m</b>", body)

    def test_detail_unknown_id_is_404(self):
        self.assertEqual(self.get("/features/999999")[0], 404)

    def test_detail_oversized_id_is_404(self):
        self.assertEqual(self.get("/features/99999999999999999999")[0], 404)

    def test_detail_huge_digit_string_id_is_404(self):
        self.assertEqual(self.get("/features/" + "9" * 5000)[0], 404)

    def test_detail_non_numeric_id_is_404(self):
        self.assertEqual(self.get("/features/abc")[0], 404)
