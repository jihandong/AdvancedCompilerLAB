import json
import sys

from L2.build_cfg import AdjTable, build_cfg, form_blocks

BlockSets = dict[str, set[str]]


def dominators(entry: str, succs: AdjTable, preds: AdjTable) -> BlockSets:
    """Map each reachable block to its dominators, including itself."""
    # 1. DFS to get reachable blocks, only consider these.
    reachable: set[str] = set()
    stack: list[str] = [entry]

    while stack:
        block = stack.pop()
        if block not in reachable:
            reachable.add(block)
            stack.extend(succs[block])

    # 2. Collect dominators till convegence
    dom: BlockSets = {block: reachable for block in reachable}
    dom[entry] = {entry}

    while True:
        changed = False
        for block in reachable:
            if block != entry:
                incoming = [p for p in preds[block] if p in reachable]
                new_dom = set.intersection(*(dom[p] for p in incoming))
                new_dom.add(block)
                if dom[block] != new_dom:
                    dom[block] = new_dom
                    changed = True
        if not changed: break

    return dom


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
