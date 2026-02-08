# petschii.py  -- robustes Laden + Chart 00..7F mit Hex rechts
from PIL import Image, ImageDraw, ImageFont
import json, sys, os

# ---- Pfade anpassen ----
SRC_JSON = "petscii_8x8.json"        # <-- hier deine aus dem ROM erzeugte JSON
OUT_PNG  = "petscii_chart_00_7F_from_rom.png"

# ---- tolerant laden: akzeptiert {bytes:{...}} oder {...} oder {data:{...}} oder {map:{...}} ----
def load_rowbytes(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Versuche gängige Containerfelder:
    for key in ("bytes", "data", "map"):
        if isinstance(raw, dict) and key in raw and isinstance(raw[key], dict):
            return normalize_hexmap(raw[key])
    # Vielleicht ist die Map direkt auf Root
    if isinstance(raw, dict):
        return normalize_hexmap(raw)
    raise KeyError("Konnte weder 'bytes' noch 'data' noch 'map' finden und Root ist keine Code-Map.")

def normalize_hexmap(d):
    """
    Erwartet ein Dict mit Keys wie '00','0x00','$00' und Werten = Liste von 8 Hex-Strings.
    Gibt Dict mit KEYS exakt '00'..'FF' zurück.
    """
    out = {}
    for k, v in d.items():
        # Key normalisieren
        ks = str(k).strip().upper()
        if ks.startswith("0X") or ks.startswith("$"):
            ks = ks[2:] if ks.startswith("0X") else ks[1:]
        if len(ks) == 1:
            ks = "0" + ks
        if len(ks) == 3 and ks.startswith("0"):
            ks = ks[1:]  # "0A0" -> "A0"
        if len(ks) != 2:
            # evtl. 4-stellig "0000" -> letzte zwei Stellen nehmen
            if len(ks) == 4:
                ks = ks[-2:]
            else:
                continue
        # Wert prüfen
        if not isinstance(v, (list, tuple)) or len(v) < 8:
            continue
        row8 = [str(x).strip().upper() for x in v[:8]]
        # kleine Korrektur: sicherstellen, dass es echte 2-stellige Hex sind
        try:
            row8 = [f"{int(h,16):02X}" for h in row8]
        except Exception:
            continue
        out[ks] = row8
    if not out:
        raise KeyError("Keine verwertbaren 8x8-Reihen gefunden.")
    return out

def measure_text(draw, text, font):
    """Kompatibel für Pillow <10 und ≥10: liefert (w, h)."""
    if hasattr(draw, "textbbox"):
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        return (r - l, b - t)
    # Fallbacks für ältere Versionen
    if hasattr(draw, "textsize"):
        return draw.textsize(text, font=font)
    # Ultimate fallback
    if hasattr(font, "getbbox"):
        l, t, r, b = font.getbbox(text)
        return (r - l, b - t)
    return font.getsize(text)

# ---- Chart-Renderer (00..7F, mit Hex pro Zeile) ----
def render_chart(rowbytes_map, out_png):
    codes = [f"{i:02X}" for i in range(0x00, 0x80)]
    # Layout
    cols, rows = 16, 8
    px_per_bit = 12
    gap = 1
    label_h = 16
    pad = 8
    outer_pad = 20
    hex_pad = 6
    hex_col_w = 28

    glyph_w = 8*px_per_bit + 7*gap
    glyph_h = 8*px_per_bit + 7*gap
    cell_w = glyph_w + pad*2 + hex_pad + hex_col_w
    cell_h = glyph_h + label_h + pad*2

    img_w = cols * cell_w + outer_pad*2
    img_h = rows * cell_h + outer_pad*2

    from PIL import Image
    img = Image.new("RGB", (img_w, img_h), (255,255,255))
    draw = ImageDraw.Draw(img)

    try:
        font_lbl = ImageFont.truetype("DejaVuSansMono.ttf", 13)
        font_hex = ImageFont.truetype("DejaVuSansMono.ttf", 10)
    except Exception:
        font_lbl = ImageFont.load_default()
        font_hex = ImageFont.load_default()

    def draw_cell(code_hex, c, r):
        cx = outer_pad + c*cell_w
        cy = outer_pad + r*cell_h
        x0 = cx + pad
        y0 = cy + pad
        # Rahmen
        draw.rectangle([cx, cy, cx+cell_w-1, cy+cell_h-1], outline=(200,200,200), width=1)
        rb = rowbytes_map.get(code_hex, ["00"]*8)
        for y in range(8):
            try:
                b = int(rb[y], 16)
            except Exception:
                b = 0
            for x in range(8):
                bit = (b >> (7-x)) & 1  # MSB links
                sx = x0 + x*(px_per_bit + gap)
                sy = y0 + y*(px_per_bit + gap)
                rect = [sx, sy, sx+px_per_bit-1, sy+px_per_bit-1]
                draw.rectangle(rect, fill=(0,0,0) if bit else (230,230,230))
                draw.rectangle(rect, outline=(180,180,180), width=1)
            # Zeilen-Hex
            hx = f"{b:02X}"
            tx = x0 + glyph_w + hex_pad
            ty = y0 + y*(px_per_bit + gap) + (px_per_bit - 10)//2
            draw.text((tx, ty), hx, fill=(0,0,0), font=font_hex)
        # Label unter Glyph
        label = f"${code_hex}"
        tw, th = measure_text(draw, label, font_lbl)
        draw.text((cx + (cell_w - tw)//2, y0 + glyph_h + 3), label, fill=(0,0,0), font=font_lbl)

    for i, code_hex in enumerate(codes):
        draw_cell(code_hex, i % 16, i // 16)

    img.save(out_png)
    print("geschrieben:", os.path.abspath(out_png))

def main():
    try:
        rowbytes = load_rowbytes(SRC_JSON)
    except Exception as e:
        print("Eingabedatei konnte nicht interpretiert werden:", e)
        sys.exit(2)
    render_chart(rowbytes, OUT_PNG)

if __name__ == "__main__":
    main()
