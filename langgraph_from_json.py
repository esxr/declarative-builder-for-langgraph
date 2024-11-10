from typing import TypedDict, Literal, Callable, Dict

from langgraph.graph import StateGraph, END
from utils.nodes import call_model, should_continue, tool_node
from utils.state import AgentState


# Define GraphConfig as per the original code
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]


# Placeholder functions (in practice, these would be actual implementations)
def call_model():
    pass


def tool_node():
    pass


def should_continue():
    pass


# END constant to represent the end of the graph
END = "__end__"

# General function registry to map function names to actual function references
function_registry = {
    "call_model": call_model,
    "tool_node": tool_node,
    "should_continue": should_continue,
}


# Function to retrieve a function reference from the registry
def get_function_reference(name: str) -> Callable:
    return function_registry.get(name, lambda: None)


# Generalized adapter function to reconstruct the imperative input
def build_graph_from_json(output_json: Dict) -> Callable:
    # Step 1: Initialize the graph with config
    workflow = StateGraph(AgentState, config_schema=GraphConfig)

    # Step 2: Add all nodes to the workflow based on the output JSON
    for node in output_json["nodes"]:
        node_id = node["id"]

        # Skip special start and end nodes in this step
        if node_id in ["__start__", "__end__"]:
            continue

        # Retrieve the function for this node
        function_name = node["data"].get("function")
        function_ref = get_function_reference(function_name)

        # Add the node with the associated function
        workflow.add_node(node_id, function_ref)

    # Step 3: Set the entry point if there's an edge from "__start__"
    for edge in output_json["edges"]:
        if edge["source"] == "__start__":
            workflow.set_entry_point(edge["target"])
            break

    # Step 4: Add edges to the workflow
    for edge in output_json["edges"]:
        source = edge["source"]
        target = edge["target"]

        # Skip "__start__" and "__end__" here, as they have special handling
        if source == "__start__" or target == "__end__":
            continue

        # Determine if the edge is conditional
        conditional = edge.get("conditional", "False") == "True"

        if conditional:
            # Retrieve the conditional function
            function_name = edge.get("function")
            condition_function = get_function_reference(function_name)

            # Define the mapping for conditional edges
            # TODO: THERE CAN BE MULTIPLE CONDITIONS
            mapping = {
                edge["data"]: target,
                "end": END,
            }

            # Add the conditional edge to the workflow
            workflow.add_conditional_edges(source, condition_function, mapping)
        else:
            # Add a normal edge if it's not conditional
            workflow.add_edge(source, target)

    # Step 5: Compile the workflow
    graph = workflow.compile()

    return graph


# Example usage
output_json = {
    "nodes": [
        {"id": "__start__", "type": "schema", "data": "__start__"},
        {"id": "agent", "type": "runnable", "data": {"function": "call_model"}},
        {"id": "action", "type": "runnable", "data": {"function": "tool_node"}},
        {"id": "__end__", "type": "schema", "data": "__end__"},
    ],
    "edges": [
        {"source": "__start__", "target": "agent"},
        {"source": "action", "target": "agent"},
        {
            "source": "agent",
            "target": "action",
            "data": "continue",
            "conditional": "True",
            "function": "should_continue",
        },
        {"source": "agent", "target": "__end__", "data": "end", "conditional": "True"},
    ],
}

# Reconstruct the graph
graph = build_graph_from_json(output_json)

print(graph.get_graph().to_json())  # Output the reconstructed graph in JSON format
