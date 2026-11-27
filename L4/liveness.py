import json
import sys

from L2.build_cfg import AdjTable, Blocks, build_cfg, form_blocks

LiveSets = dict[str, set[str]]


def liveness(blocks: Blocks, succs: AdjTable) -> tuple[LiveSets, LiveSets]:
    """Return (live_in, live_out), with each table keyed by block name."""
    raise NotImplementedError("live variable analysis")


if __name__ == "__main__":
    program = json.load(sys.stdin)
    result = {}
    for function in program["functions"]:
        blocks = form_blocks(function["instrs"])
        succs, _ = build_cfg(blocks)
        live_in, live_out = liveness(blocks, succs)
        result[function["name"]] = {
            name: {"in": sorted(live_in[name]), "out": sorted(live_out[name])}
            for name in blocks
        }
    print(json.dumps(result, indent=2))
