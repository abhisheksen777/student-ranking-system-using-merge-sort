"""
Merge Sort Implementation for Student Records
=============================================
This module implements the Merge Sort algorithm manually.
It sorts student objects in DESCENDING order based on marks.
No built-in sorting functions are used.
"""


def merge_sort(students):
    """
    MERGE SORT - Divide and Conquer Algorithm
    =========================================

    DIVIDE: Split the list into two halves recursively until
            each sublist has 0 or 1 element.
    CONQUER: Recursively sort each half.
    COMBINE: Merge the sorted halves back together by comparing marks.

    Args:
        students: List of student dictionaries with keys:
                  'roll', 'name', 'marks'

    Returns:
        List of student dictionaries sorted in descending order by marks.
    """
    # Base case: a list of 0 or 1 elements is already sorted
    if len(students) <= 1:
        return students

    # DIVIDE step: Find the middle point and split into two halves
    mid = len(students) // 2
    left_half = students[:mid]
    right_half = students[mid:]

    # CONQUER step: Recursively sort both halves
    left_sorted = merge_sort(left_half)
    right_sorted = merge_sort(right_half)

    # COMBINE step: Merge the sorted halves
    return merge(left_sorted, right_sorted)


def merge(left, right):
    """
    MERGE - Combine two sorted lists into one sorted list.
    =========================================

    Compare elements from both lists and merge them in
    descending order based on marks.

    Args:
        left: Left sorted sublist of student dictionaries
        right: Right sorted sublist of student dictionaries

    Returns:
        Merged sorted list in descending order by marks.
    """
    result = []
    i = 0  # Index for left sublist
    j = 0  # Index for right sublist

    # Compare elements from both sublists and add the larger one first
    # (for descending order)
    while i < len(left) and j < len(right):
        if left[i]['marks'] >= right[j]['marks']:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add any remaining elements from the left sublist
    while i < len(left):
        result.append(left[i])
        i += 1

    # Add any remaining elements from the right sublist
    while j < len(right):
        result.append(right[j])
        j += 1

    return result


def generate_ranks(sorted_students):
    """
    Generate competition ranks after sorting.
    ========================================
    Uses competition ranking (ties get the same rank, next rank skips).
    Example: 96→1, 91→2, 91→2, 85→4

    Args:
        sorted_students: List of student dictionaries sorted in
                         descending order by marks.

    Returns:
        List of student dictionaries with an added 'rank' key.
    """
    if not sorted_students:
        return []

    ranked_students = []
    current_rank = 1

    for idx, student in enumerate(sorted_students):
        if idx == 0:
            # First student always gets rank 1
            current_rank = 1
        else:
            # If marks are the same as previous student, same rank
            if student['marks'] == sorted_students[idx - 1]['marks']:
                current_rank = ranked_students[-1]['rank']
            else:
                # Otherwise rank = index + 1 (competition ranking)
                current_rank = idx + 1

        # Create a copy with the rank added
        ranked_student = dict(student)
        ranked_student['rank'] = current_rank
        ranked_students.append(ranked_student)

    return ranked_students


def get_statistics(students):
    """
    Calculate basic statistics from a list of students.

    Args:
        students: List of student dictionaries.

    Returns:
        Dictionary with total, highest, average, lowest marks.
    """
    if not students:
        return {
            'total': 0,
            'highest': 0,
            'average': 0,
            'lowest': 0
        }

    marks = [s['marks'] for s in students]
    total = len(students)
    highest = max(marks)
    lowest = min(marks)
    average = sum(marks) / total

    return {
        'total': total,
        'highest': highest,
        'average': round(average, 2),
        'lowest': lowest
    }
