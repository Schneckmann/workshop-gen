from app import db
from tests.support import AppTestCase


def _count() -> int:
    conn = db.connect()
    try:
        return conn.execute("SELECT COUNT(*) FROM features").fetchone()[0]
    finally:
        conn.close()


class FeaturesTest(AppTestCase):
    def test_form_has_name_module_and_notes_inputs(self):
        status, _, body = self.get("/features")
        self.assertEqual(status, 200)
        self.assertIn('<form method="post" action="/features">', body)
        self.assertIn('name="name"', body)
        self.assertIn('name="module"', body)
        self.assertIn('<textarea name="notes"', body)

    def test_nav_links_to_features(self):
        self.assertIn('<a href="/features">Features</a>', self.get("/")[2])

    def test_valid_post_redirects_to_feature_page(self):
        before = _count()
        status, headers, _ = self.post_form("/features", {"name": "Order entry", "module": "Sales", "notes": "n"})
        self.assertEqual(status, 303)
        self.assertRegex(headers["Location"], r"^/features/\d+$")
        self.assertEqual(_count(), before + 1)

    def test_notes_are_optional(self):
        status, _, _ = self.post_form("/features", {"name": "No notes", "module": "Sales"})
        self.assertEqual(status, 303)

    def test_missing_name_is_400_and_keeps_input(self):
        before = _count()
        status, _, body = self.post_form("/features", {"name": "  ", "module": "Sales", "notes": "keep me"})
        self.assertEqual(status, 400)
        self.assertIn('class="error"', body)
        self.assertIn("Name is required.", body)
        self.assertIn('value="Sales"', body)
        self.assertIn("keep me</textarea>", body)
        self.assertEqual(_count(), before)

    def test_missing_module_is_400(self):
        before = _count()
        status, _, body = self.post_form("/features", {"name": "X", "module": ""})
        self.assertEqual(status, 400)
        self.assertIn("Module is required.", body)
        self.assertEqual(_count(), before)

    def test_missing_fields_entirely_is_400_not_500(self):
        self.assertEqual(self.post_form("/features", {})[0], 400)

    def test_list_is_grouped_by_module(self):
        self.post_form("/features", {"name": "Receiving", "module": "Warehouse"})
        self.post_form("/features", {"name": "Picking", "module": "Warehouse"})
        self.post_form("/features", {"name": "Purchase orders", "module": "Purchasing"})
        body = self.get("/features")[2]
        self.assertEqual(body.count("<h2>Warehouse</h2>"), 1)
        warehouse = body.split("<h2>Warehouse</h2>")[1].split("</section>")[0]
        self.assertIn("Receiving", warehouse)
        self.assertIn("Picking", warehouse)
        self.assertNotIn("Purchase orders", warehouse)
        self.assertLess(body.index("<h2>Purchasing</h2>"), body.index("<h2>Warehouse</h2>"))

    def test_user_values_are_escaped(self):
        self.post_form("/features", {"name": "<script>x</script>", "module": "<b>M</b>"})
        body = self.get("/features")[2]
        self.assertNotIn("<script>x", body)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", body)
        self.assertIn("&lt;b&gt;M&lt;/b&gt;", body)

    def test_error_rerender_escapes_input(self):
        body = self.post_form("/features", {"name": "", "module": '"><i>'})[2]
        self.assertNotIn("<i>", body)


class EmptyFeaturesTest(AppTestCase):
    def test_empty_list_says_so(self):
        self.assertIn("No features yet", self.get("/features")[2])
