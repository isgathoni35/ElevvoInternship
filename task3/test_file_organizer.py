"""Unit tests for Task 3: Automated File Organizer."""

import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from file_organizer import organize_directory, get_unique_destination


class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.target = Path(self.test_dir)
        # Suppress logging during tests
        self.logger = logging.getLogger("TestLogger")
        self.logger.setLevel(logging.CRITICAL)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_organize_files_by_extension(self):
        # Create test files
        (self.target / "doc1.txt").write_text("text 1", encoding="utf-8")
        (self.target / "doc2.txt").write_text("text 2", encoding="utf-8")
        (self.target / "image.png").write_text("image data", encoding="utf-8")
        (self.target / "data.csv").write_text("a,b,c", encoding="utf-8")
        (self.target / "no_ext").write_text("no extension file", encoding="utf-8")

        summary = organize_directory(str(self.target), dry_run=False, logger=self.logger)
        self.assertEqual(len(summary), 5)

        # Check subfolders
        self.assertTrue((self.target / "txt" / "doc1.txt").exists())
        self.assertTrue((self.target / "txt" / "doc2.txt").exists())
        self.assertTrue((self.target / "png" / "image.png").exists())
        self.assertTrue((self.target / "csv" / "data.csv").exists())
        self.assertTrue((self.target / "no_extension" / "no_ext").exists())

    def test_collision_safe_no_overwrite(self):
        # Pre-create destination file in 'txt' folder
        txt_folder = self.target / "txt"
        txt_folder.mkdir(parents=True)
        original_dest = txt_folder / "file.txt"
        original_dest.write_text("ORIGINAL CONTENT", encoding="utf-8")

        # Incoming file with same name in target root
        incoming = self.target / "file.txt"
        incoming.write_text("NEW CONTENT", encoding="utf-8")

        organize_directory(str(self.target), dry_run=False, logger=self.logger)

        # Ensure original file was NOT overwritten
        self.assertEqual(original_dest.read_text(encoding="utf-8"), "ORIGINAL CONTENT")

        # Ensure incoming file was renamed with a suffix
        renamed_file = txt_folder / "file_1.txt"
        self.assertTrue(renamed_file.exists())
        self.assertEqual(renamed_file.read_text(encoding="utf-8"), "NEW CONTENT")

    def test_dry_run_does_not_move_files(self):
        test_file = self.target / "sample.pdf"
        test_file.write_text("pdf content", encoding="utf-8")

        summary = organize_directory(str(self.target), dry_run=True, logger=self.logger)
        self.assertEqual(len(summary), 1)

        # File should still be in original location
        self.assertTrue(test_file.exists())
        # Destination folder should not exist or not have file
        self.assertFalse((self.target / "pdf" / "sample.pdf").exists())

    def test_empty_folder(self):
        summary = organize_directory(str(self.target), dry_run=False, logger=self.logger)
        self.assertEqual(summary, [])


if __name__ == "__main__":
    unittest.main()
