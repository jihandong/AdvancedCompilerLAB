import json
import sys

from L2.build_cfg import AdjTable, Blocks, build_cfg, form_blocks

VarTable = dict[str, set[str]]


def liveness(blocks: Blocks, succs: AdjTable, preds: AdjTable) -> tuple[VarTable, VarTable]:
    """Return (live_in, live_out), with each table keyed by block name."""
    live_in: VarTable = {label: set() for label in blocks}
    live_out: VarTable = {label: set() for label in blocks}
    uses: VarTable = {label: set() for label in blocks} # use before defined
    defs: VarTable = {label: set() for label in blocks} # all defines
    worklist: set[str] = set(blocks)

    # 1. Collect uses and defs
    for label, block in blocks.items():
        for instr in block:
            for arg in instr.get("args", ()):
                if arg not in defs[label]:
                    uses[label].add(arg)
            if "dest" in instr:
                defs[label].add(instr["dest"])

    # 2. update liveness Variables In/Out till convegence
    while worklist:
        label = worklist.pop()

        # XXX by reduce + lambda, might easier to abstract to DFA
        new_out = set()
        for succ in succs[label]:
            new_out.update(live_in[succ])
        live_out[label] = new_out

        new_in = uses[label] | (live_out[label] - defs[label])

        if live_in[label] != new_in:
            live_in[label] = new_in
            worklist.update(preds[label])

    return live_in, live_out


if __name__ == "__main__":
    program = json.load(sys.stdin)
    result = {}
    for function in program["functions"]:
        blocks = form_blocks(function["instrs"])
        succs, preds = build_cfg(blocks)
        live_in, live_out = liveness(blocks, succs, preds)
        result[function["name"]] = {
            name: {
                "in": sorted(live_in[name]),
                "out": sorted(live_out[name])
            }
            for name in blocks
        }
    print(json.dumps(result, indent=2))
