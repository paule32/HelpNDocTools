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
        "d64_file": "program.d64"
    },
    "project": {
        "variant": "A",         # "A" = ein Segment (BASIC @ $0801 + Code direkt dahinter)
        "code_load": 0x0801     # nur relevant für Variante A
    }
}

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
            return cls(DEFAULT_SETTINGS.copy(), path)
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f), path)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # Convenience getters
    def c1541(self) -> str: return self.data["paths"]["c1541"]
    def x64sc(self) -> str: return self.data["paths"]["x64sc"]
    def build_dir(self) -> str: return self.data["output"]["build_dir"]
    def disk_name(self) -> str: return self.data["output"]["disk_name"]
    def prg_name(self) -> str:  return self.data["output"]["prg_name"]
    def prg_file(self) -> str:  return os.path.join(self.build_dir(), self.data["output"]["prg_file"])
    def d64_file(self) -> str:  return os.path.join(self.build_dir(), self.data["output"]["d64_file"])
