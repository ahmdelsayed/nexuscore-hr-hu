import csv
import os
import tempfile
import unittest
from unittest.mock import patch

from hr_hub_engine import BASE_DIR, HRHubEngine, PostgresStorage, REMOTE_DEMO_SEED
from run_acceptance_tests import reset_test_databases


class StorageTests(unittest.TestCase):
    def test_local_csv_update_changes_only_matching_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidates_file = os.path.join(temp_dir, "Candidates.csv")
            with open(candidates_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["application_id", "stage"])
                writer.writeheader()
                writer.writerows([
                    {"application_id": "APP-1", "stage": "Applied"},
                    {"application_id": "APP-2", "stage": "Interview"},
                ])

            with patch.dict(os.environ, {"DATABASE_URL": ""}):
                engine = HRHubEngine()
            engine.candidates_file = candidates_file

            updated = engine._update_csv_row(
                candidates_file,
                "application_id",
                "APP-1",
                {"stage": "Hired", "reviewed_by": "Demo Reviewer"},
            )

            self.assertTrue(updated)
            self.assertEqual(
                engine._read_csv(candidates_file),
                [
                    {
                        "application_id": "APP-1",
                        "stage": "Hired",
                        "reviewed_by": "Demo Reviewer",
                    },
                    {
                        "application_id": "APP-2",
                        "stage": "Interview",
                        "reviewed_by": "",
                    },
                ],
            )

    def test_database_seed_contains_only_relative_demo_references(self):
        for rows in REMOTE_DEMO_SEED.values():
            for row in rows:
                for key in ("description_ref", "cv_link", "private_link"):
                    value = row.get(key)
                    if value:
                        self.assertFalse(os.path.isabs(value))
                        self.assertNotIn("\\", value)

    def test_database_only_accepts_known_data_files(self):
        self.assertEqual(
            PostgresStorage._dataset_name(r"C:\project\data\Candidates.csv"),
            "candidates",
        )
        with self.assertRaises(ValueError):
            PostgresStorage._dataset_name(r"C:\project\data\private.csv")

    def test_stored_references_do_not_expose_absolute_paths(self):
        project_file = os.path.join(BASE_DIR, "synthetic_dataset", "resumes", "demo.pdf")
        self.assertEqual(
            HRHubEngine._stored_reference(project_file),
            "synthetic_dataset/resumes/demo.pdf",
        )
        self.assertEqual(HRHubEngine._stored_reference(r"C:\private\cv.pdf"), "cv.pdf")

    def test_acceptance_reset_is_blocked_when_database_url_is_set(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://not-used"}):
            with self.assertRaisesRegex(RuntimeError, "unset DATABASE_URL"):
                reset_test_databases()


if __name__ == "__main__":
    unittest.main()
