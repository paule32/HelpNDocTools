#!/usr/bin/env python3
import sys, os, json, argparse
from PIL import Image, ImageDraw, ImageFont

def read_rom(path):
    data = open(path, "rb").read()
    if len(data) not in (4096, 8192):
        raise ValueError(f"Unexpected ROM size {len(data)}. Expected 4096 or 8192 bytes.")
    return data

def select_bank(data: bytes, bank: str) -> bytes:
    # One bank is 2KB (256 glyphs x 8 bytes)
    if len(data) == 4096:
        # two banks: 0..2047 (upper/graphics), 2048..4095 (lower/upper) in most dumps
        if bank == "upper":
            return data[0:2048]
        else:
            return data[2048:4096]
    elif len(data) == 8192:
        # 4 x 2KB; take first for 'upper', second for 'lower'
        if bank == "upper":
            return data[0:2048]
        else:
            return data[2048:4096]
    else:
        raise ValueError("Unsupported ROM size")

def glyph_rows_from_bank(bank_bytes: bytes, code: int):
    """Return 8 hex strings for PETSCII code. We use code & 0x7F (inverse uses same shape)."""
    idx = code & 0x7F  # 0..127
    off = idx * 8
    row = bank_bytes[off:off+8]
    if len(row) < 8:
        row = row + bytes(8-len(row))
    return [f"{b:02X}" for b in row]

def build_json(bank_bytes: bytes, full_00_ff: bool=True):
    out = {"meta": {
                "source": "chargen ROM",
                "cell": "8x8",
                "bit_order": "MSB left",
                "mapping": "PETSCII code -> glyph (code & 0x7F)"
            },
           "bytes": {}}
    maxc = 0xFF if full_00_ff else 0x7F
    for code in range(0x00, maxc+1):
        out["bytes"][f"{code:02X}"] = glyph_rows_from_bank(bank_bytes, code)
    return out

def measure_text(draw, text, font):
    if hasattr(draw, "textbbox"):
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        return (r - l, b - t)
    if hasattr(draw, "textsize"):
        return draw.textsize(text, font=font)
    if hasattr(font, "getbbox"):
        l, t, r, b = font.getbbox(text)
        return (r - l, b - t)
    return font.getsize(text)

def render_chart(bytes_map: dict, out_png: str, upto_ff: bool):
    codes = [f"{i:02X}" for i in range(0x00, 0x100 if upto_ff else 0x80)]
    cols = 16
    rows = (len(codes) + cols - 1) // cols

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

    W = cols * cell_w + outer_pad*2
    H = rows * cell_h + outer_pad*2

    img = Image.new("RGB", (W,H), (255,255,255))
    draw = ImageDraw.Draw(img)

    try:
        font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
        font_hex = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
    except Exception:
        font_lbl = ImageFont.load_default()
        font_hex = ImageFont.load_default()

    def draw_cell(code_hex, col, row):
        cx = outer_pad + col*cell_w
        cy = outer_pad + row*cell_h
        x0 = cx + pad
        y0 = cy + pad
        draw.rectangle([cx, cy, cx+cell_w-1, cy+cell_h-1], outline=(200,200,200), width=1)
        rb = bytes_map.get(code_hex, ["00"]*8)
        for y in range(8):
            try:
                b = int(rb[y], 16)
            except Exception:
                b = 0
            for x in range(8):
                bit = (b >> (7-x)) & 1  # MSB left
                sx = x0 + x*(px_per_bit + gap)
                sy = y0 + y*(px_per_bit + gap)
                rect = [sx, sy, sx+px_per_bit-1, sy+px_per_bit-1]
                draw.rectangle(rect, fill=(0,0,0) if bit else (230,230,230))
                draw.rectangle(rect, outline=(180,180,180), width=1)
            # row hex
            hx = f"{b:02X}"
            tx = x0 + glyph_w + hex_pad
            ty = y0 + y*(px_per_bit + gap) + (px_per_bit - 10)//2
            draw.text((tx, ty), hx, fill=(0,0,0), font=font_hex)

        label = f"${code_hex}"
        tw, th = measure_text(draw, label, font_lbl)
        draw.text((cx + (cell_w - tw)//2, y0 + glyph_h + 3), label, fill=(0,0,0), font=font_lbl)

    for i, code_hex in enumerate(codes):
        draw_cell(code_hex, i % 16, i // 16)

    img.save(out_png)

def main():
    ap = argparse.ArgumentParser(description="Extract PETSCII 8x8 from C64 char ROM and render charts.")
    ap.add_argument("rom", help="chargen ROM (4KB or 8KB)")
    ap.add_argument("--bank", choices=["upper","lower"], default="upper", help="which bank to use (2KB)")
    ap.add_argument("--out-json", default="petscii_8x8_from_rom.json", help="output JSON with 8 rows per code")
    ap.add_argument("--chart-7F", default="petscii_chart_00_7F_from_rom.png", help="chart PNG (00..7F)")
    ap.add_argument("--chart-FF", default="petscii_chart_00_FF_from_rom.png", help="chart PNG (00..FF)")
    args = ap.parse_args()

    rom = read_rom(args.rom)
    bank_bytes = select_bank(rom, args.bank)

    data = build_json(bank_bytes, full_00_ff=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # charts
    render_chart(data["bytes"], args.chart_7F, upto_ff=False)
    render_chart(data["bytes"], args.chart_FF, upto_ff=True)

if __name__ == "__main__":
    main()
