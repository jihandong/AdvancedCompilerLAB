import json
import sys
from collections import OrderedDict
from typing import Any

Instruction = dict[str, Any]
Blocks = OrderedDict[str, list[Instruction]]
AdjTable = dict[str, list[str]]

def form_blocks(instrs: list[Instruction]) -> Blocks:
    terminators = ("jmp", "br", "ret")

    blocks = OrderedDict()
    block = []
    label = ""
    def save_block():
        nonlocal label, block
        # FIXME: might be label confict
        if label: # including empty but labeled block
            blocks[label] = block
        elif block: # unlabled non-empty block
            blocks[f"__b{len(blocks)}"] = block
        block = []
        label = ""

    for instr in instrs:
        if "op" in instr:
            block.append(instr)
            if instr["op"] in terminators:
                save_block()
        else: # labels
            save_block()
            label = instr["label"]

    save_block() # tail block maybe
    return blocks

def build_cfg(blocks: Blocks) -> tuple[AdjTable, AdjTable]:
    """Return (successors, predecessors)."""
    labels = list(blocks) # keys only?
    succs = {label: [] for label in labels}
    preds = {label: [] for label in labels}

    for i, (label, block) in enumerate(blocks.items()):
        if block:
            last = block[-1]
            if last["op"] in ("jmp", "br"):
                for succ in last["labels"]:
                    succs[label].append(succ)
                    preds[succ].append(label)
                continue
            elif last["op"] == "ret":
                continue
        if i + 1 < len(labels):
            succ = labels[i + 1]
            succs[label].append(succ)
            preds[succ].append(label)

    return succs, preds

if __name__ == "__main__":
    program = json.load(sys.stdin)
    result = {}
    for function in program["functions"]:
        blocks = form_blocks(function["instrs"])
        succs, preds = build_cfg(blocks)
        result[function["name"]] = {
            "blocks": blocks, "succs": succs, "preds": preds}

    print(json.dumps(result, indent=2))
