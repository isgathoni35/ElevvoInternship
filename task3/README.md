# Task 3: Automated File Organizer

A Python script that scans a target directory and organizes files into extension-based subfolders with collision safety, dry-run preview, and file logging.

---

## Features
- **Extension Sorting**: Automatically moves files into subfolders corresponding to their file extension (e.g., `.pdf` $\rightarrow$ `pdf/`, `.txt` $\rightarrow$ `txt/`).
- **Guaranteed No-Overwrite**: If a file with the same name already exists in the destination folder, the incoming file is safely renamed (e.g. `file_1.txt`, `file_2.txt`).
- **Summary & Logging (Bonus)**: Prints move summaries to the console and logs all actions to `organizer.log`.
- **Dry-Run Mode (Bonus)**: `--dry-run` flag previews all moves without altering files on disk.

---

## Files
- `file_organizer.py`: Core file organizer script and CLI.
- `test_file_organizer.py`: Unit tests for sorting, conflict handling, and dry-run mode.
- `organizer.log`: Output log file generated during runs.

---

## How to Run

### 1. Organize a Directory
```bash
python task3/file_organizer.py path/to/target/folder
```

### 2. Preview with Dry-Run
```bash
python task3/file_organizer.py path/to/target/folder --dry-run
```

### 3. Run Unit Tests
```bash
python -m unittest task3/test_file_organizer.py
```
