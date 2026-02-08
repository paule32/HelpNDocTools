
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List, Any

import json
import os

FLAGS_ORDER = "NZCIDV"

@dataclass(frozen=True)
class ModeInfo:
    opcode: int
    size: int
    cycles: int
    flags: str
    page_cross_penalty: int = 0
    illegal: bool = False
    comment: str = ""

@dataclass(frozen=True)
class OpInfo:
    mnem: str
    mode: str
    size: int
    cycles: int
    flags: str
    page_cross_penalty: int = 0
    illegal: bool = False
    comment: str = ""

class C6510Spec:
    """
    Loader/Indexer for 6510 opcode spec.
    Use from_json() to initialize from a JSON file that matches the provided schema.
    """
    def __init__(self, mnemonics: Dict[str, Dict[str, ModeInfo]], opcode_table: List[Optional[OpInfo]]):
        self.mnemonics = mnemonics
        self.opcode_table = opcode_table

    @staticmethod
    def from_json(path: str = "6510_with_illegal_flags.json") -> "C6510Spec":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spec JSON not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        mnemonics: Dict[str, Dict[str, ModeInfo]] = {}
        for mnem, modes in spec["mnemonics"].items():
            mm: Dict[str, ModeInfo] = {}
            for mode, v in modes.items():
                mm[mode] = ModeInfo(
                    opcode=int(v["opcode"], 16),
                    size=int(v["bytes"]),
                    cycles=int(v["cycles"]),
                    flags=v.get("flags", "-" * len(FLAGS_ORDER)),
                    page_cross_penalty=int(v.get("page_cross_penalty", 0)),
                    illegal=bool(v.get("illegal", False)),
                    comment=v.get("comment", ""),
                )
            mnemonics[mnem] = mm

        opcode_table: List[Optional[OpInfo]] = [None] * 256
        for k, v in spec["opcodes"].items():
            op = int(k, 16)
            opcode_table[op] = OpInfo(
                mnem=v["mnem"],
                mode=v["mode"],
                size=int(v["bytes"]),
                cycles=int(v["cycles"]),
                flags=v.get("flags", "-" * len(FLAGS_ORDER)),
                page_cross_penalty=int(v.get("page_cross_penalty", 0)),
                illegal=bool(v.get("illegal", False)),
                comment=v.get("comment", ""),
            )
        return C6510Spec(mnemonics, opcode_table)

    # ---------- Query APIs ----------
    def get_opcode(self, mnem: str, mode: str) -> int:
        """Return opcode byte for (mnemonic, addressing mode). Raises KeyError if not present."""
        return self.mnemonics[mnem][mode].opcode

    def get_mode_info(self, mnem: str, mode: str) -> ModeInfo:
        return self.mnemonics[mnem][mode]

    def get_info_by_opcode(self, opcode: int) -> OpInfo:
        oi = self.opcode_table[opcode]
        if oi is None:
            raise KeyError(f"Opcode 0x{opcode:02X} not defined in spec")
        return oi

    # ---------- Helpers ----------
    @staticmethod
    def rel_branch_offset(pc: int, target: int) -> int:
        """
        Compute relative branch offset for 6502 (signed 8-bit), given:
        - pc: address of branch opcode byte
        - target: destination address
        Returns the encoded 8-bit offset (0..255). Raises ValueError if out of range.
        """
        off = target - (pc + 2)
        if off < -128 or off > 127:
            raise ValueError(f"Branch out of range: {off} (pc=0x{pc:04X}, target=0x{target:04X})")
        return off & 0xFF

    @staticmethod
    def crosses_page(addr: int, index: int) -> bool:
        """
        True if addr and addr+index are in different 256-byte pages.
        Useful for adding 'page_cross_penalty' cycle when addressing abs,X / abs,Y / (zp),Y etc.
        """
        return ((addr & 0xFF00) != ((addr + index) & 0xFF00))

# ---- Tiny CLI for quick inspection ----
def _demo():
    import argparse
    p = argparse.ArgumentParser(description="Quick 6510 opcode queries")
    p.add_argument("--json", default="6510_with_illegal_flags.json", help="Path to spec JSON")
    p.add_argument("--mnem", help="Mnemonic to lookup")
    p.add_argument("--mode", help="Addressing mode to lookup")
    p.add_argument("--opcode", type=lambda x: int(x, 0), help="Opcode byte (e.g. 0xA9)")
    args = p.parse_args()

    spec = C6510Spec.from_json(args.json)
    if args.mnem and args.mode:
        op = spec.get_opcode(args.mnem.upper(), args.mode)
        mi = spec.get_mode_info(args.mnem.upper(), args.mode)
        print(f"{args.mnem.upper()} {args.mode}: opcode=0x{op:02X} size={mi.size} cycles={mi.cycles} flags={mi.flags} illegal={mi.illegal}")
        if mi.comment:
            print(f"  comment: {mi.comment}")
    if args.opcode is not None:
        oi = spec.get_info_by_opcode(args.opcode)
        print(f"0x{args.opcode:02X}: {oi.mnem} {oi.mode} size={oi.size} cycles={oi.cycles} flags={oi.flags} illegal={oi.illegal}")
        if oi.comment:
            print(f"  comment: {oi.comment}")

if __name__ == "__main__":
    _demo()
