from difflib import get_close_matches
from database import get_employees, format_employees

from graph_builder import build_employee_graph
from generator import generate_answer


# --------------------------------------------------
# LOAD GRAPH
# --------------------------------------------------

graph = build_employee_graph()


# --------------------------------------------------
# FIND EMPLOYEE
# --------------------------------------------------

def find_employee(employee_name):
    """
    Find an employee node using exact or fuzzy name matching.
    """

    employee_name = employee_name.strip().lower()

    employees = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "Employee":
            employees.append(
                {
                    "node": node,
                    "name": data.get("name", ""),
                }
            )

    # Exact match
    for employee in employees:
        if employee["name"].lower() == employee_name:
            return employee["node"]

    # Fuzzy match
    names = [employee["name"].lower() for employee in employees]

    matches = get_close_matches(
        employee_name,
        names,
        n=1,
        cutoff=0.6,
    )

    if matches:
        matched_name = matches[0]

        for employee in employees:
            if employee["name"].lower() == matched_name:
                return employee["node"]

    return None


# --------------------------------------------------
# EMPLOYEE PROPERTIES
# --------------------------------------------------

def format_employee(node):
    """
    Format an employee node as readable context.
    """

    data = graph.nodes[node]

    lines = [
        f"Employee: {data.get('name')}",
        f"Emp ID: {data.get('emp_id')}",
        f"Email: {data.get('email')}",
        f"Phone: {data.get('phone')}",
        f"Hire Date: {data.get('hire_date')}",
        f"Salary: {data.get('salary_inr')} INR",
    ]

    return "\n".join(lines)


# --------------------------------------------------
# DIRECT RELATIONSHIPS
# --------------------------------------------------

def get_direct_relationships(employee_node):
    """
    Retrieve only relationships directly connected
    to the requested employee.

    IMPORTANT:
    We do NOT traverse through shared nodes such as:
        Engineering
        Active
        Gurugram

    because those nodes are shared by many employees.
    """

    relationships = []

    for _, target, data in graph.out_edges(
        employee_node,
        data=True,
    ):
        relation = data.get("relation")
        target_data = graph.nodes[target]

        relationships.append(
            {
                "source": employee_node,
                "target": target,
                "relation": relation,
                "target_data": target_data,
            }
        )

    return relationships


# --------------------------------------------------
# FORMAT DIRECT RELATIONSHIPS
# --------------------------------------------------

def format_relationships(employee_node):
    """
    Convert direct employee relationships into context.
    """

    relationships = get_direct_relationships(employee_node)

    lines = []

    for item in relationships:

        relation = item["relation"]
        target_data = item["target_data"]

        source_name = graph.nodes[employee_node].get(
            "name",
            employee_node,
        )

        target_name = target_data.get(
            "name",
            item["target"],
        )

        lines.append(
            f"{source_name} --{relation}--> {target_name}"
        )

    return lines


# --------------------------------------------------
# GET TARGET EMPLOYEE FROM RELATIONSHIP
# --------------------------------------------------

def get_related_employee(
    employee_node,
    relation_name,
):
    """
    Follow a specific relationship from an employee.

    Example:

        Kevin Davis
             |
        REPORTS_TO
             |
             v
        Jennifer Mehta
    """

    for _, target, data in graph.out_edges(
        employee_node,
        data=True,
    ):

        if data.get("relation") == relation_name:

            target_data = graph.nodes[target]

            if target_data.get("node_type") in (
                "Employee",
                "ExternalManager",
            ):
                return target

    return None


# --------------------------------------------------
# TARGETED MULTI-HOP RETRIEVAL
# --------------------------------------------------

def retrieve_targeted_graph(employee_node, question):
    """
    Retrieve only the graph information required
    for the question.

    This replaces broad BFS traversal.
    """

    question_lower = question.lower()

    context_parts = []

    # --------------------------------------------------
    # STEP 1: Always include requested employee
    # --------------------------------------------------

    context_parts.append(
        format_employee(employee_node)
    )

    # --------------------------------------------------
    # STEP 2: Direct relationships
    # --------------------------------------------------

    direct_relationships = format_relationships(
        employee_node
    )

    if direct_relationships:

        context_parts.append(
            "\nGRAPH RELATIONSHIPS:"
        )

        context_parts.extend(
            direct_relationships
        )

    # --------------------------------------------------
    # STEP 3: Manager question
    # --------------------------------------------------

    manager_keywords = [
        "manager",
        "reports to",
        "supervisor",
    ]

    asks_manager = any(
        keyword in question_lower
        for keyword in manager_keywords
    )

    if asks_manager:

        manager_node = get_related_employee(
            employee_node,
            "REPORTS_TO",
        )

        if manager_node:

            manager_data = graph.nodes[manager_node]

            context_parts.append(
                "\nMANAGER INFORMATION:"
            )

            context_parts.append(
                f"Manager: {manager_data.get('name')}"
            )

            # If manager is an actual employee,
            # include their employee properties.
            if manager_data.get("node_type") == "Employee":

                context_parts.append(
                    format_employee(manager_node)
                )

                # Manager's direct relationships
                manager_relationships = (
                    format_relationships(manager_node)
                )

                if manager_relationships:

                    context_parts.append(
                        "\nMANAGER RELATIONSHIPS:"
                    )

                    context_parts.extend(
                        manager_relationships
                    )

    # --------------------------------------------------
    # STEP 4: Department of manager
    # --------------------------------------------------

    asks_manager_department = (
        asks_manager
        and "department" in question_lower
    )

    if asks_manager_department:

        manager_node = get_related_employee(
            employee_node,
            "REPORTS_TO",
        )

        if manager_node:

            for _, target, data in graph.out_edges(
                manager_node,
                data=True,
            ):

                if data.get("relation") == "WORKS_IN":

                    department_name = graph.nodes[
                        target
                    ].get("name")

                    context_parts.append(
                        "\nMANAGER DEPARTMENT:"
                    )

                    context_parts.append(
                        f"{graph.nodes[manager_node].get('name')} "
                        f"--WORKS_IN--> "
                        f"{department_name}"
                    )

    return "\n".join(context_parts)


# --------------------------------------------------
# MAIN GRAPH RAG QUERY
# --------------------------------------------------

def graph_rag_query(question, employee_name):
    """
    Execute targeted Graph RAG.
    """

    print("\nGRAPH RAG")
    print("-------------------------")

    print(
        f"Searching employee: {employee_name}"
    )

    employee_node = find_employee(
        employee_name
    )

    if not employee_node:

        return (
            "Employee not found in the employee graph."
        )

    actual_name = graph.nodes[
        employee_node
    ].get("name")

    print(
        f"Employee found: {actual_name}"
    )

    # --------------------------------------------------
    # TARGETED RETRIEVAL
    # --------------------------------------------------

    context = retrieve_targeted_graph(
        employee_node,
        question,
    )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print("\nGRAPH CONTEXT")
    print("-------------------------")
    print(context)

    # --------------------------------------------------
    # GENERATION
    # --------------------------------------------------

    answer = generate_answer(
        question,
        context,
    )

    print("\nFINAL ANSWER")
    print("-------------------------")

    return answer


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    questions = [
        "Who is Kevin Davis?",
        "Who is Kevin Davis's manager?",
        "What department does Kevin Davis's manager work in?",
    ]

    for question in questions:

        print("\n===================================")
        print("QUESTION")
        print("===================================")
        print(question)

        answer = graph_rag_query(
            question,
            "Kevin Davis",
        )

        print("\nANSWER")
        print("-------------------------")
        print(answer)