import json
import sys

from lvn import lvn
from tdce import tdce


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        instrs = lvn(function["instrs"], function.get("args", []))
        function["instrs"] = tdce(instrs)
    json.dump(program, sys.stdout)
