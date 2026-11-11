"""Web Scraping and Analysis of Job Postings.

Extracts job listings from HTML, respects robots.txt rules,
cleans and analyzes skills & roles using pandas, and visualizes
skill frequencies by city using matplotlib.
"""

import argparse
from pathlib import Path
from urllib.parse import urlparse
import urllib.robotparser
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless plot generation
import matplotlib.pyplot as plt
import pandas as pd
import requests


def check_robots_permission(target_url: str, user_agent: str = "*") -> bool:
    """Check if scraping is allowed according to the website's robots.txt.

    Args:
        target_url: Full URL of the page to scrape.
        user_agent: User-Agent name to check for (default: '*').

    Returns:
        True if permitted or if robots.txt cannot be reached, False otherwise.
    """
    parsed = urlparse(target_url)
    if not parsed.scheme or not parsed.netloc:
        # Local file or scheme-less URL
        return True

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(user_agent, target_url)
        return allowed
    except Exception as e:
        print(f"Notice: Could not read robots.txt ({e}). Proceeding carefully.")
        return True


def parse_job_listings(html_content: str) -> list[dict]:
    """Parse HTML content and extract structured job records.

    Extracts: job title, company, location, skills list, and posted date.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    job_cards = soup.find_all(class_="job-card")

    records = []
    for card in job_cards:
        title_el = card.find(class_="job-title") or card.find("h2")
        company_el = card.find(class_="company")
        location_el = card.find(class_="location")
        skills_el = card.find(class_="skills")
        date_el = card.find(class_="posted-date")

        title = title_el.get_text(strip=True) if title_el else "Unknown Title"
        company = company_el.get_text(strip=True) if company_el else "Unknown Company"
        location = location_el.get_text(strip=True) if location_el else "Unknown Location"
        posted_date = date_el.get_text(strip=True) if date_el else "Unknown Date"

        # Split skills string into clean list of normalized skills
        skills_raw = skills_el.get_text(strip=True) if skills_el else ""
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

        records.append({
            "title": title,
            "company": company,
            "location": location,
            "skills": skills,
            "posted_date": posted_date,
        })

    return records


def analyze_jobs(jobs: list[dict]) -> tuple[pd.Series, pd.Series]:
    """Analyze job data using pandas to find most in-demand roles and skills.

    Returns:
        A tuple of (top_roles_series, top_skills_series).
    """
    if not jobs:
        return pd.Series(dtype=int), pd.Series(dtype=int)

    df = pd.DataFrame(jobs)

    # Most in-demand roles
    top_roles = df["title"].value_counts()

    # Explode skills list to analyze frequency
    skills_series = df.explode("skills")["skills"].dropna()
    top_skills = skills_series.value_counts()

    return top_roles, top_skills


def visualize_skills_by_city(jobs: list[dict], output_file: str = "skills_by_city.png"):
    """Generate and save a bar chart of top skills by city."""
    if not jobs:
        return

    df = pd.DataFrame(jobs)
    exploded = df.explode("skills")[["location", "skills"]].dropna()

    # Calculate skill frequency per city
    city_skill_counts = (
        exploded.groupby(["location", "skills"])
        .size()
        .unstack(fill_value=0)
    )

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    city_skill_counts.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")

    ax.set_title("Tech Skill Distribution Across Cities", fontsize=14, fontweight="bold")
    ax.set_xlabel("City / Location", fontsize=12)
    ax.set_ylabel("Skill Mentions", fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(title="Skills", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    fig.savefig(output_file, dpi=150)
    plt.close(fig)
    print(f"[OK] Visualization saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Web Scraping and Job Market Analysis")
    parser.add_argument("--source", default=str(Path(__file__).parent / "jobs_sample.html"),
                        help="Path to local HTML file or web URL (default: jobs_sample.html)")
    parser.add_argument("--chart", default="skills_by_city.png",
                        help="Output path for city skills chart (default: skills_by_city.png)")
    args = parser.parse_args()

    source = args.source
    html_content = ""

    if source.startswith("http://") or source.startswith("https://"):
        print(f"Checking robots.txt for: {source}...")
        if not check_robots_permission(source):
            print(f"[Error] Scraping is disallowed by robots.txt for {source}.")
            return
        print(f"Fetching: {source}...")
        res = requests.get(source, timeout=10)
        res.raise_for_status()
        html_content = res.text
    else:
        file_path = Path(source)
        if not file_path.exists():
            print(f"File not found: {source}")
            return
        html_content = file_path.read_text(encoding="utf-8")

    jobs = parse_job_listings(html_content)
    print(f"\nSuccessfully extracted {len(jobs)} job postings.")

    top_roles, top_skills = analyze_jobs(jobs)

    print("\n--- Top In-Demand Roles ---")
    for role, count in top_roles.items():
        print(f"  {role:<30} : {count} opening(s)")

    print("\n--- Most In-Demand Skills ---")
    for skill, count in top_skills.head(8).items():
        print(f"  {skill:<20} : {count} mention(s)")

    # Generate chart visualization
    visualize_skills_by_city(jobs, output_file=args.chart)


if __name__ == "__main__":
    main()
