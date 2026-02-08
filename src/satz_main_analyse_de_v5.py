"""
Satzanalyse DE (v5) – erweiterte Morphologie
- Schritt 1: Rechtschreibung + Groß-/Kleinschreibung (Heuristik)
- Schritt 2: Einfache Satzbauchecks (Satzanfang groß, Endzeichen, „nach Hause“, Verb-2-Heuristik)
- Schritt 3: Feste Wendungen (konfigurierbar)
- Schritt 4: Satzbau-Heuristiken (Konjunktionsdopplungen, Kommahinweis, doppelte Negation)
- Schritt 5: Flexions-Erkennung (Verbformen inkl. Partizip II & trennbare Verben; Nomen-Plurale inkl. Umlaut-Heuristik & Sonderfälle)
Optional: JSON-Konfigurationsdatei "satz_analyse_config.json" im selben Ordner.
"""
import sys, re, json, os
from typing import List, Tuple, Union, Dict
import pandas as pd

DICT_PATH = "satz_de_woerterbuch.csv"
CONFIG_PATH = "satz_analyse_config.json"

DEFAULT_CONFIG = {
    "fixed_phrases": [
        [r"\bzu hause\b", "zu Hause"],
        [r"\bim allgemeinen\b", "im Allgemeinen"],
        [r"\bim voraus\b", "im Voraus"],
        [r"\bin ordnung\b", "in Ordnung"],
        [r"\bin gefahr\b", "in Gefahr"],
        [r"\bin frage\b", "in Frage"]
    ],
    "conjunctions": ["und","oder","aber","denn","doch","sondern","weil","dass","sowie","bzw","beziehungsweise","sowohl","als","auch","weder","noch"],
    "negation_1": ["nicht","nie","niemals","nichts","niemand","nirgends","nirgendwo"],
    "negation_2": ["kein","keine","keinen","keinem","keiner","keines","nichts","niemand","nirgends","nirgendwo"],
    "verb_endings": ["e","st","t","en","te","ten","tet"],
    "noun_plural_endings": ["e","en","er","n","s"],
    "separable_prefixes": ["ab","an","auf","aus","bei","dar","ein","fest","fort","her","hin","los","mit","nach","vor","weg","zu","zurück","zusammen"]
}

def load_config(path: str) -> Dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            for k,v in data.items():
                cfg[k] = v
            return cfg
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

CFG = load_config(CONFIG_PATH)

# ---------- utils ----------
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
    return {"all": vocab_all,"nouns": nouns,"names": names,"cities": cities,"verbs": verbs,"adjs": adjs,"colors": colors}

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

# ---------- step1 ----------
def analyze_sentence_step1(sentence: str, vocab_or_df: Union[dict, pd.DataFrame]):
    if isinstance(vocab_or_df, pd.DataFrame):
        vocab = build_vocab(vocab_or_df)
    else:
        vocab = vocab_or_df
    toks = tokenize(sentence)
    report = {"sentence": sentence,"tokens": [t for t,_ in toks],"unknown": [],"suggestions": {},"casing_warnings": [],
              "notes": ["Rechtschreibprüfung gegen Wörterbuch (case-insensitive).","Nomen-Heuristik für Groß-/Klein (außer am Satzanfang)."]}
    vocab_all = vocab["all"]; nouns = vocab["nouns"]; names = vocab["names"]; cities = vocab["cities"]
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
            report["casing_warnings"].append({"token": tok,"issue": "Nomen vermutlich klein geschrieben","suggest": tok[:1].upper() + tok[1:]})
        if idx != 0 and tok[:1].isupper():
            if (t_cf not in nouns) and (t_cf not in names) and (t_cf not in cities) and (t_cf in non_noun_categories):
                report["casing_warnings"].append({"token": tok,"issue": "Wort wirkt kein Substantiv/Eigenname","suggest": tok[:1].lower() + tok[1:]})
    return report

# ---------- step2 ----------
def is_probable_finite_verb(token: str) -> bool:
    t = token.casefold()
    return any(t.endswith(suf) for suf in CFG["verb_endings"])

def analyze_sentence_step2(sentence: str):
    s = sentence.strip()
    diagnostics = {"original": sentence,"normalized_suggestion": None,"issues": []}
    if s and s[0].isalpha() and s[0].islower():
        diagnostics["issues"].append({"type":"casing","pos":0,"msg":"Satzanfang klein geschrieben.","suggest":"Erstes Wort groß schreiben."})
    if not s.endswith((".", "!", "?")):
        diagnostics["issues"].append({"type":"punctuation","msg":"Kein Satzzeichen am Ende.","suggest":"Punkt/Frage-/Ausrufezeichen setzen."})
    lower = s.casefold()
    if "nach hause" in lower and "nach Hause" not in s:
        diagnostics["issues"].append({"type":"fixed_phrase","span":"nach hause","msg":"Feste Wendung „nach Hause“ groß schreiben.","suggest":"Hause groß."})
    toks = [t for t,_ in tokenize(s)]
    if toks:
        if len(toks) >= 2:
            second = toks[1]
            if not is_probable_finite_verb(second):
                diagnostics["issues"].append({"type":"verb_position","msg":"Vermutlich kein finites Verb in 2. Position (Heuristik).","info":"In vielen deutschen Hauptsätzen steht das finite Verb an 2. Stelle."})
        if not any(is_probable_finite_verb(t) for t in toks):
            diagnostics["issues"].append({"type":"verb_existence","msg":"Kein finites Verb erkannt (Heuristik)."})
    suggestion = s
    if suggestion:
        m = re.match(r"^([A-Za-zÄÖÜäöüß])", suggestion)
        if m and m.group(1).islower():
            suggestion = suggestion[0].upper() + suggestion[1:]
    suggestion = re.sub(r"\\bnach hause\\b", "nach Hause", suggestion, flags=re.IGNORECASE)
    if not suggestion.endswith((".", "!", "?")):
        suggestion = suggestion + "."
    diagnostics["normalized_suggestion"] = suggestion
    return diagnostics

# ---------- step3 ----------
def analyze_sentence_step3_fixed(sentence: str):
    s = sentence
    issues = []
    suggestion = s
    for pat, repl in CFG["fixed_phrases"]:
        for m in re.finditer(pat, s, flags=re.IGNORECASE):
            span_text = m.group(0)
            if span_text != repl:
                issues.append({"type": "fixed_phrase","span": span_text,"msg": f'Feste Wendung „{repl}“ groß/korrekt schreiben.',"suggest": repl})
        suggestion = re.sub(pat, repl, suggestion, flags=re.IGNORECASE)
    return {"original": sentence,"issues": issues,"normalized_suggestion": suggestion}

# ---------- step4 ----------
def analyze_sentence_step4_syntax(sentence: str):
    s = sentence
    toks = [t.casefold() for t,_ in tokenize(s)]
    issues = []
    conj_set = set(CFG["conjunctions"])
    for i in range(len(toks)-1):
        if toks[i] in conj_set:
            if toks[i+1] == toks[i]:
                issues.append({"type":"conjunction_repeat","tokens":[toks[i], toks[i+1]],"msg": f'Doppelte Konjunktion „{toks[i]} {toks[i+1]}“. Kürzen.'})
            if i+2 < len(toks) and toks[i+2] == toks[i]:
                issues.append({"type":"conjunction_repeat_spaced","tokens":[toks[i], toks[i+2]],"msg": f'Mögliche Dopplung der Konjunktion „{toks[i]} … {toks[i]}“. Prüfen.'})
    count_und = toks.count("und"); count_oder = toks.count("oder")
    if count_und >= 2 or count_oder >= 2:
        issues.append({"type":"comma_hint","msg":"Mehrfaches „und/oder“ – Kommasetzung prüfen (Aufzählung/Teilsätze?)."})
    neg1 = set(CFG["negation_1"]); neg2 = set(CFG["negation_2"])
    for i, t in enumerate(toks):
        if t in neg1:
            for j in range(i+1, min(i+7, len(toks))):
                if toks[j] in neg2:
                    issues.append({"type":"double_negation","span":" ".join(toks[i:j+1]),"msg":"Mögliche doppelte Negation."})
                    break
    return {"original": sentence, "issues": issues}

# ---------- step5 (morphology) ----------
DEUMLAUT = str.maketrans({"ä":"a","ö":"o","ü":"u","Ä":"A","Ö":"O","Ü":"U"})

def deumlaut_once(s: str) -> str:
    return s.translate(DEUMLAUT)

def try_recognize_separable_participle(token_cf: str, vocab: Dict[str,set]):
    # pattern: <prefix> + ge + <stem> + (t|en)  -> infinitive: <prefix><stem>en
    for pref in sorted(CFG["separable_prefixes"], key=len, reverse=True):
        if token_cf.startswith(pref + "ge") and len(token_cf) > len(pref) + 3:
            core = token_cf[len(pref)+2:]  # after 'ge'
            if core.endswith("t"):
                base = pref + core[:-1] + "en"
            elif core.endswith("en"):
                base = pref + core
            else:
                continue
            if base in vocab["verbs"] or base in vocab["all"]:
                return base
    return None

def try_recognize_verb_form(token_cf: str, vocab: Dict[str, set]):
    # regular endings
    for suf in CFG["verb_endings"]:
        if token_cf.endswith(suf) and len(token_cf) > len(suf):
            base = token_cf[:-len(suf)] + "en"
            if base in vocab["verbs"] or base in vocab["all"]:
                return base
    # participle II (ge...t / ge...en)
    if token_cf.startswith("ge") and len(token_cf) > 4:
        if token_cf.endswith("t"):
            base = token_cf[2:-1] + "en"
            if base in vocab["verbs"] or base in vocab["all"]:
                return base
        if token_cf.endswith("en"):
            base = token_cf[2:]
            if base in vocab["verbs"] or base in vocab["all"]:
                return base
    # separable prefixes: aufge-... -> auf...en
    sep = try_recognize_separable_participle(token_cf, vocab)
    if sep:
        return sep
    return None

def try_recognize_noun_plural(token: str, vocab: Dict[str, set]):
    if not token or not token[0].isalpha():
        return None
    t_cf = token.casefold()
    # special irregulars
    if t_cf.endswith("männer"):
        return "mann"
    if t_cf.endswith("frauen"):
        return "frau"
    if t_cf.endswith("kinder"):
        return "kind"
    if t_cf.endswith("tümer"):
        return t_cf[:-4] + "tum"   # e.g., "Besitztümer" -> "Besitztum" (selten, aber heuristisch)
    # -ien -> -ium
    if t_cf.endswith("ien"):
        base = t_cf[:-3] + "ium"
        if base in vocab["nouns"] or base in vocab["all"]:
            return base
    # generic suffixes with de-umlaut attempt on preceding vowel
    for suf in CFG["noun_plural_endings"]:
        if t_cf.endswith(suf) and len(t_cf) > len(suf):
            base = t_cf[:-len(suf)]
            # try plain base
            if base in vocab["nouns"] or base in vocab["all"]:
                return base
            # try de-umlauted last vowel in base
            alt = deumlaut_once(base)
            if alt in vocab["nouns"] or alt in vocab["all"]:
                return alt
    return None

def analyze_sentence_step5_flex(sentence: str, vocab_or_df: Union[dict, pd.DataFrame]):
    if isinstance(vocab_or_df, pd.DataFrame):
        vocab = build_vocab(vocab_or_df)
    else:
        vocab = vocab_or_df
    toks = [t for t,_ in tokenize(sentence)]
    recognized = []
    for tok in toks:
        t_cf = tok.casefold()
        if t_cf not in vocab["all"]:
            vbase = try_recognize_verb_form(t_cf, vocab)
            if vbase:
                recognized.append({"token": tok, "class":"Verbform", "base": vbase})
                continue
            nbase = try_recognize_noun_plural(tok, vocab)
            if nbase:
                recognized.append({"token": tok, "class":"Nomen (Plural)", "base": nbase})
                continue
    return {"original": sentence, "recognized": recognized, "note": "Heuristik mit Umlaut-Umkehr, Sonderfällen und trennbaren Verben."}

def main():
    if len(sys.argv) < 2:
        print("Nutzung: python satz_analyse_de_v5.py \"Dein Satz hier\"")
        sys.exit(0)
    sentence = sys.argv[1]
    df = pd.read_csv(DICT_PATH)
    vocab = build_vocab(df)
    out = {
        "step1": analyze_sentence_step1(sentence, vocab),
        "step2": analyze_sentence_step2(sentence),
        "step3": analyze_sentence_step3_fixed(sentence),
        "step4": analyze_sentence_step4_syntax(sentence),
        "step5": analyze_sentence_step5_flex(sentence, vocab),
        "config_used": CFG
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
