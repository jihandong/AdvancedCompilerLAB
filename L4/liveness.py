import json
import sys
from collections.abc import Callable, Iterable
from typing import TypeVar

from L2.build_cfg import AdjTable, Blocks, build_cfg, form_blocks

VarTable = dict[str, set[str]]
T = TypeVar("T")

def data_flow_analysis(
    succs: AdjTable,
    preds: AdjTable,
    *,
    forward: bool,
    init: Callable[[], T],
    merge: Callable[[Iterable[T]], T], # merge the inputs
    transfer: Callable[[str, T], T], # transfer into output
) -> tuple[dict[str, T], dict[str, T]]:
    in_blocks, out_blocks = (preds, succs) if forward else (succs, preds)
    inputs  = {label: init() for label in succs}
    outputs = {label: init() for label in succs}
    worklist: set[str] = set(succs)

    while worklist:
        label = worklist.pop()
        inputs[label] = merge(outputs[b] for b in in_blocks[label])
        new_out = transfer(label, inputs[label])
        if outputs[label] != new_out:
            outputs[label] = new_out
            worklist.update(out_blocks[label])

    return (inputs, outputs) if forward else (outputs, inputs)

def record_vars(blocks: Blocks) -> tuple[VarTable, VarTable]:
    uses: VarTable = {label: set() for label in blocks} # use before defined
    defs: VarTable = {label: set() for label in blocks} # all defines

    for label, block in blocks.items():
        for instr in block:
            for arg in instr.get("args", ()):
                if arg not in defs[label]:
                    uses[label].add(arg)
            if "dest" in instr:
                defs[label].add(instr["dest"])

    return uses, defs

def liveness(blocks: Blocks, succs: AdjTable, preds: AdjTable) -> tuple[VarTable, VarTable]:
    """Return (live_in, live_out), with each table keyed by block name."""
    uses, defs = record_vars(blocks)
    return data_flow_analysis(succs, preds,
        forward=False,
        init=set,
        merge=lambda in_lives: set().union(*in_lives),
        transfer=lambda label, out_live: uses[label] | (out_live - defs[label])
    )


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
