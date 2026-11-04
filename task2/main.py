"""Main script to demonstrate student grade processing (Task 2)."""

from grade_processor import (
    InvalidScoreError,
    assign_pass_fail,
    calculate_average,
    get_highest_score,
    get_lowest_score,
)


def main():
    # Sample list of student records
    students = [
        {"name": "Alice", "score": 92.5},
        {"name": "Bob", "score": 45.0},
        {"name": "Charlie", "score": 78.0},
        {"name": "Diana", "score": 88.5},
        {"name": "Evan", "score": 38.0},
    ]

    print("--- Student Grade Processing ---")
    avg = calculate_average(students)
    top_student = get_highest_score(students)
    low_student = get_lowest_score(students)
    graded_list = assign_pass_fail(students, passing_score=50.0)

    print(f"Class Average: {avg:.2f}")
    print(f"Highest Score: {top_student['name']} ({top_student['score']})")
    print(f"Lowest Score : {low_student['name']} ({low_student['score']})")

    print("\n--- Student Results ---")
    for s in graded_list:
        print(f"  {s['name']:<10}: {s['score']:>5.1f} -> {s['status']}")

    # Demonstrate input validation error handling
    print("\n--- Testing Invalid Score Validation ---")
    invalid_students = [
        {"name": "Frank", "score": 105.0},  # Invalid score > 100
    ]
    try:
        calculate_average(invalid_students)
    except InvalidScoreError as e:
        print(f"Caught expected error: {e}")


if __name__ == "__main__":
    main()
