# basic_compiler.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# --- Ziel-Register/Zero-Page-Konzept ---
# Variablen A..Z → Zero-Page $02..$1B (anpassbar)
ZP_BASE = 0x02
def zp_addr_for_var(name: str) -> int:
    name = name.strip().upper()
    if len(name) != 1 or not ('A' <= name <= 'Z'):
        raise ValueError(f"Nur Einzelbuchstaben A..Z als Variable unterstützt (got {name})")
    return ZP_BASE + (ord(name) - ord('A'))

# --- KERNAL ---
KERN_CHROUT = "$FFD2"

@dataclass
class BasicLine:
    num: int
    text: str

TOKEN_SPEC = [
    ("NUM",   r"\d+"),
    ("ID",    r"[A-Za-z][A-Za-z0-9]*"),
    ("STR",   r"\"[^\"]*\""),
    ("OP",    r"<=|>=|<>|[=+\-*/(),:]"),
    ("WS",    r"[ \t]+"),
]
TOK_RE = re.compile("|".join(f"(?P<{n}>{p})" for n,p in TOKEN_SPEC))

def tokenize(s: str):
    pos=0
    while pos < len(s):
        m = TOK_RE.match(s, pos)
        if not m: raise SyntaxError(f"Tokenfehler bei: {s[pos:pos+16]!r}")
        kind = m.lastgroup; val = m.group()
        pos = m.end()
        if kind == "WS": continue
        yield (kind, val)

def parse_lines(src: str) -> List[BasicLine]:
    lines=[]
    for raw in src.splitlines():
        raw = raw.strip()
        if not raw: continue
        m = re.match(r"^(\d+)\s+(.*)$", raw)
        if not m: raise SyntaxError(f"Zeilennummer fehlt: {raw}")
        num = int(m.group(1)); text = m.group(2).strip()
        lines.append(BasicLine(num, text))
    return lines

# --- Ausdruck sehr simpel: nur Ganzzahlen + einstellige Variablen + () + + - * / ---
class Expr:
    pass
@dataclass
class Num(Expr): v:int
@dataclass
class Var(Expr): name:str
@dataclass
class Bin(Expr): op:str; a:Expr; b:Expr
@dataclass
class Par(Expr): x:Expr

class ExprParser:
    def __init__(self, tokens): self.toks=list(tokens); self.i=0
    def peek(self): return self.toks[self.i] if self.i<len(self.toks) else (None,None)
    def eat(self,k=None,v=None):
        t=self.peek()
        if t[0] is None: raise SyntaxError("Unerwartetes Ende")
        if (k and t[0]!=k) or (v and t[1]!=v): raise SyntaxError(f"Erwartet {k or v}, fand {t}")
        self.i+=1; return t
    def parse_expr(self): return self.parse_add()
    def parse_add(self):
        x=self.parse_mul()
        while True:
            k,v=self.peek()
            if v in ("+","-"):
                self.eat("OP",v); y=self.parse_mul(); x=Bin(v,x,y)
            else: break
        return x
    def parse_mul(self):
        x=self.parse_atom()
        while True:
            k,v=self.peek()
            if v in ("*","/"):
                self.eat("OP",v); y=self.parse_atom(); x=Bin(v,x,y)
            else: break
        return x
    def parse_atom(self):
        k,v=self.peek()
        if k=="NUM": self.eat("NUM"); return Num(int(v))
        if k=="ID" and len(v)==1: self.eat("ID"); return Var(v.upper())
        if v=="(": self.eat("OP","("); x=self.parse_expr(); self.eat("OP",")"); return Par(x)
        raise SyntaxError(f"Unerwartetes Token in Ausdruck: {k,v}")

# --- Lowering: Ausdrücke → Akkumulator (8-Bit), sehr simpel (kein Overflow-Handling) ---
def lower_expr_to_asm(e: Expr) -> List[str]:
    if isinstance(e, Num):
        return [f"    LDA #{e.v & 0xFF:02X}h"]
    if isinstance(e, Var):
        zp = zp_addr_for_var(e.name)
        return [f"    LDA ${zp:02X}"]
    if isinstance(e, Par):
        return lower_expr_to_asm(e.x)
    if isinstance(e, Bin):
        code = []
        code += lower_expr_to_asm(e.a)         # A := a
        code += ["    STA TMP"]                # TMP := A  (TMP definieren wir in Runtime)
        code += lower_expr_to_asm(e.b)         # A := b
        if e.op == "+": code += ["    CLC", "    ADC TMP"]
        elif e.op == "-": code += ["    SEC", "    SBC TMP"]
        elif e.op == "*":
            # naive 8-Bit-Mul: A=b, TMP=a → result in A (nur low byte)
            code += [
                "    STA MUL_B",
                "    LDA #00h",
                "    LDX MUL_B",
                "mul_lp:",
                "    BEQ mul_done",
                "    CLC",
                "    ADC TMP",
                "    DEX",
                "    BNE mul_lp",
                "mul_done:"
            ]
        elif e.op == "/":
            code += [
                "    TAX",              # X = b
                "    LDA TMP",          # A = a
                "    LSR A",            # (sehr grob: A/=2 solange X>1) – Platzhalter
                "    ; TODO: echte Division"
            ]
        else:
            code += ["    ; TODO: Operator " + e.op]
        return code
    raise TypeError(e)

# --- Statement-Lowering ---
def lower_print(args: List[str]) -> List[str]:
    out=[]
    for a in args:
        a=a.strip()
        if a.upper().startswith('CHR$(') and a.endswith(')'):
            inner = a[5:-1]
            v = int(inner) if inner.isdigit() else 13
            out += [f"    LDA #{v & 0xFF:02X}h", f"    JSR {KERN_CHROUT}"]
        elif a.startswith('"') and a.endswith('"'):
            label = f"STR_{abs(hash(a)) & 0xFFFF:04X}"
            out += [f"    LDY #00h",
                    f"{label}:",
                    f"    LDA {label}_DATA,Y",
                    f"    BEQ {label}_END",
                    f"    JSR {KERN_CHROUT}",
                    f"    INY",
                    f"    BNE {label}",
                    f"{label}_END:"]
            out += [f"{label}_DATA:",
                    f"    .BYTE " + ",".join(f"{ord(c)}" for c in a.strip('"')) + ",0"]
        elif a == "":  # leeres Feld (z. B. aufeinanderfolgende Kommas)
            pass
        else:
            # Zahl/Var → Ausdruck nach A, dann rudimentär als Ziffern ausgeben (TODO)
            out += ["    ; PRINT expr (TODO: Zahl/Var schön ausgeben)"]
            out += lower_expr_to_asm(parse_expr(a))
            out += [f"    JSR {KERN_CHROUT}"]
    return out

def parse_expr(s: str) -> Expr:
    return ExprParser(tokenize(s)).parse_expr()

def compile_basic_to_asm(source: str) -> Tuple[str, Dict[int,str]]:
    """
    Rückgabe:
      asm_text: str
      label_map: Mapping BASIC-Liniennummer -> ASM-Label
    """
    lines = parse_lines(source)
    # Label pro BASIC-Zeile
    label_for: Dict[int,str] = {ln.num: f"L{ln.num}" for ln in lines}

    asm: List[str] = []
    asm += [
        "; --- BASIC→ASM ---",
        ".ORG $1000",
        "TMP = $FB",
        "MUL_B = $FC",
        "",
        "start:"
    ]

    for ln in lines:
        text = ln.text.strip()
        # REM
        if text.upper().startswith("REM"):
            asm += [f"{label_for[ln.num]}: ; {text[3:].strip()}"]
            continue

        # IF <expr> THEN <line>
        m = re.match(r"(?i)^IF\s+(.+?)\s+THEN\s+(\d+)$", text)
        if m:
            cond = m.group(1).strip(); dest = int(m.group(2))
            asm += [f"{label_for[ln.num]}:"]
            asm += lower_expr_to_asm(parse_expr(cond))
            asm += ["    CMP #00h", f"    BEQ {label_for.get(dest, f'L{dest}')}",]
            continue

        # GOTO n
        m = re.match(r"(?i)^GOTO\s+(\d+)$", text)
        if m:
            dest=int(m.group(1))
            asm += [f"{label_for[ln.num]}:", f"    JMP {label_for.get(dest, f'L{dest}')}",]
            continue

        # GOSUB n / RETURN
        m = re.match(r"(?i)^GOSUB\s+(\d+)$", text)
        if m:
            dest=int(m.group(1))
            asm += [f"{label_for[ln.num]}:", f"    JSR {label_for.get(dest, f'L{dest}')}",]
            continue
        if re.match(r"(?i)^RETURN$", text):
            asm += [f"{label_for[ln.num]}:", "    RTS"]; continue

        # SYS addr
        m = re.match(r"(?i)^SYS\s+(.+)$", text)
        if m:
            addr = m.group(1).strip()
            asm += [f"{label_for[ln.num]}:", f"    JSR ${int(addr):04X}" if addr.isdigit() else f"    JSR {addr}"]
            continue

        # POKE a, v
        m = re.match(r"(?i)^POKE\s+(.+?)\s*,\s*(.+)$", text)
        if m:
            a = parse_expr(m.group(1)); v = parse_expr(m.group(2))
            asm += [f"{label_for[ln.num]}:"]
            asm += lower_expr_to_asm(v)    # A = value
            # Adresse (nur absolut 16-Bit für jetzt)
            asm += ["    ; POKE addr, A"]
            # naive: wenn Konstante → direkt
            if isinstance(a, Num):
                asm += [f"    STA ${a.v & 0xFFFF:04X}"]
            else:
                asm += ["    ; TODO: POKE (expr-Addr)"]
            continue

        # LET X = expr   /   X = expr
        m = re.match(r"(?i)^(?:LET\s+)?([A-Za-z])\s*=\s*(.+)$", text)
        if m:
            var = m.group(1).upper(); expr = parse_expr(m.group(2))
            zp = zp_addr_for_var(var)
            asm += [f"{label_for[ln.num]}:"]
            asm += lower_expr_to_asm(expr)
            asm += [f"    STA ${zp:02X}"]
            continue

        # PRINT a[,b,...]
        m = re.match(r"(?i)^PRINT\s*(.*)$", text)
        if m:
            tail = m.group(1).strip()
            # Split an Kommas außerhalb von Strings
            parts=[]; buf=[]; ins=False
            for ch in tail:
                if ch=='"': ins=not ins; buf.append(ch); continue
                if ch==',' and not ins: parts.append("".join(buf).strip()); buf=[]; continue
                buf.append(ch)
            if buf: parts.append("".join(buf).strip())
            asm += [f"{label_for[ln.num]}:"]
            asm += lower_print(parts)
            continue

        # FOR i = from TO to [STEP s]
        m = re.match(r"(?i)^FOR\s+([A-Za-z])\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$", text)
        if m:
            v=m.group(1).upper(); vaddr=zp_addr_for_var(v)
            lo=parse_expr(m.group(2)); hi=parse_expr(m.group(3))
            step=parse_expr(m.group(4)) if m.group(4) else Num(1)
            loop_lbl=f"FOR_{ln.num}"
            end_lbl=f"NEXT_{ln.num}"
            asm += [f"{label_for[ln.num]}:"]
            asm += lower_expr_to_asm(lo); asm += [f"    STA ${vaddr:02X}"]
            # test
            asm += [f"{loop_lbl}:"]
            asm += lower_expr_to_asm(Var(v)); asm += ["    CMP #00h ; TODO: richtige Grenze"]
            asm += [f"    BEQ {end_lbl}"]
            # body: läuft einfach weiter (bis NEXT)
            continue

        if re.match(r"(?i)^NEXT(\s+[A-Za-z])?$", text):
            # sehr grob: v++ ; springe zu loop_lbl
            # In wirklichkeit bräuchten wir Stack/Loop-Kette – für den Start ok
            asm += [f"{label_for[ln.num]}:", "    ; TODO: FOR/NEXT Verknüpfung herstellen", "    RTS"]
            continue

        # Fallback
        asm += [f"{label_for[ln.num]}:", f"    ; TODO: Nicht unterstützt: {text}"]

    asm += ["", "    RTS"]
    return "\n".join(asm), label_for
