import json
import sys
from typing import Any

Instruction = dict[str, Any]


def tdce(instrs: list[Instruction]) -> list[Instruction]:
    """Return one function's instructions after dead code elimination."""
    return instrs


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        function["instrs"] = tdce(function["instrs"])
    print(json.dumps(program, indent=2))
