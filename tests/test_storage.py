import tempfile
import unittest
from pathlib import Path

from keiba_money.storage import RaceStorage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = RaceStorage(Path(self.temp_dir.name) / "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_list(self):
        race_id = self.storage.add("天皇賞", "2026-11-02", 1000, 2500)
        rows = self.storage.list_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], race_id)
        self.assertEqual(rows[0]["profit"], 1500)

    def test_totals(self):
        self.storage.add("レースA", "2026-11-01", 1000, 1500)
        self.storage.add("レースB", "2026-11-02", 2000, 0)
        totals = self.storage.totals()
        self.assertEqual(totals["purchase"], 3000)
        self.assertEqual(totals["payout"], 1500)
        self.assertEqual(totals["profit"], -1500)
        self.assertEqual(totals["recovery_rate"], 50.0)

    def test_delete(self):
        race_id = self.storage.add("レースA", "2026-11-01", 100, 0)
        self.assertTrue(self.storage.delete(race_id))
        self.assertFalse(self.storage.delete(race_id))
        self.assertEqual(self.storage.list_all(), [])

    def test_empty_totals(self):
        self.assertEqual(self.storage.totals()["recovery_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
