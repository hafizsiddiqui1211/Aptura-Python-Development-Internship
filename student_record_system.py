"""
================================================================================
 SMART STUDENT RECORD MANAGEMENT SYSTEM
 Aptura Tech Solutions - Python Development Internship (Batch 02)
 Week 01 Task - Task 01

 Author : Hafiz Wildan Ahmed Siddiqui
 Description:
    A menu-driven console application to manage student records with
    persistent file storage (JSON). Supports Add, Update, Delete, Search,
    and Display (sorted by GPA using a custom-built Merge Sort algorithm).
================================================================================
"""

import json
import os

DATA_FILE = "students_data.json"


# ==============================================================================
# 1. FILE HANDLING
# ==============================================================================
def load_students():
    """Load student records from the JSON data file into memory."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        print("[WARNING] Data file was corrupted or unreadable. Starting fresh.")
        return []


def save_students(students):
    """Persist the current in-memory list of students to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)


# ==============================================================================
# 2. QUESTION 01 - CUSTOM SORTING ALGORITHM (MERGE SORT)
# ==============================================================================
# Why Merge Sort? (full justification also included in the PDF report)
#   1. Guaranteed O(n log n) performance in ALL cases (best, average, worst) -
#      unlike Quick Sort, which degrades to O(n^2) on already-sorted or
#      reverse-sorted data - a realistic scenario for student records that
#      are frequently re-displayed after being entered in roll-number order.
#   2. It is STABLE: students who share the exact same GPA keep their
#      original relative order (e.g. insertion/roll-number order), which
#      matters for fair, predictable class ranking.
#   3. Divide-and-conquer structure scales cleanly to very large datasets
#      and adapts naturally to external/merge-based sorting when the data
#      no longer fits in memory (directly relevant to Question 02).
# ------------------------------------------------------------------------------
def merge_sort_by_gpa(students):
    """
    Custom implementation of Merge Sort (no built-in sort()/sorted() used).
    Sorts a list of student dictionaries by GPA in DESCENDING order
    (highest GPA first).
    """
    # Base case: a list of 0 or 1 elements is already "sorted"
    if len(students) <= 1:
        return students

    mid = len(students) // 2
    left_half = merge_sort_by_gpa(students[:mid])
    right_half = merge_sort_by_gpa(students[mid:])

    return _merge(left_half, right_half)


def _merge(left, right):
    """Merge two GPA-sorted (descending) lists into a single sorted list."""
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        # ">=" keeps the merge stable (preserves original relative order)
        if left[i]["gpa"] >= right[j]["gpa"]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append any remaining elements
    while i < len(left):
        merged.append(left[i])
        i += 1
    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged


# ==============================================================================
# 3. CRUD OPERATIONS
# ==============================================================================
def find_index_by_roll(students, roll_no):
    """Linear search helper - returns the index of a student by roll number,
    or -1 if not found."""
    for idx, s in enumerate(students):
        if s["roll_no"].lower() == roll_no.lower():
            return idx
    return -1


def get_valid_gpa():
    """Prompt until a valid GPA (0.0 - 4.0) is entered."""
    while True:
        raw = input("Enter GPA (0.0 - 4.0): ").strip()
        try:
            gpa = float(raw)
            if 0.0 <= gpa <= 4.0:
                return round(gpa, 2)
            print("[ERROR] GPA must be between 0.0 and 4.0. Try again.")
        except ValueError:
            print("[ERROR] Please enter a valid number.")


def add_student(students):
    print("\n--- ADD NEW STUDENT ---")
    roll_no = input("Enter Roll No (e.g. BSE-23F-081): ").strip()

    if not roll_no:
        print("[ERROR] Roll No cannot be empty.")
        return

    if find_index_by_roll(students, roll_no) != -1:
        print(f"[ERROR] A student with Roll No '{roll_no}' already exists.")
        return

    name = input("Enter Name: ").strip()
    while not name:
        name = input("Name cannot be empty. Enter Name: ").strip()

    department = input("Enter Department: ").strip() or "N/A"
    gpa = get_valid_gpa()

    student = {
        "roll_no": roll_no,
        "name": name,
        "department": department,
        "gpa": gpa,
    }
    students.append(student)
    save_students(students)
    print(f"[SUCCESS] Student '{name}' ({roll_no}) added successfully.")


def update_student(students):
    print("\n--- UPDATE STUDENT ---")
    roll_no = input("Enter Roll No of student to update: ").strip()
    idx = find_index_by_roll(students, roll_no)

    if idx == -1:
        print(f"[ERROR] No student found with Roll No '{roll_no}'.")
        return

    student = students[idx]
    print(f"Current details -> Name: {student['name']}, "
          f"Department: {student['department']}, GPA: {student['gpa']}")
    print("Leave a field blank to keep its current value.\n")

    new_name = input(f"New Name [{student['name']}]: ").strip()
    new_dept = input(f"New Department [{student['department']}]: ").strip()
    new_gpa_raw = input(f"New GPA [{student['gpa']}]: ").strip()

    if new_name:
        student["name"] = new_name
    if new_dept:
        student["department"] = new_dept
    if new_gpa_raw:
        try:
            gpa_val = float(new_gpa_raw)
            if 0.0 <= gpa_val <= 4.0:
                student["gpa"] = round(gpa_val, 2)
            else:
                print("[WARNING] GPA out of range (0.0-4.0). GPA not updated.")
        except ValueError:
            print("[WARNING] Invalid GPA input. GPA not updated.")

    students[idx] = student
    save_students(students)
    print(f"[SUCCESS] Record for '{student['name']}' updated successfully.")


def delete_student(students):
    print("\n--- DELETE STUDENT ---")
    roll_no = input("Enter Roll No of student to delete: ").strip()
    idx = find_index_by_roll(students, roll_no)

    if idx == -1:
        print(f"[ERROR] No student found with Roll No '{roll_no}'.")
        return

    confirm = input(
        f"Are you sure you want to delete '{students[idx]['name']}' "
        f"({roll_no})? (y/n): "
    ).strip().lower()

    if confirm == "y":
        removed = students.pop(idx)
        save_students(students)
        print(f"[SUCCESS] Student '{removed['name']}' deleted successfully.")
    else:
        print("[CANCELLED] Delete operation cancelled.")


def search_student(students):
    print("\n--- SEARCH STUDENT ---")
    print("Search by: 1) Roll No   2) Name")
    choice = input("Enter choice (1/2): ").strip()

    results = []
    if choice == "1":
        roll_no = input("Enter Roll No: ").strip().lower()
        results = [s for s in students if s["roll_no"].lower() == roll_no]
    elif choice == "2":
        name_query = input("Enter Name (partial match allowed): ").strip().lower()
        results = [s for s in students if name_query in s["name"].lower()]
    else:
        print("[ERROR] Invalid choice.")
        return

    if not results:
        print("[INFO] No matching student record found.")
    else:
        print(f"\n{len(results)} record(s) found:")
        _print_table(results)


def display_all(students):
    print("\n--- ALL STUDENT RECORDS (Sorted by GPA: Highest -> Lowest) ---")
    if not students:
        print("[INFO] No student records to display.")
        return

    sorted_students = merge_sort_by_gpa(students.copy())
    _print_table(sorted_students, rank=True)


def _print_table(students, rank=False):
    """Pretty-print a list of student dicts as a formatted table."""
    if rank:
        header = f"{'Rank':<6}{'Roll No':<16}{'Name':<20}{'Department':<28}{'GPA':<6}"
    else:
        header = f"{'Roll No':<16}{'Name':<20}{'Department':<28}{'GPA':<6}"
    print(header)
    print("-" * len(header))

    for i, s in enumerate(students, start=1):
        if rank:
            print(f"{i:<6}{s['roll_no']:<16}{s['name']:<20}{s['department']:<28}{s['gpa']:<6}")
        else:
            print(f"{s['roll_no']:<16}{s['name']:<20}{s['department']:<28}{s['gpa']:<6}")


# ==============================================================================
# 4. MENU-DRIVEN INTERFACE
# ==============================================================================
def print_menu():
    print("\n" + "=" * 50)
    print("     SMART STUDENT RECORD MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Add Student")
    print("2. Update Student")
    print("3. Delete Student")
    print("4. Search Student")
    print("5. Display All Records (Sorted by GPA)")
    print("6. Exit")
    print("=" * 50)


def main():
    students = load_students()
    print("Welcome to the Smart Student Record Management System!")
    print(f"[INFO] Loaded {len(students)} existing record(s) from '{DATA_FILE}'.")

    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            update_student(students)
        elif choice == "3":
            delete_student(students)
        elif choice == "4":
            search_student(students)
        elif choice == "5":
            display_all(students)
        elif choice == "6":
            print("\n[INFO] All data saved. Exiting the system. Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
