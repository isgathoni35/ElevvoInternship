"""Unit tests for Task 6: Web Scraping and Job Analysis."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from job_scraper import (
    check_robots_permission,
    parse_job_listings,
    analyze_jobs,
    visualize_skills_by_city,
)

SAMPLE_HTML = """
<div class="job-card">
    <h2 class="job-title">Backend Python Engineer</h2>
    <div class="company">AlphaCorp</div>
    <div class="location">Nairobi</div>
    <div class="skills">Python, Docker, SQL</div>
    <div class="posted-date">2026-11-01</div>
</div>
<div class="job-card">
    <h2 class="job-title">Data Analyst</h2>
    <div class="company">BetaAnalytics</div>
    <div class="location">Nairobi</div>
    <div class="skills">Python, SQL, Excel</div>
    <div class="posted-date">2026-11-02</div>
</div>
"""


class TestJobScraper(unittest.TestCase):
    def test_parse_job_listings(self):
        jobs = parse_job_listings(SAMPLE_HTML)
        self.assertEqual(len(jobs), 2)

        j1 = jobs[0]
        self.assertEqual(j1["title"], "Backend Python Engineer")
        self.assertEqual(j1["company"], "AlphaCorp")
        self.assertEqual(j1["location"], "Nairobi")
        self.assertEqual(j1["skills"], ["Python", "Docker", "SQL"])
        self.assertEqual(j1["posted_date"], "2026-11-01")

    def test_analyze_jobs(self):
        jobs = parse_job_listings(SAMPLE_HTML)
        top_roles, top_skills = analyze_jobs(jobs)

        self.assertEqual(top_roles["Backend Python Engineer"], 1)
        self.assertEqual(top_roles["Data Analyst"], 1)

        # Python and SQL appear in both jobs
        self.assertEqual(top_skills["Python"], 2)
        self.assertEqual(top_skills["SQL"], 2)
        self.assertEqual(top_skills["Docker"], 1)

    def test_check_robots_local_file(self):
        # Local paths / non-HTTP URLs should pass safely
        self.assertTrue(check_robots_permission("jobs_sample.html"))

    def test_visualize_skills_by_city(self):
        jobs = parse_job_listings(SAMPLE_HTML)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_png = Path(tmpdir) / "test_chart.png"
            visualize_skills_by_city(jobs, output_file=str(out_png))
            self.assertTrue(out_png.exists())
            self.assertGreater(out_png.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
