
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Expect an external C6510Spec providing get_opcode(mnemonic, mode)
# and, ideally, a JSON spec with all (incl. illegal) opcodes.
# We keep this module focused on assembling logic.

@dataclass
class AsmLine:
    label: Optional[str]; mnemonic: Optional[str]; operand: Optional[str]; raw: str; lineno: int

ALIASES = {
    "BNZ": "BNE", "BZ": "BEQ",
    "DB": ".BYTE", "DW": ".WORD",
    ".ASC": ".TEXT", ".BYT": ".BYTE"
}

BRANCHES = {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}

class MiniAssembler:
    def __init__(self, spec):
        self.spec = spec
        self.org = 0x1000
        self.pc = self.org
        self.symbols: Dict[str,int] = {}
        # rows for UI
        self.rows: List[Tuple[str, List[int], str, int]] = []

    # ----------------- Parsing helpers -----------------
    def parse(self, text: str) -> List[AsmLine]:
        lines: List[AsmLine] = []
        for lineno, rawline in enumerate(text.splitlines(), start=1):
            # keep original for listing; strip comments only for parsing
            line_no_comment = rawline.split(";",1)[0].rstrip()
            if not line_no_comment.strip():
                continue
            label=None; mnemonic=None; operand=None
            s = line_no_comment
            if ":" in s:
                before, after = s.split(":",1)
                if before.strip():
                    label = before.strip()
                s = after.strip()
            if s:
                parts = s.split(None,1)
                mnemonic = parts[0].upper()
                operand = parts[1].strip() if len(parts)>1 else None
            lines.append(AsmLine(label,mnemonic,operand,rawline,lineno))
        return lines

    def _split_args(self, operand: Optional[str]) -> List[str]:
        if not operand: return []
        s = operand
        out=[]; buf=[]; in_str=False; i=0
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

    # ----------------- Expression eval -----------------
    def eval_expr(self, expr: str) -> int:
        expr = expr.strip()
        m=re.fullmatch(r"'(.)'",expr)
        if m: return ord(m.group(1))
        # hex ($...)
        if expr.startswith("$"): return int(expr[1:],16)
        # binary (%...)
        if expr.startswith("%"): return int(expr[1:],2)
        # decimal
        if re.fullmatch(r"[0-9]+", expr): return int(expr,10)
        # simple +/- on a single term (keeps it simple, enough for many use cases)
        m = re.fullmatch(r"(.+)\s*([+-])\s*(.+)", expr)
        if m:
            a = self.eval_expr(m.group(1))
            b = self.eval_expr(m.group(3))
            return (a + b) & 0xFFFF if m.group(2)== "+" else (a - b) & 0xFFFF
        # label
        if expr in self.symbols: return self.symbols[expr]
        raise ValueError(f"Unbekannter Ausdruck/Label: {expr}")

    # ----------------- Addressing mode detection -----------------
    def detect_mode_and_operand_bytes(self, mnem: str, operand: Optional[str], pc: int) -> Tuple[str,List[int]]:
        # implied/acc/imm/relative/indirect/zp/abs and indexed variants
        if operand is None or operand.strip() == "":
            return "imp", []

        op = operand.strip()

        # accumulator
        if op.upper() == "A":
            return "acc", []

        # immediate
        if op.startswith("#"):
            v = self.eval_expr(op[1:]) & 0xFF
            return "imm", [v]

        # (zp,X)
        if re.fullmatch(r"\(\s*[^)]+\s*,\s*X\s*\)", op, flags=re.IGNORECASE):
            inner = op[1:-1]
            lhs = inner.split(",")[0]
            v = self._try_eval_relaxed(lhs)
            if v is not None:
                return "indx", [v & 0xFF]
            # assume zp for pass 1 sizing
            return "indx", [0x00]

        # (zp),Y
        if re.fullmatch(r"\(\s*[^)]+\s*\)\s*,\s*Y", op, flags=re.IGNORECASE):
            inner = op.split(")")[0][1:]
            v = self._try_eval_relaxed(inner)
            if v is not None:
                return "indy", [v & 0xFF]
            return "indy", [0x00]

        # (abs)
        if re.fullmatch(r"\(\s*[^)]+\s*\)", op):
            inner = op[1:-1].strip()
            v = self._try_eval_relaxed(inner)
            if v is not None:
                return "ind", [v & 0xFF, (v>>8)&0xFF]
            # size for pass 1
            return "ind", [0x00,0x00]

        # abs,zp with ,X / ,Y
        m = re.fullmatch(r"(.+)\s*,\s*([XY])", op, flags=re.IGNORECASE)
        if m:
            val = self._try_eval_relaxed(m.group(1))
            idx = m.group(2).upper()
            if val is not None and val <= 0xFF:
                return ("zpx",[val & 0xFF]) if idx == "X" else ("zpy",[val & 0xFF])
            # absolute indexed
            if val is not None:
                return ("absx",[val & 0xFF,(val>>8)&0xFF]) if idx == "X" else ("absy",[val & 0xFF,(val>>8)&0xFF])
            # unknown yet → assume absolute indexed size
            return (("absx" if idx=="X" else "absy"), [0x00,0x00])

        # plain zp/abs
        val = self._try_eval_relaxed(op)
        if val is not None and val <= 0xFF:
            return "zp", [val & 0xFF]
        if val is not None:
            return "abs", [val & 0xFF, (val>>8)&0xFF]

        # forward label unknown in pass 1 → assume abs size
        return "abs", [0x00,0x00]

    def _try_eval_relaxed(self, expr: str) -> Optional[int]:
        try:
            return self.eval_expr(expr)
        except Exception:
            return None

    @staticmethod
    def rel_branch_offset(pc: int, target: int) -> int:
        diff = (target - (pc + 2)) & 0xFFFF
        if diff & 0x8000:
            diff = -((~diff + 1) & 0xFFFF)
        if diff < -128 or diff > 127:
            raise ValueError("Branch außerhalb Reichweite")
        return diff & 0xFF

    # ----------------- Assemble -----------------
    def assemble(self, text: str) -> Tuple[bytes,int,List[str]]:
        lines = self.parse(text)
        self.rows.clear()

        # Pass 1: sizes + symbol table
        self.pc = self.org
        self.symbols.clear()
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols:
                    raise ValueError(f"Label doppelt definiert: {ln.label} (Zeile {ln.lineno})")
                self.symbols[ln.label] = self.pc

            if not ln.mnemonic:
                continue

            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())

            # directives
            if mnem in (".ORG",".EQU",".SET",".BYTE",".BYT",".TEXT",".ASC",".WORD",".INCBIN"):
                size = self._pass1_directive_size(mnem, ln.operand, ln.lineno)
                self.pc += size
                continue

            # branches are always 2 bytes
            if mnem in BRANCHES:
                self.pc += 2
                continue

            # instruction: detect tentative mode → size
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            try:
                _ = self.spec.get_opcode(mnem, mode)
            except Exception:
                # try to upgrade zp to abs if opcode not available in zp (e.g. JMP)
                if mode == "zp":
                    mode = "abs"; ob = [0x00,0x00]
                    _ = self.spec.get_opcode(mnem, mode)
                else:
                    # leave size guess as 3 to keep going
                    pass
            self.pc += 1 + len(ob)

        # Pass 2: actual bytes
        self.pc = self.org
        out = bytearray()
        listing: List[str] = []
        for ln in lines:
            if not ln.mnemonic:
                continue

            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())

            # directives
            if mnem == ".ORG":
                if not ln.operand: raise ValueError(f".org ohne Adresse (Zeile {ln.lineno})")
                self.org = self.eval_expr(ln.operand); self.pc = self.org; out = bytearray()
                continue
            if mnem in (".EQU",".SET"):
                if not ln.label or not ln.operand:
                    raise ValueError(f"{mnem} benötigt Label und Wert (Zeile {ln.lineno})")
                self.symbols[ln.label] = self.eval_expr(ln.operand) & 0xFFFF
                continue
            if mnem in (".BYTE",".BYT"):
                start_pc = self.pc
                bytes_here = []
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s = bytes(p[1:-1], "latin1", "replace")
                        out.extend(s); bytes_here.extend(list(s)); self.pc += len(s)
                    else:
                        v = self.eval_expr(p) & 0xFF
                        out.append(v); bytes_here.append(v); self.pc += 1
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem in (".TEXT",".ASC"):
                start_pc = self.pc
                bytes_here = []
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s = bytes(p[1:-1], "latin1", "replace")
                        out.extend(s); bytes_here.extend(list(s)); self.pc += len(s)
                    else:
                        v = self.eval_expr(p) & 0xFF
                        out.append(v); bytes_here.append(v); self.pc += 1
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem == ".WORD":
                start_pc = self.pc
                bytes_here = []
                for p in self._split_args(ln.operand):
                    v = self.eval_expr(p) & 0xFFFF
                    out.extend([v & 0xFF, (v>>8) & 0xFF]); bytes_here.extend([v & 0xFF, (v>>8) & 0xFF]); self.pc += 2
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem == ".INCBIN":
                raise NotImplementedError(".incbin noch nicht implementiert")

            # branches
            if mnem in BRANCHES:
                opcode = self.spec.get_opcode(mnem, "rel")
                target = self.eval_expr(ln.operand)
                off = MiniAssembler.rel_branch_offset(self.pc, target)
                out.extend([opcode, off])
                listing.append(f"{self.pc:04X}: {opcode:02X} {off:02X}    {mnem} ${target:04X}")
                self.rows.append((f"{self.pc:04X}", [opcode, off], f"{mnem} ${target:04X}", ln.lineno))
                self.pc += 2
                continue

            # general instruction
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            # auto-upgrade zp->abs if needed by spec
            try:
                opcode = self.spec.get_opcode(mnem, mode)
            except Exception as e:
                if mode == "zp":
                    mode = "abs"; ob = [self.eval_expr(ln.operand) & 0xFF, (self.eval_expr(ln.operand)>>8) & 0xFF]
                    opcode = self.spec.get_opcode(mnem, mode)
                else:
                    raise ValueError(f"Opcode nicht gefunden: {mnem} / {mode} (Zeile {ln.lineno})") from e

            out.append(opcode); out.extend(ob)
            listing.append(f"{self.pc:04X}: " + " ".join(f"{b:02X}" for b in [opcode]+ob) + f"    {mnem} {ln.operand or ''}")
            self.rows.append((f"{self.pc:04X}", [opcode]+ob, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
            self.pc += 1 + len(ob)

        return bytes(out), self.org, listing

    # ----------------- Pass1 directive sizing -----------------
    def _pass1_directive_size(self, mnem: str, operand: Optional[str], lineno: int) -> int:
        if mnem == ".ORG":
            if not operand: raise ValueError(f".org ohne Adresse (Zeile {lineno})")
            # .org doesn't emit bytes; will be applied in pass2
            return 0
        if mnem in (".EQU",".SET"):
            return 0
        if mnem in (".BYTE",".BYT"):
            size = 0
            for p in self._split_args(operand):
                if p.startswith('"') and p.endswith('"'):
                    size += len(p[1:-1])
                else:
                    size += 1
            return size
        if mnem in (".TEXT",".ASC"):
            size = 0
            for p in self._split_args(operand):
                if p.startswith('"') and p.endswith('"'):
                    size += len(p[1:-1])
                else:
                    size += 1
            return size
        if mnem == ".WORD":
            n = len(self._split_args(operand))
            return 2*n
        if mnem == ".INCBIN":
            # cannot size without FS, assume 0 to avoid surprises
            return 0
        return 0
