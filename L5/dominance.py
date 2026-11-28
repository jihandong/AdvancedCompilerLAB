import json
import sys

from L2.build_cfg import AdjTable, build_cfg, form_blocks

BlockSets = dict[str, set[str]]


def dominators(entry: str, succs: AdjTable, preds: AdjTable) -> BlockSets:
    """Map each reachable block to its dominators, including itself."""
    raise NotImplementedError("dominators")


def dominator_tree(dom: BlockSets) -> BlockSets:
    """Map each block to its immediate children, including leaves."""
    raise NotImplementedError("dominator_tree")


def dominance_frontier(dom: BlockSets, preds: AdjTable) -> BlockSets:
    """Map each reachable block to its dominance frontier."""
    raise NotImplementedError("dominance_frontier")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("dom", "tree", "frontier"):
        sys.exit("Usage: python3 -m L5.dominance {dom,tree,frontier}")

    analysis = sys.argv[1]
    program = json.load(sys.stdin)
    result = {}
    for function in program["functions"]:
        blocks = form_blocks(function["instrs"])
        succs, preds = build_cfg(blocks)
        entry = next(iter(blocks), None)
        dom = dominators(entry, succs, preds) if entry is not None else {}

        if analysis == "tree":
            sets = dominator_tree(dom)
        elif analysis == "frontier":
            sets = dominance_frontier(dom, preds)
        else:
            sets = dom
        result[function["name"]] = {label: sorted(nodes) for label, nodes in sets.items()}

    print(json.dumps(result, indent=2, sort_keys=True))
