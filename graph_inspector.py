from graph_builder import build_employee_graph


def show_employee(graph, emp_id):

    employee_node = f"employee:{emp_id}"

    if employee_node not in graph:
        print("Employee not found.")
        return

    data = graph.nodes[employee_node]

    print("\nEMPLOYEE")
    print("-" * 40)

    for key, value in data.items():
        print(f"{key}: {value}")

    print("\nRELATIONSHIPS")
    print("-" * 40)

    for _, target, edge_data in graph.out_edges(
        employee_node,
        data=True
    ):
        target_data = graph.nodes[target]

        print(
            f"{edge_data['relation']} "
            f"-> "
            f"{target_data.get('name', target)}"
        )


if __name__ == "__main__":

    graph = build_employee_graph()

    print("Graph statistics")
    print("-" * 40)
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    show_employee(graph, "EMP001")