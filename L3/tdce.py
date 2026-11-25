import json
import sys
from typing import Any

Instruction = dict[str, Any]


def tdce(instrs: list[Instruction]) -> list[Instruction]:
    """Eliminate the duplicated assign"""
    REMOVABLE_OPS = ("const", "id", "add", "sub", "mul",
        "eq", "lt", "le", "gt", "ge", "not", "and", "or")
    last_defs : dict[str, int] = {} # id -> __LINE__
    dead : set[int] = {}

    for i, instr in enumerate(instrs):
        if "label" in instr:
            last_defs.clear()
            continue

        # Check the users
        for arg in instr.get("args", ()):
            last_defs.pop(arg, None)
        # Check the defs
        if "dest" in instr:
            x = instr["dest"]
            if x in last_defs:
                old = last_defs[x]
                if instrs[old]["op"] in REMOVABLE_OPS:
                    dead.add(old)
            last_defs[x] = i

        if instr["op"] in ("jmp", "br", "ret"):
            last_defs.clear() # end of scope

    return [instr for i, instr in enumerate(instrs)
            if i not in dead]


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        function["instrs"] = tdce(function["instrs"])
    print(json.dumps(program, indent=2))
