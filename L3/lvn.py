import json
import sys
from collections import OrderedDict
from typing import Any

Instruction = dict[str, Any]


def lvn(instrs: list[Instruction], params: list[Instruction]) -> list[Instruction]:
    """Return one function's instructions after value numbering each block."""
    # TODO: Apply LVN within blocks that read values defined in predecessor blocks.
    TERMINATORS = ("jmp", "br", "ret")
    OVERWRITABLE_OPS = (
        "add", "sub", "mul", "eq", "lt", "le", "gt", "ge", "not", "and", "or",
    )

    cross_vars: set[str] = set()
    var2idx: dict[str, int] = {}
    expr2var: OrderedDict[tuple, str] = {}

    def reset_tables():
        var2idx.clear()
        expr2var.clear()
        for param in params: # params vailble in the whole func
            name = param["name"]
            var2idx[name] = len(expr2var)
            expr2var[("param", name)] = name

    def calculate_expr(instr: Instruction) -> tuple | None:
        op = instr["op"]
        if op == "const":
            value = instr["value"]
            if instr["type"] == "float" and value == 0.0:
                value = float(value).hex() # +0.0 != -0.0
            return (op, instr["type"], value)
        elif op in OVERWRITABLE_OPS:
            return (op, tuple(var2idx[x] for x in instr["args"]))
        else:
            return None # some side-effect instr like CALL

    def rename_args(instr: Instruction) -> Instruction:
        if "args" in instr:
            vars = list(expr2var.values())
            instr["args"] = [vars[var2idx[x]] for x in instr["args"]]
        return instr

    # 1. detect cross block vars, won't rename or optimize using instrs
    inblock_vars: set[str] = set()
    entry_label = instrs[0].get("label") if len(instrs) > 0 else None
    if entry_label is not None and any(
        entry_label in instr.get("labels", ()) for instr in instrs):
        pass # Corner Case: 1st instr is label, accessable by future instr
    else:
        inblock_vars = {param["name"] for param in params}

    for i, instr in enumerate(instrs):
        for name in instr.get("args", ()):
            if name not in inblock_vars:
                cross_vars.add(name)
        if ("label" in instr and i != 0) or instr["op"] in TERMINATORS:
            inblock_vars.clear()
        elif "dest" in instr:
            inblock_vars.add(instr["dest"])

    # 2. on-the-fly instr generate
    reset_tables()
    out = []
    for i, instr in enumerate(instrs):
        for name in instr.get("args", ()):
            if name not in var2idx: # must be from previous block
                var2idx[name] = len(expr2var)
                expr2var[("input", name)] = name

        if "label" in instr or instr["op"] in TERMINATORS:
            out.append(rename_args(instr))
            reset_tables()
        elif "dest" not in instr:
            out.append(rename_args(instr))
        else:
            dest = instr["dest"]
            expr = calculate_expr(instr)
            if expr is None or dest in cross_vars:
                expr = ("opaque", i) # Avoid key confilct

            if expr in expr2var:
                idx = list(expr2var).index(expr)
            else: # new entry
                idx = len(expr2var)
                name = dest if dest in cross_vars else f"__{dest}_lvn{i}"
                instr["dest"] = name
                out.append(rename_args(instr))
                expr2var[expr] = name

            var2idx[dest] = idx

    return out


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        function["instrs"] = lvn(
            function["instrs"], function.get("args", []))
    print(json.dumps(program, indent=2))
