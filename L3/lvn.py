import json
import sys
from collections import OrderedDict
from typing import Any

Instruction = dict[str, Any]


def lvn(instrs: list[Instruction]) -> list[Instruction]:
    """Return one function's instructions after value numbering each block."""
    # FIXME: Number function parameters before their first use in the entry block.
    # FIXME: Preserve outgoing values under names that successor blocks can read.
    # FIXME: Number variables read from predecessors when starting a new block.
    # FIXME: Prevent generated temporary names from colliding with source names.
    # FIXME: Distinguish positive and negative floating-point zero in constant keys.
    OVERWRITABLE_OPS = (
        "add", "sub", "mul", "eq", "lt", "le", "gt", "ge", "not", "and", "or",
    )

    var2idx: dict[str, int] = {}
    expr2var: OrderedDict[tuple, str] = {}

    def clear_tables():
        var2idx.clear()
        expr2var.clear()

    def calculate_expr(instr: Instruction) -> tuple | None:
        op = instr["op"]
        if op == "const":
            return (op, instr["type"], instr["value"])
        elif op in OVERWRITABLE_OPS:
            return (op, tuple(var2idx[x] for x in instr["args"]))
        else:
            return None # some side-effect instr like CALL

    def rename_args(instr: Instruction) -> Instruction:
        if "args" in instr:
            vars = list(expr2var.values())
            instr["args"] = [vars[var2idx[x]] for x in instr["args"]]
        return instr

    out = []
    for i, instr in enumerate(instrs):
        if "label" in instr or instr["op"] in ("jmp", "br", "ret"):
            out.append(rename_args(instr))
            clear_tables()
        elif "dest" not in instr:
            out.append(rename_args(instr))
        else:
            expr = calculate_expr(instr)
            if expr is None:
                expr = ("opaque", i) # Avoid key confilct

            dest = instr["dest"]
            if expr in expr2var:
                idx = list(expr2var).index(expr)
            else: # new entry
                idx = len(expr2var)
                name = f"__lvn{i}_{instr["dest"]}"
                instr["dest"] = name
                out.append(rename_args(instr))
                expr2var[expr] = name

            var2idx[dest] = idx

    return out


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        function["instrs"] = lvn(function["instrs"])
    print(json.dumps(program, indent=2))
