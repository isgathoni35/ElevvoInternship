"""Student Grade Processor Module.

Provides functions for validating scores, calculating class averages,
finding highest and lowest scores, and assigning pass/fail status.
"""


class InvalidScoreError(Exception):
    """Raised when a student score is below 0 or above 100."""
    pass


def validate_score(score: float) -> float:
    """Validate that a score is a number between 0 and 100."""
    if not isinstance(score, (int, float)):
        raise TypeError(f"Score must be a number, got {type(score).__name__}.")
    if score < 0 or score > 100:
        raise InvalidScoreError(f"Invalid score: {score}. Score must be between 0 and 100.")
    return float(score)


def calculate_average(students: list[dict]) -> float:
    """Calculate the average score for a list of student records."""
    if not students:
        return 0.0
    total = sum(validate_score(s["score"]) for s in students)
    return round(total / len(students), 2)


def get_highest_score(students: list[dict]) -> dict:
    """Find and return the student record with the highest score."""
    if not students:
        return {}
    for s in students:
        validate_score(s["score"])
    return max(students, key=lambda s: s["score"])


def get_lowest_score(students: list[dict]) -> dict:
    """Find and return the student record with the lowest score."""
    if not students:
        return {}
    for s in students:
        validate_score(s["score"])
    return min(students, key=lambda s: s["score"])


def assign_pass_fail(students: list[dict], passing_score: float = 50.0) -> list[dict]:
    """Return a new list of student records with an added 'status' ('Pass' or 'Fail')."""
    results = []
    for s in students:
        score = validate_score(s["score"])
        status = "Pass" if score >= passing_score else "Fail"
        updated = dict(s)
        updated["status"] = status
        results.append(updated)
    return results
