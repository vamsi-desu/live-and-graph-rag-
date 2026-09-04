import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "database" / "employees.db"


def get_connection():
    """Create a connection to the employee SQLite database."""
    return sqlite3.connect(DB_PATH)


def get_employees(
    department=None,
    employee_id=None,
    location=None,
    status=None
):
    """
    Retrieve employees using structured filters.
    """

    query = """
        SELECT
            emp_id,
            name,
            department,
            position,
            email,
            phone,
            hire_date,
            salary_inr,
            location,
            manager,
            status
        FROM employees
        WHERE 1=1
    """

    parameters = []

    if department:
        query += " AND LOWER(department) = LOWER(?)"
        parameters.append(department)

    if employee_id:
        query += " AND LOWER(emp_id) = LOWER(?)"
        parameters.append(employee_id)

    if location:
        query += " AND LOWER(location) = LOWER(?)"
        parameters.append(location)

    if status:
        query += " AND LOWER(status) = LOWER(?)"
        parameters.append(status)

    query += " ORDER BY emp_id"

    with get_connection() as connection:
        cursor = connection.execute(query, parameters)
        rows = cursor.fetchall()

    return rows


def format_employees(rows):
    """Convert database rows into readable context."""

    if not rows:
        return "No employees matched the requested filters."

    context = []

    for row in rows:
        (
            emp_id,
            name,
            department,
            position,
            email,
            phone,
            hire_date,
            salary_inr,
            location,
            manager,
            status
        ) = row

        employee = f"""
Employee ID: {emp_id}
Name: {name}
Department: {department}
Position: {position}
Email: {email}
Phone: {phone}
Hire Date: {hire_date}
Salary: {salary_inr} INR
Location: {location}
Manager: {manager}
Status: {status}
""".strip()

        context.append(employee)

    return "\n\n".join(context)