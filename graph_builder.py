from pathlib import Path

import networkx as nx
import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def find_csv_file():
    """
    Find the employee CSV file without depending on
    Windows/Linux filename capitalization.
    """

    possible_names = [
        "employees.csv",
        "Employees.csv",
        "employee.csv",
        "Employee.csv",
    ]

    for name in possible_names:
        path = DATA_DIR / name
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Employee CSV file was not found in: {DATA_DIR}\n"
        f"Expected one of: {', '.join(possible_names)}"
    )


# --------------------------------------------------
# Graph builder
# --------------------------------------------------

def build_employee_graph():
    """
    Build the employee knowledge graph.

    Canonical person nodes are Employee nodes.

    Relationships:
        Employee -> Department       WORKS_IN
        Employee -> Position         HAS_POSITION
        Employee -> Location         LOCATED_IN
        Employee -> Status           HAS_STATUS
        Employee -> Employee         REPORTS_TO
        Employee -> ExternalManager  REPORTS_TO
    """

    csv_path = find_csv_file()

    print(f"Loading employee data from: {csv_path}")

    df = pd.read_csv(csv_path)

    # Normalize column names so accidental spaces do not
    # cause KeyError problems.
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_columns = {
        "emp_id",
        "name",
        "department",
        "position",
        "email",
        "phone",
        "hire_date",
        "salary_inr",
        "location",
        "manager",
        "status",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required CSV columns: "
            + ", ".join(sorted(missing_columns))
        )

    graph = nx.MultiDiGraph()

    # --------------------------------------------------
    # STEP 1: Employee lookup
    # --------------------------------------------------

    employee_lookup = {}

    for _, employee in df.iterrows():
        name = str(employee["name"]).strip()

        if name and name.lower() != "nan":
            employee_lookup[name.lower()] = str(
                employee["emp_id"]
            ).strip()

    # --------------------------------------------------
    # STEP 2: Create employee nodes and relationships
    # --------------------------------------------------

    for _, employee in df.iterrows():

        emp_id = str(employee["emp_id"]).strip()
        name = str(employee["name"]).strip()

        employee_node = f"employee:{emp_id}"

        # ----------------------------------------------
        # Employee node
        # ----------------------------------------------

        salary = pd.to_numeric(
            employee["salary_inr"],
            errors="coerce",
        )

        graph.add_node(
            employee_node,
            node_type="Employee",
            emp_id=emp_id,
            name=name,
            email=str(employee["email"]).strip(),
            phone=str(employee["phone"]).strip(),
            hire_date=str(employee["hire_date"]).strip(),
            salary_inr=(
                float(salary)
                if pd.notna(salary)
                else None
            ),
        )

        # ----------------------------------------------
        # Department
        # ----------------------------------------------

        department = str(employee["department"]).strip()

        if department and department.lower() != "nan":
            department_node = f"department:{department}"

            graph.add_node(
                department_node,
                node_type="Department",
                name=department,
            )

            graph.add_edge(
                employee_node,
                department_node,
                relation="WORKS_IN",
            )

        # ----------------------------------------------
        # Position
        # ----------------------------------------------

        position = str(employee["position"]).strip()

        if position and position.lower() != "nan":
            position_node = f"position:{position}"

            graph.add_node(
                position_node,
                node_type="Position",
                name=position,
            )

            graph.add_edge(
                employee_node,
                position_node,
                relation="HAS_POSITION",
            )

        # ----------------------------------------------
        # Location
        # ----------------------------------------------

        location = str(employee["location"]).strip()

        if location and location.lower() != "nan":
            location_node = f"location:{location}"

            graph.add_node(
                location_node,
                node_type="Location",
                name=location,
            )

            graph.add_edge(
                employee_node,
                location_node,
                relation="LOCATED_IN",
            )

        # ----------------------------------------------
        # Status
        # ----------------------------------------------

        status = str(employee["status"]).strip()

        if status and status.lower() != "nan":
            status_node = f"status:{status}"

            graph.add_node(
                status_node,
                node_type="Status",
                name=status,
            )

            graph.add_edge(
                employee_node,
                status_node,
                relation="HAS_STATUS",
            )

        # ----------------------------------------------
        # Manager
        # ----------------------------------------------

        manager = str(employee["manager"]).strip()

        if manager and manager.lower() != "nan":

            manager_key = manager.lower()

            # If manager is also an employee, reuse the
            # existing Employee node.
            if manager_key in employee_lookup:

                manager_emp_id = employee_lookup[manager_key]
                manager_node = f"employee:{manager_emp_id}"

            else:
                # Manager exists in the source data but is
                # not an employee record.
                manager_node = f"external_manager:{manager}"

                graph.add_node(
                    manager_node,
                    node_type="ExternalManager",
                    name=manager,
                )

            graph.add_edge(
                employee_node,
                manager_node,
                relation="REPORTS_TO",
            )

    return graph


# --------------------------------------------------
# Test the graph builder
# --------------------------------------------------

if __name__ == "__main__":

    graph = build_employee_graph()

    print("\n========== GRAPH SUMMARY ==========")
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    employee = "employee:EMP001"

    if employee not in graph:
        print(f"\nEmployee node not found: {employee}")
    else:
        print(f"\n========== {employee} RELATIONSHIPS ==========")

        for _, target, data in graph.out_edges(
            employee,
            data=True,
        ):
            print(
                f"{data.get('relation')} -> {target}"
            )
