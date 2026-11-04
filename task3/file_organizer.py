"""Automated File Organizer (Task 3).

Scans a target directory, sorts files into subfolders by extension,
safely avoids overwriting existing files via unique renaming,
and optionally previews moves (--dry-run) and logs to file.
"""

import argparse
import logging
import os
import shutil
from pathlib import Path


def setup_logger(log_to_file=True, log_filename="organizer.log"):
    """Configure standard logging to file and console."""
    logger = logging.getLogger("FileOrganizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional file logging (Bonus)
    if log_to_file:
        fh = logging.FileHandler(log_filename, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_unique_destination(dest_folder: Path, filename: str) -> Path:
    """Generate a collision-safe destination path to ensure no file is ever overwritten.

    If 'report.txt' exists, returns 'report_1.txt', 'report_2.txt', etc.
    """
    dest_path = dest_folder / filename
    if not dest_path.exists():
        return dest_path

    stem = dest_path.stem
    suffix = dest_path.suffix
    counter = 1

    while True:
        candidate_name = f"{stem}_{counter}{suffix}"
        candidate_path = dest_folder / candidate_name
        if not candidate_path.exists():
            return candidate_path
        counter += 1


def organize_directory(target_path: str, dry_run: bool = False, logger: logging.Logger = None) -> list:
    """Scan target directory and move files into subfolders by extension."""
    if logger is None:
        logger = setup_logger(log_to_file=False)

    target_dir = Path(target_path).resolve()

    if not target_dir.exists():
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    if not target_dir.is_dir():
        logger.error(f"Target path is not a directory: {target_dir}")
        return []

    # Read items in target directory
    try:
        entries = list(target_dir.iterdir())
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory '{target_dir}': {e}")
        return []

    # Filter only regular files (ignore existing subdirectories to avoid recursive moves)
    files_to_move = [e for e in entries if e.is_file()]

    if not files_to_move:
        logger.info(f"No files found to organize in: {target_dir}")
        return []

    summary = []

    for file_path in files_to_move:
        # Determine extension or use 'no_extension'
        ext = file_path.suffix.lstrip(".").lower()
        subfolder_name = ext if ext else "no_extension"
        dest_folder = target_dir / subfolder_name

        # Calculate collision-safe destination path
        safe_dest_path = get_unique_destination(dest_folder, file_path.name)

        op_desc = {
            "file": file_path.name,
            "source": str(file_path),
            "destination": str(safe_dest_path),
            "status": "dry-run" if dry_run else "moved"
        }

        if dry_run:
            logger.info(f"[DRY-RUN] Would move: '{file_path.name}' -> '{safe_dest_path.relative_to(target_dir)}'")
        else:
            try:
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(safe_dest_path))
                logger.info(f"[MOVED] '{file_path.name}' -> '{safe_dest_path.relative_to(target_dir)}'")
            except PermissionError as e:
                logger.error(f"Permission denied moving '{file_path.name}': {e}")
                op_desc["status"] = "error_permission"
            except OSError as e:
                logger.error(f"Error moving '{file_path.name}': {e}")
                op_desc["status"] = "error_os"

        summary.append(op_desc)

    return summary


def main():
    """CLI interface for the File Organizer."""
    parser = argparse.ArgumentParser(description="Organize files in a directory by file extension.")
    parser.add_argument("target", help="Target directory to scan and organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview moves without modifying any files")
    parser.add_argument("--log", default="organizer.log", help="Path to write log file (default: organizer.log)")
    args = parser.parse_args()

    logger = setup_logger(log_to_file=True, log_filename=args.log)
    mode_str = " (DRY-RUN MODE)" if args.dry_run else ""
    logger.info(f"Starting organization for: {args.target}{mode_str}")

    results = organize_directory(args.target, dry_run=args.dry_run, logger=logger)
    logger.info(f"Completed. Total files processed: {len(results)}")


if __name__ == "__main__":
    main()
