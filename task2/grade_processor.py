"""Student Grade Processor Module (Task 2).

Provides modular functions for validating scores, calculating averages,
finding highest and lowest scores, and assigning pass/fail status.
"""


class InvalidScoreError(Exception):
    """Raised when a student score is below 0 or above 100."""
    pass


def validate_score(score: float) -> float:
    """Validate that a score is a number between 0 and 100.

    Args:
        score: The numerical score to validate.

    Returns:
        The validated float score.

    Raises:
        InvalidScoreError: If score is less than 0 or greater than 100.
        TypeError: If score is not a numeric value.
    """
    if not isinstance(score, (int, float)):
        raise TypeError(f"Score must be a number, got {type(score).__name__}.")
    if score < 0 or score > 100:
        raise InvalidScoreError(f"Invalid score: {score}. Score must be between 0 and 100.")
    return float(score)


def calculate_average(students: list[dict]) -> float:
    """Calculate the average score for a list of student records.

    Args:
        students: List of student dicts, each containing a 'score' key.

    Returns:
        The average score as a float rounded to 2 decimal places.
    """
    if not students:
        return 0.0
    total = sum(validate_score(s["score"]) for s in students)
    return round(total / len(students), 2)


def get_highest_score(students: list[dict]) -> dict:
    """Find and return the student record with the highest score.

    Args:
        students: List of student dicts.

    Returns:
        The dictionary of the student with the highest score.
    """
    if not students:
        return {}
    for s in students:
        validate_score(s["score"])
    return max(students, key=lambda s: s["score"])


def get_lowest_score(students: list[dict]) -> dict:
    """Find and return the student record with the lowest score.

    Args:
        students: List of student dicts.

    Returns:
        The dictionary of the student with the lowest score.
    """
    if not students:
        return {}
    for s in students:
        validate_score(s["score"])
    return min(students, key=lambda s: s["score"])


def assign_pass_fail(students: list[dict], passing_score: float = 50.0) -> list[dict]:
    """Return a new list of student records with an added 'status' ('Pass' or 'Fail').

    Args:
        students: List of student dicts.
        passing_score: The minimum score required to pass (default: 50.0).

    Returns:
        A list of new student dicts including the 'status' field.
    """
    results = []
    for s in students:
        score = validate_score(s["score"])
        status = "Pass" if score >= passing_score else "Fail"
        updated = dict(s)
        updated["status"] = status
        results.append(updated)
    return results
