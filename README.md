# Elevo Python Programming & AI Internship — Master Deliverables

This repository contains the complete implementation of the 9-task curriculum for the **Elevo Python Programming & AI Internship**. Every task is implemented with clean architecture, modular design, and comprehensive test coverage.

---

## Curriculum Overview & Status Matrix

| Task | Module | Description | Core Deliverables | Automated Tests |
| :---: | :--- | :--- | :--- | :---: |
| **01** | Modules 1, 2, 4 | CLI Expense Tracker with JSON Persistence | `expense_tracker.py`, `expenses.json` | 4 / 4 Passed |
| **02** | Module 3 | Student Grade Processor with Custom Functions | `grade_processor.py`, `main.py` | 5 / 5 Passed |
| **03** | Module 4 | Safe Automated File Organizer | `file_organizer.py`, `organizer.log` | 4 / 4 Passed |
| **04** | Module 5 | OOP Inventory Management with Properties | `inventory.py`, `main.py` | 5 / 5 Passed |
| **05** | Module 6 | Weather Dashboard Using Public REST API | `weather_dashboard.py`, `.env.example` | 6 / 6 Passed |
| **06** | Module 7 | Web Scraping & Job Skill Demand Analysis | `job_scraper.py`, `jobs_sample.html`, `skills_by_city.png` | 4 / 4 Passed |
| **07** | Module 8 | LLM-Powered Document Q&A (RAG Basics) | `rag_tool.py`, `documents/` (4 docs) | 4 / 4 Passed |
| **08** | Module 9 | AI-Assisted Code Review Tool | `code_reviewer.py`, `sample_target.py` | 6 / 6 Passed |
| **09** | Self-study | AI Agent for a Two-Tool Task | `agent.py`, `agent_execution.log`, `result.txt` | 4 / 4 Passed |

---

## Global Test Runner

You can execute the entire test suite across all 9 tasks with a single command from the project root:

```powershell
# Run all unit tests
Get-ChildItem -Recurse -Filter "test_*.py" | ForEach-Object { Write-Host "`n=== Testing $($_.Name) ==="; python -m unittest $_.FullName }

# Run pytest on Task 5
pytest task5/test_weather.py -v
```

---

## Detailed Step-by-Step Testing Guide

Follow these steps to interact with and test each project firsthand:

### Task 1: CLI Expense Tracker
Tracks daily expenditures in memory, persists to local JSON, and produces monthly summary reports.

- **To run interactively**:
  ```bash
  python task1/expense_tracker.py
  ```
  - Choose `[1]` to add an expense (e.g. Amount: `45.50`, Category: `Food`, Date: press Enter for today).
  - Choose `[2]` to view all saved expenses in a clean table.
  - Choose `[3]` to view the monthly summary report showing total spent and category breakdown.
  - Choose `[4]` to exit.

- **To run unit tests**:
  ```bash
  python -m unittest task1/test_expense_tracker.py
  ```

---

### Task 2: Student Grade Processor
Modular calculation engine calculating averages, highest/lowest scores, pass/fail status, and custom `InvalidScoreError` validation.

- **To run the demonstration**:
  ```bash
  python task2/main.py
  ```
  - Displays class average calculation, top student, lowest student, pass/fail statuses, and demonstrates catching invalid scores ($> 100$ or $< 0$).

- **To run unit tests**:
  ```bash
  python -m unittest task2/test_grade_processor.py
  ```

---

### Task 3: Automated File Organizer
Scans a directory and sorts files by extension into subfolders. Guaranteed never to overwrite existing files (appends unique numerical suffixes).

- **To test with a dry-run preview** (does not modify files):
  ```bash
  python task3/file_organizer.py path/to/folder --dry-run
  ```
- **To run live**:
  ```bash
  python task3/file_organizer.py path/to/folder
  ```
- **To run unit tests** (verifies sorting, conflict renaming, and dry-run):
  ```bash
  python -m unittest task3/test_file_organizer.py
  ```

---

### Task 4: OOP Inventory Management System
Demonstrates object-oriented inheritance, `@property` encapsulation (preventing negative stock/prices), perishable goods with expiration tracking, and low-inventory alerts.

- **To run the demonstration**:
  ```bash
  python task4/main.py
  ```
  - Shows creation of standard and perishable products, stock increases/decreases, safety guards when removing more units than available, low-stock alerts, and a formatted valuation table.

- **To run unit tests**:
  ```bash
  python -m unittest task4/test_inventory.py
  ```

---

### Task 5: Weather Dashboard Using Public REST API
Fetches live weather conditions for any city. Works seamlessly with OpenWeatherMap API keys via `.env` or falls back to free live public weather data (Open-Meteo) with zero setup.

- **To test live weather fetching**:
  ```bash
  python task5/weather_dashboard.py Nairobi
  python task5/weather_dashboard.py London
  python task5/weather_dashboard.py Tokyo
  ```
  - Displays real-time temperature (in °C), feels-like, humidity percentage, wind speed, and weather condition.

- **To run automated mock unit tests** (100% offline):
  ```bash
  pytest task5/test_weather.py -v
  ```

---

### Task 6: Web Scraping & Job Skill Demand Analysis
Parses job listings using `BeautifulSoup`, checks `robots.txt` compliance, analyzes top in-demand skills and roles via `pandas`, and generates a city-skill breakdown visualization.

- **To run the analysis**:
  ```bash
  python task6/job_scraper.py
  ```
  - Parses job listings from `task6/jobs_sample.html`, prints top roles and skills, and saves the chart to `skills_by_city.png`.

- **To run unit tests**:
  ```bash
  python -m unittest task6/test_job_scraper.py
  ```

---

### Task 7: LLM-Powered Document Q&A (RAG Basics)
Splits sample company documents into chunks, builds a vector store with normalized term embeddings, and enforces a **hard confidence threshold** (0.35) below which it declines to answer with *"I don't know."* Supports live OpenAI API integration via `.env` with seamless fallback to local synthesis.

- **To test a relevant question (returns answer + citations)**:
  ```bash
  python task7/rag_tool.py "How many days of paid vacation do employees get?"
  ```
  - Expected output: Returns 25 days paid vacation with citations to `doc2_vacation_policy.txt`.

- **To test an out-of-domain question (strictly declines with 'I don't know')**:
  ```bash
  python task7/rag_tool.py "What is the capital of Mars and how to build a rocket?"
  ```
  - Expected output: Status `declined_below_threshold`, Confidence score $< 0.35$, Answer: `"I don't know."`

- **To run unit tests**:
  ```bash
  python -m unittest task7/test_rag_tool.py
  ```

---

### Task 8: AI-Assisted Code Review Tool
Inspects Python code for bugs (mutable defaults, zero division), PEP 8 compliance (line length), and refactoring opportunities, producing a structured JSON report and unified diff previews. Supports live OpenAI API integration via `.env` alongside an offline AST analysis engine.

- **To run code review with diff preview**:
  ```bash
  python task8/code_reviewer.py task8/sample_target.py --diff
  ```
  - Identifies 7 findings, verifies line numbers, marks unverifiable lines as approximate, displays before/after diffs, and saves `sample_target_review.json`.

- **To run unit tests**:
  ```bash
  python -m unittest task8/test_code_reviewer.py
  ```

---

### Task 9: AI Agent for a Two-Tool Task
Autonomous agent with a strict 5-step loop limit, tool dispatch (`calculator` and `file_writer`), and action-only logging (never logging internal reasoning). Supports live OpenAI step planning via `.env` alongside an offline deterministic goal planner.

- **To run the reference workflow**:
  ```bash
  python task9/agent.py --goal "What's 15% of 240, and save the answer to a file called result.txt?"
  ```
  - Calls `calculator` with `240 * 0.15` $\rightarrow$ gets `36.0`.
  - Calls `file_writer` saving `36.0` to `result.txt`.
  - Logs tool calls to `agent_execution.log` and console.
  - Reports: *"Calculated 36.0 and saved it to result.txt."*

- **To run unit tests**:
  ```bash
  python -m unittest task9/test_agent.py
  ```
