from database import get_employees, format_employees
from generator import generate_answer


# --------------------------------------------------
# STRUCTURED RAG QUERY
# --------------------------------------------------

def structured_rag_query(
    question,
    department=None,
    employee_id=None,
    location=None,
    status=None
):
    """
    Execute a structured employee query.

    Structured data is retrieved directly from SQLite
    using exact filters.
    """

    print("\nSTRUCTURED RAG")
    print("-------------------------")

    print(f"Question: {question}")

    # --------------------------------------------------
    # RETRIEVE FROM DATABASE
    # --------------------------------------------------

    rows = get_employees(
        department=department,
        employee_id=employee_id,
        location=location,
        status=status
    )

    # --------------------------------------------------
    # FORMAT DATABASE RESULTS
    # --------------------------------------------------

    context = format_employees(rows)

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print("\nSTRUCTURED CONTEXT")
    print("-------------------------")
    print(context)

    # --------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------

    answer = generate_answer(
        question,
        context
    )

    print("\nFINAL ANSWER")
    print("-------------------------")

    return answer


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    answer = structured_rag_query(
        question="Which employees work in Engineering?",
        department="Engineering"
    )

    print(answer)