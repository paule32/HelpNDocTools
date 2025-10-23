# settings.py
from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict

DEFAULT_SETTINGS = {
    "paths": {
        "c1541": "C:/Program Files/WinVICE/c1541.exe",
        "x64sc": "C:/Program Files/WinVICE/x64sc.exe"
    },
    "output": {
        "build_dir": "./build",
        "disk_name": "HELLODISK,01",
        "prg_name": "HELLO",
        "prg_file": "program.prg",
        "d64_file": "program.d64",
        "runtime_pre_file" : "runtime_pre.asm",
        "runtime_post_file": "runtime_post.asm"
    },
    "project": {
        "variant": "A",         # "A" = ein Segment (BASIC @ $0801 + Code direkt dahinter)
        "code_load": 0x0801     # nur relevant für Variante A
    }
}

def _deep_merge_defaults(dst: dict, src_defaults: dict) -> bool:
    """Trägt alle fehlenden Keys aus src_defaults in dst ein. Gibt True zurück, wenn etwas ergänzt wurde."""
    changed = False
    for k, v in src_defaults.items():
        if k not in dst:
            dst[k] = v if not isinstance(v, dict) else json.loads(json.dumps(v))
            changed = True
        else:
            if isinstance(v, dict) and isinstance(dst[k], dict):
                if _deep_merge_defaults(dst[k], v):
                    changed = True
    return changed
    
@dataclass
class Settings:
    data: dict
    path: str

    @classmethod
    def load(cls, path: str = "settings.json") -> "Settings":
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2)
            return cls(json.loads(json.dumps(DEFAULT_SETTINGS)), path)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # >>> WICHTIG: fehlende Defaults nachtragen <<<
        if _deep_merge_defaults(data, DEFAULT_SETTINGS):
            # gleich persistieren, damit es beim nächsten Start drin ist
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        return cls(data, path)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def runtime_pre_file(self) -> str:
        name = self.data.get("output", {}).get("runtime_pre_file", "runtime_pre.asm")
        return os.path.join(self.build_dir(), name)

    def runtime_post_file(self) -> str:
        name = self.data.get("output", {}).get("runtime_post_file", "runtime_post.asm")
        return os.path.join(self.build_dir(), name)

    # Convenience getters
    def c1541(self) -> str: return self.data["paths"]["c1541"]
    def x64sc(self) -> str: return self.data["paths"]["x64sc"]
    
    def build_dir(self) -> str: return self.data["output"]["build_dir"]
    def disk_name(self) -> str: return self.data["output"]["disk_name"]
    def prg_name (self) -> str: return self.data["output"]["prg_name"]
    def prg_file (self) -> str: return os.path.join(self.build_dir(), self.data["output"]["prg_file"])
    def d64_file (self) -> str: return os.path.join(self.build_dir(), self.data["output"]["d64_file"])
