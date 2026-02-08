#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Satzanalyse DE (Schritte 1–3)
- Schritt 1: Rechtschreibung + Groß-/Kleinschreibung (Heuristik)
- Schritt 2: Einfache Satzbauchecks (Satzanfang groß, Endzeichen, „nach Hause“, Verb-2-Heuristik)
- Schritt 3: Zusätzliche feste Wendungen (zu Hause, im Allgemeinen, im Voraus, in Ordnung, in Gefahr, in Frage)
Nutzung:
    python satz_analyse_de_v2.py "dein satz hier"
"""
import sys, re, json
from typing import List, Tuple, Union

import pandas as pd

DICT_PATH = "satz_de_woerterbuch.csv"

def tokenize(text: str) -> List[Tuple[str,int]]:
    return [(m.group(0), m.start()) for m in re.finditer(r"[A-Za-zÄÖÜäöüß\-]+", text)]

def levenshtein(a: str, b: str, max_dist: int = 2) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > max_dist:
        return max_dist + 1
    if la > lb:
        a, b = b, a
        la, lb = lb, la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0]*lb
        ai = a[i-1]
        row_min = cur[0]
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j-1] else 1
            cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + cost)
            if cur[j] < row_min:
                row_min = cur[j]
        if row_min > max_dist:
            return max_dist + 1
        prev = cur
    return prev[-1]

def build_vocab(df: pd.DataFrame):
    vocab_all = set(w.casefold() for w in df["wort"].astype(str).tolist())
    nouns = set(w.casefold() for w in df[df["kategorie"]=="Substantiv"]["wort"].astype(str).tolist())
    male_names = set(w.casefold() for w in df[df["kategorie"]=="Männername"]["wort"].astype(str).tolist())
    female_names = set(w.casefold() for w in df[df["kategorie"]=="Frauenname"]["wort"].astype(str).tolist())
    names = male_names | female_names
    cities = set(w.casefold() for w in df[df["kategorie"]=="Stadt"]["wort"].astype(str).tolist())
    verbs = set(w.casefold() for w in df[df["kategorie"]=="Verb"]["wort"].astype(str).tolist())
    adjs = set(w.casefold() for w in df[df["kategorie"]=="Adjektiv"]["wort"].astype(str).tolist())
    colors = set(w.casefold() for w in df[df["kategorie"]=="Farbe"]["wort"].astype(str).tolist())
    return {
        "all": vocab_all,
        "nouns": nouns,
        "names": names,
        "cities": cities,
        "verbs": verbs,
        "adjs": adjs,
        "colors": colors
    }

def candidates(word: str, vocab_list):
    w = word.casefold()
    L = len(w)
    pool = [v for v in vocab_list if abs(len(v) - L) <= 2 and (not w or v[:1] == w[:1])]
    scored = []
    for v in pool:
        d = levenshtein(w, v, max_dist=2)
        if d <= 2:
            scored.append((d, v))
    scored.sort()
    return [v for d,v in scored[:5]]

def analyze_sentence_step1(sentence: str, vocab_or_df: Union[dict, pd.DataFrame]):
    if isinstance(vocab_or_df, pd.DataFrame):
        vocab = build_vocab(vocab_or_df)
    else:
        vocab = vocab_or_df
    toks = tokenize(sentence)
    report = {
        "sentence": sentence,
        "tokens": [t for t,_ in toks],
        "unknown": [],
        "suggestions": {},
        "casing_warnings": [],
        "notes": [
            "Rechtschreibprüfung gegen Wörterbuch (case-insensitive).",
            "Nomen-heuristik für Groß-/Kleinschreibung (außer am Satzanfang)."
        ]
    }
    vocab_all = vocab["all"]
    nouns = vocab["nouns"]
    names = vocab["names"]
    cities = vocab["cities"]
    non_noun_categories = vocab["verbs"] | vocab["adjs"] | vocab["colors"]

    for idx, (tok, pos) in enumerate(toks):
        t_cf = tok.casefold()
        known = t_cf in vocab_all
        if not known:
            report["unknown"].append(tok)
            cands = candidates(tok, list(vocab_all))
            if cands:
                report["suggestions"][tok] = cands

        if tok[:1].islower() and t_cf in nouns and idx != 0:
            report["casing_warnings"].append({
                "token": tok,
                "issue": "Nomen vermutlich klein geschrieben",
                "suggest": tok[:1].upper() + tok[1:]
            })
        if idx != 0 and tok[:1].isupper():
            if (t_cf not in nouns) and (t_cf not in names) and (t_cf not in cities) and (t_cf in non_noun_categories):
                report["casing_warnings"].append({
                    "token": tok,
                    "issue": "Wort wirkt kein Substantiv/Eigenname",
                    "suggest": tok[:1].lower() + tok[1:]
                })
    return report

def is_probable_finite_verb(token: str) -> bool:
    t = token.casefold()
    return any(t.endswith(suf) for suf in ["e","st","t","en","te","ten","tet"])

def analyze_sentence_step2(sentence: str):
    s = sentence.strip()
    diagnostics = {
        "original": sentence,
        "normalized_suggestion": None,
        "issues": []
    }

    if s and s[0].isalpha() and s[0].islower():
        diagnostics["issues"].append({"type":"casing", "pos":0, "msg":"Satzanfang klein geschrieben.", "suggest":"Erstes Wort groß schreiben."})
    if not s.endswith((".", "!", "?")):
        diagnostics["issues"].append({"type":"punctuation", "msg":"Kein Satzzeichen am Ende.", "suggest":"Punkt/Frage-/Ausrufezeichen setzen."})

    lower = s.casefold()
    if "nach hause" in lower and "nach Hause" not in s:
        diagnostics["issues"].append({"type":"fixed_phrase", "span":"nach hause", "msg":"Feste Wendung „nach Hause“ groß schreiben.", "suggest":"Hause groß."})

    toks = [t for t,_ in tokenize(s)]
    if toks:
        if len(toks) >= 2:
            second = toks[1]
            if not is_probable_finite_verb(second):
                diagnostics["issues"].append({"type":"verb_position", "msg":"Vermutlich kein finites Verb in 2. Position (Heuristik).", "info":"In vielen deutschen Hauptsätzen steht das finite Verb an 2. Stelle."})
        if not any(is_probable_finite_verb(t) for t in toks):
            diagnostics["issues"].append({"type":"verb_existence", "msg":"Kein finites Verb erkannt (Heuristik)."})

    suggestion = s
    if suggestion:
        m = re.match(r"^([A-Za-zÄÖÜäöüß])", suggestion)
        if m and m.group(1).islower():
            suggestion = suggestion[0].upper() + suggestion[1:]
    suggestion = re.sub(r"\bnach hause\b", "nach Hause", suggestion, flags=re.IGNORECASE)
    if not suggestion.endswith((".", "!", "?")):
        suggestion = suggestion + "."
    diagnostics["normalized_suggestion"] = suggestion

    return diagnostics

# Schritt 3: zusätzliche feste Wendungen
FIXED_PHRASES = [
    (r"\bzu hause\b", "zu Hause"),
    (r"\bim allgemeinen\b", "im Allgemeinen"),
    (r"\bim voraus\b", "im Voraus"),
    (r"\bin ordnung\b", "in Ordnung"),
    (r"\bin gefahr\b", "in Gefahr"),
    (r"\bin frage\b", "in Frage"),
]

def analyze_sentence_step3_fixed(sentence: str):
    s = sentence
    issues = []
    suggestion = s
    for pat, repl in FIXED_PHRASES:
        for m in re.finditer(pat, s, flags=re.IGNORECASE):
            span_text = m.group(0)
            if span_text != repl:
                issues.append({
                    "type": "fixed_phrase",
                    "span": span_text,
                    "msg": f'Feste Wendung „{repl}“ groß/korrekt schreiben.',
                    "suggest": repl
                })
        suggestion = re.sub(pat, repl, suggestion, flags=re.IGNORECASE)
    return {
        "original": sentence,
        "issues": issues,
        "normalized_suggestion": suggestion
    }

def main():
    if len(sys.argv) < 2:
        print("Nutzung: python satz_analyse_de_v2.py \"Dein Satz hier\"")
        sys.exit(0)
    sentence = sys.argv[1]
    df = pd.read_csv(DICT_PATH)
    vocab = build_vocab(df)
    step1 = analyze_sentence_step1(sentence, vocab)
    step2 = analyze_sentence_step2(sentence)
    step3 = analyze_sentence_step3_fixed(sentence)
    print(json.dumps({"step1": step1, "step2": step2, "step3": step3}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
