# mini_assembler.py
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import re

from c6510_spec import C6510Spec

ALIASES = {
    "BNZ":"BNE","BZ":"BEQ",".BYT":".BYTE",".ASC":".TEXT","DB":".BYTE","DW":".WORD",
    "*":".ORG","ORG":".ORG",
    "EQU":".EQU","SET":".SET"
}

BRANCHES = {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}

@dataclass
class AsmLine:
    label: Optional[str]; mnemonic: Optional[str]; operand: Optional[str]; raw: str; lineno: int

class MiniAssembler:
    def __init__(self, spec: C6510Spec):
        self.spec = spec
        self.org = 0x1000
        self.pc = self.org
        self.symbols: Dict[str,int] = {}
        self.rows: List[Tuple[str, List[int], str, int]] = []  # (addr, bytes, text, srcline)
        self.ignore_org: bool = False

    def parse(self, text: str) -> List[AsmLine]:
        lines: List[AsmLine] = []
        for lineno, rawline in enumerate(text.splitlines(), start=1):
            line = rawline.split(";",1)[0].rstrip()
            if not line.strip(): continue
            label=None; mnemonic=None; operand=None
            if ":" in line:
                before, after = line.split(":",1)
                if before.strip(): label = before.strip()
                line = after.strip()
            if line:
                parts = line.split(None,1)
                mnemonic = parts[0].upper()
                operand = parts[1].strip() if len(parts)>1 else None
            lines.append(AsmLine(label,mnemonic,operand,rawline,lineno))
        return lines

    def _split_args(self, operand: Optional[str]) -> List[str]:
        if not operand: return []
        s = operand; out=[]; buf=[]; in_str=False; i=0
        while i<len(s):
            c=s[i]
            if c=='"':
                in_str=not in_str; buf.append(c); i+=1; continue
            if c==',' and not in_str:
                part="".join(buf).strip()
                if part: out.append(part)
                buf=[]; i+=1; continue
            buf.append(c); i+=1
        part="".join(buf).strip()
        if part: out.append(part)
        return out

    def eval_expr(self, expr: str) -> int:
        expr=expr.strip()
        m=re.fullmatch(r"'(.)'",expr)
        if m: return ord(m.group(1))
        if expr.startswith("$"): return int(expr[1:],16)
        if expr.startswith("%"): return int(expr[1:],2)
        if expr.isdigit(): return int(expr,10)
        if expr in self.symbols: return self.symbols[expr]
        m=re.fullmatch(r"(.+)\s*([+-])\s*(.+)",expr)
        if m:
            a=self.eval_expr(m.group(1)); b=self.eval_expr(m.group(3))
            return (a+b)&0xFFFF if m.group(2)== '+' else (a-b)&0xFFFF
        raise ValueError(f"Unbekannter Ausdruck/Label: {expr}")

    def _try_eval(self, expr: str):
        try: return self.eval_expr(expr)
        except Exception: return None

    def detect_mode_and_operand_bytes(self, mnem: str, operand: Optional[str], pc: int):
        if operand is None or operand.strip()=="": return "imp", []
        op = operand.strip()
        if op.upper() == "A": return "acc", []
        if op.startswith("#"): v=self.eval_expr(op[1:])&0xFF; return "imm",[v]
        if re.fullmatch(r"\(\s*[^)]+\s*,\s*X\s*\)", op, flags=re.IGNORECASE):
            inner=op[1:-1]; lhs=inner.split(",")[0]; v=self._try_eval(lhs); return "indx", [0xFF & (v or 0)]
        if re.fullmatch(r"\(\s*[^)]+\s*\)\s*,\s*Y", op, flags=re.IGNORECASE):
            inner=op.split(")")[0][1:]; v=self._try_eval(inner); return "indy", [0xFF & (v or 0)]
        if re.fullmatch(r"\(\s*[^)]+\s*\)", op):
            v=self._try_eval(op[1:-1]); vv = v or 0; return "ind", [vv&0xFF,(vv>>8)&0xFF]
        m = re.fullmatch(r"(.+)\s*,\s*([XY])", op, re.IGNORECASE)
        if m:
            val=self._try_eval(m.group(1)); idx=m.group(2).upper()
            if val is not None and val<=0xFF:
                return ("zpx",[val&0xFF]) if idx=="X" else ("zpy",[val&0xFF])
            vv=val or 0
            return ("absx",[vv&0xFF,(vv>>8)&0xFF]) if idx=="X" else ("absy",[vv&0xFF,(vv>>8)&0xFF])
        val=self._try_eval(op)
        if val is not None and val<=0xFF: return "zp",[val&0xFF]
        vv=val or 0
        return "abs",[vv&0xFF,(vv>>8)&0xFF]

    @staticmethod
    def rel_branch_offset(pc: int, target: int) -> int:
        diff = (target - (pc + 2)) & 0xFFFF
        if diff & 0x8000: diff = -((~diff + 1) & 0xFFFF)
        if diff < -128 or diff > 127: raise ValueError("Branch außerhalb Reichweite")
        return diff & 0xFF

    def assemble(self, text: str):
        listing: List[str] = []
        lines = self.parse(text)
        self.rows.clear()

        # Pass 1: Adressen/Größen
        self.pc = self.org; self.symbols.clear()
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols: raise ValueError(f"Label doppelt: {ln.label} (Z{ln.lineno})")
                self.symbols[ln.label]=self.pc
            if not ln.mnemonic: continue
            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())
            # Pass 1 (in assemble, wo mnem == ".ORG"):
            if mnem == ".ORG":
                if not self.ignore_org:
                    if not ln.operand:
                        raise ValueError(".org ohne Adresse (Z{})".format(ln.lineno))
                    op = ln.operand.strip()
                    if op.startswith("="):      # <— NEU: * = $1000 / .org = $1000
                        op = op[1:].strip()
                    self.org = self.eval_expr(op)
                    self.pc = self.org
                continue
            if mnem in (".EQU",".SET"):
                if not ln.label or not ln.operand: raise ValueError(f"{mnem} braucht Label+Wert (Z{ln.lineno})")
                self.symbols[ln.label] = self.eval_expr(ln.operand)&0xFFFF; continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'): self.pc += len(p[1:-1])
                    else: self.pc += 1
                continue
            if mnem == ".WORD":
                self.pc += 2*len(self._split_args(ln.operand)); continue
            if mnem in {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}:
                self.pc += 2; continue
            try:
                mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
                _ = self.spec.get_opcode(mnem, mode)
                self.pc += 1+len(ob)
            except Exception:
                self.pc += 3   # worst case

        # Pass 2: Bytes erzeugen
        self.pc = self.org; out = bytearray()
        for ln in lines:
            if not ln.mnemonic: continue
            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())
            # Guard: "NAME = expr" als .EQU behandeln
            if (ln.operand and ln.operand.lstrip().startswith("=")
                and re.fullmatch(r"[A-Za-z_]\w*", mnem)):
                mnem = ".EQU"
                op_equ = ln.operand.lstrip()[1:].strip()
            else:
                op_equ = ln.operand
            # Pass 2 (in assemble, wo mnem == ".ORG"):
            if mnem == ".ORG":
                if not self.ignore_org:
                    if not op_equ: raise ValueError(".org ohne Adresse (Z{})".format(ln.lineno))
                    self.org = self.eval_expr(op_equ); self.pc = self.org
                continue
            if mnem in (".EQU",".SET"):
                if not ln.label or not op_equ: raise ValueError(f"{mnem} braucht Label+Wert (Z{ln.lineno})")
                self.symbols[ln.label] = self.eval_expr(op_equ) & 0xFFFF
                continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                start_pc = self.pc; bytes_here=[]
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s=bytes(p[1:-1],"latin1","replace"); out.extend(s); bytes_here.extend(list(s)); self.pc += len(s)
                    else:
                        v=self.eval_expr(p)&0xFF; out.append(v); bytes_here.append(v); self.pc += 1
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem == ".WORD":
                start_pc = self.pc; bytes_here=[]
                for p in self._split_args(ln.operand):
                    v=self.eval_expr(p)&0xFFFF; out.extend([v & 0xFF,(v>>8)&0xFF]); bytes_here.extend([v & 0xFF,(v>>8)&0xFF]); self.pc += 2
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem in BRANCHES:
                opcode = self.spec.get_opcode(mnem,"rel")
                target = self.eval_expr(ln.operand)
                off = MiniAssembler.rel_branch_offset(self.pc, target)
                out.extend([opcode, off])
                listing.append(f"{self.pc:04X}: {opcode:02X} {off:02X}    {mnem} ${target:04X}")
                self.rows.append((f"{self.pc:04X}", [opcode, off], f"{mnem} ${target:04X}", ln.lineno))
                self.pc += 2
                continue
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            opcode = self.spec.get_opcode(mnem, mode)
            out.append(opcode); out.extend(ob)
            listing.append(f"{self.pc:04X}: " + " ".join(f"{b:02X}" for b in [opcode]+ob) + f"    {mnem} {ln.operand or ''}")
            self.rows.append((f"{self.pc:04X}", [opcode]+ob, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
            self.pc += 1+len(ob)

        return bytes(out), self.org, listing

def build_prg_with_basic_autostart(payload: bytes) -> bytes:
    LOAD_BASIC = 0x0801
    code_start = LOAD_BASIC
    while True:
        dec = str(code_start).encode("ascii")
        sysline = bytes([0x9E]) + b" " + dec + b"\x00"
        next_addr = LOAD_BASIC + 2 + 2 + len(sysline)
        new_code_start = next_addr + 2
        if new_code_start == code_start:
            break
        code_start = new_code_start
    # BASIC-Zeile + Ende
    dec = str(code_start).encode("ascii")
    sysline = bytes([0x9E]) + b" " + dec + b"\x00"
    next_addr = LOAD_BASIC + 2 + 2 + len(sysline)
    basic = bytearray([next_addr & 0xFF, next_addr >> 8, 10, 0])
    basic += sysline + b"\x00\x00"
    prg = bytearray([LOAD_BASIC & 0xFF, LOAD_BASIC >> 8])
    prg += basic + payload
    return bytes(prg)
