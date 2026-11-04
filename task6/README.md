# Task 6: Web Scraping and Analysis of Job Postings

A web scraping and data analysis script built using `BeautifulSoup`, `pandas`, and `matplotlib`.

---

## Features
- **Scraping with robots.txt Compliance**: Checks `robots.txt` using `urllib.robotparser` to ensure web scraping permissions before downloading web pages.
- **HTML Extraction**: Parses job postings to extract `title`, `company`, `location`, `skills`, and `posted_date`.
- **Data Analysis (`pandas`)**: Cleans extracted data, explodes multi-value skill tags, and identifies top in-demand roles and skills.
- **Bonus Visualization (`matplotlib`)**: Generates a stacked bar chart (`skills_by_city.png`) illustrating skill distribution across different cities.

---

## Files
- `job_scraper.py`: Core scraper, analysis, and plotting module.
- `jobs_sample.html`: Deterministic test HTML fixture with diverse tech job listings across multiple cities.
- `test_job_scraper.py`: Unit tests for parsing, pandas aggregation, and visualization.
- `skills_by_city.png`: Generated chart output.

---

## How to Run

### 1. Run Analysis on the Sample HTML
```bash
python task6/job_scraper.py
```

### 2. Run Analysis on a Live Web URL
```bash
python task6/job_scraper.py --source https://example.com/jobs
```

### 3. Run the Unit Tests
```bash
python -m unittest task6/test_job_scraper.py
```
