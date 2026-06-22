"""
Unit tests for oxygent.utils.data_utils
"""

from oxygent.utils.data_utils import add_post_and_child_node_ids


# ──────────────────────────────────────────────────────────────────────────────
# add_post_and_child_node_ids
# ──────────────────────────────────────────────────────────────────────────────
def test_add_post_and_child_node_ids_basic():
    """
    A ─┬─► B        (pre-edge)
        └─► C        (pre-edge)
        │
        └── D        (father-child)
    """
    nodes = [
        {"node_id": "A", "pre_node_ids": [], "father_node_id": ""},
        {"node_id": "B", "pre_node_ids": ["A"], "father_node_id": ""},
        {"node_id": "C", "pre_node_ids": ["A"], "father_node_id": ""},
        {"node_id": "D", "pre_node_ids": [], "father_node_id": "A"},
    ]

    add_post_and_child_node_ids(nodes)

    a = next(n for n in nodes if n["node_id"] == "A")
    b = next(n for n in nodes if n["node_id"] == "B")
    c = next(n for n in nodes if n["node_id"] == "C")
    d = next(n for n in nodes if n["node_id"] == "D")

    assert set(a["post_node_ids"]) == {"B", "C"}
    assert a["child_node_ids"] == ["D"]

    for leaf in (b, c, d):
        assert leaf["post_node_ids"] == []
        assert leaf["child_node_ids"] == []


def test_add_post_and_child_missing_pre():
    nodes = [
        {"node_id": "X", "pre_node_ids": ["no_exist"], "father_node_id": ""},
        {"node_id": "Y", "pre_node_ids": ["X"], "father_node_id": "no_exist"},
    ]
    add_post_and_child_node_ids(nodes)
    x = nodes[0]
    assert x["post_node_ids"] == ["Y"]
    assert x["child_node_ids"] == []
