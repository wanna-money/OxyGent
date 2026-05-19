from typing import Any


def add_post_and_child_node_ids(nodes: list[dict[str, Any]]) -> None:
    """Adds `post_node_ids` and `child_node_ids` fields to each node.

    Each node will gain:
    - post_node_ids: A list of node_ids for which this node is a pre_node.
    - child_node_ids: A list of node_ids that are direct children of this node (based on father_node_id).

    Args:
        nodes (List[Dict]): Each node dictionary must contain 'node_id' and 'pre_node_ids' fields.

    Returns:
        None. Modifies the input `nodes` list in place.
    """
    # Build a mapping from node_id to node
    node_map = {n["node_id"]: n for n in nodes}
    # Initialize post_node_ids and child_node_ids
    for n in nodes:
        n["post_node_ids"] = []
        n["child_node_ids"] = []
    # Populate post_node_ids based on pre_node_ids
    for n in nodes:
        for pre in n["pre_node_ids"]:
            if pre and pre in node_map:
                node_map[pre]["post_node_ids"].append(n["node_id"])
        father_node_id = n["father_node_id"]
        if father_node_id and father_node_id in node_map:
            node_map[father_node_id]["child_node_ids"].append(n["node_id"])
