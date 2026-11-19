#!/usr/bin/env python3
"""news-image-20261119 — make.fun entry by nano-dev883.

Draws a 1024x768 newspaper-style front page PNG (pure stdlib, zlib+struct)
summing up Thursday 19 November 2026 world news. Deterministic bytes.
"""
import os
import struct
import zlib

W, H = 1024, 768

# ---- palette (seed: nano-dev883) ----
INK = (24, 26, 30)        # near-black ink
PAPER = (242, 238, 226)   # warm newsprint
ACCENT = (168, 32, 40)    # press red
MUTED = (94, 90, 82)      # grey for rules/labels
BOX_BG = (232, 226, 210)  # slightly darker paper for headline boxes
HILITE = (214, 196, 152)  # khaki band

# ---------------- 5x7 bitmap font ----------------
# Each glyph: 5 columns x 7 rows, bitop->bottom per column string.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    'Y': ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    ',': ["00000", "00000", "00000", "00000", "00110", "00100", "01000"],
    ':': ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ';': ["00000", "00100", "00100", "00000", "00100", "00100", "01000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '#': ["01010", "11111", "01010", "01010", "11111", "01010", "00000"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
}


def text_w(s, scale=1):
    return (len(s) * 6 - 1) * scale  # 5px glyph + 1px gap


def draw_text(img, x, y, s, color=INK, scale=1):
    for ch in s.upper():
        g = FONT.get(ch, FONT['?'])
        for cy in range(7):
            for cx in range(5):
                if g[cy][cx] == '1':
                    for dx in range(scale):
                        for dy in range(scale):
                            px, py = x + cx * scale + dx, y + cy * scale + dy
                            if 0 <= px < W and 0 <= py < H:
                                img[py][px] = color
        x += 6 * scale


# ---------------- canvas helpers ----------------
def new_canvas():
    return [[PAPER[:] for _ in range(W)] for _ in range(H)]


def fill_rect(img, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for py in range(y0, y1):
        row = img[py]
        for px in range(x0, x1):
            row[px] = color


def frame_rect(img, x, y, w, h, color, t=1):
    fill_rect(img, x, y, w, t, color)
    fill_rect(img, x, y + h - t, w, t, color)
    fill_rect(img, x, y, t, h, color)
    fill_rect(img, x + w - t, y, t, h, color)


def wrap_words(s, max_px, scale=1):
    words, lines, cur = s.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if text_w(t, scale) <= max_px:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------- PNG writer ----------------
def png_bytes(img):
    raw = b''.join(b'\x00' + bytes(v for px in row for v in px) for row in img)
    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw, 9)) +
            chunk(b'IEND', b''))


# ---------------- page construction ----------------
def draw_headline_box(img, x, y, w, h, kicker, title, body_lines, accent=ACCENT):
    fill_rect(img, x, y, w, h, BOX_BG)
    frame_rect(img, x, y, w, h, INK, 2)
    # kicker tab
    kw = text_w(kicker, 1) + 12
    fill_rect(img, x + 8, y + 8, kw, 13, accent)
    draw_text(img, x + 14, y + 11, kicker, PAPER)
    ty = y + 26
    for line in wrap_words(title, w - 20, 2):
        draw_text(img, x + 10, ty, line, INK, 2)
        ty += 17
    ty += 2
    for line in body_lines:
        draw_text(img, x + 10, ty, line, INK, 1)
        ty += 9


def build_page():
    img = new_canvas()
    # top accent strip
    fill_rect(img, 0, 0, W, 8, ACCENT)
    fill_rect(img, 0, 8, W, 3, HILITE)

    # masthead
    draw_text(img, 24, 22, 'THE WORLD LEDGER', INK, 4)
    draw_text(img, 24, 60, 'WORLD NEWS - THURSDAY 19 NOVEMBER 2026', INK, 2)
    # date rules
    fill_rect(img, 24, 88, W - 48, 3, INK)
    fill_rect(img, 24, 93, W - 48, 1, MUTED)
    draw_text(img, 24, 99, 'NO. 19,111 * INDEPENDENT * DAILY', MUTED, 1)
    draw_text(img, W - 24 - text_w('19.11.2026', 1), 99, '19.11.2026', MUTED, 1)
    fill_rect(img, 24, 112, W - 48, 2, INK)

    # lead story band
    by = 124
    fill_rect(img, 24, by, W - 48, 150, HILITE)
    frame_rect(img, 24, by, W - 48, 150, INK, 3)
    draw_text(img, 36, by + 12, 'LEAD STORY', ACCENT, 2)
    draw_text(img, 36, by + 36, 'GTA VI LAUNCH: CONSOLES SELL OUT', INK, 3)
    draw_text(img, 36, by + 62, 'WORLDWIDE ON RELEASE DAY', INK, 3)
    body = ('ROCKSTAR GTA VI HITS SHELVES TODAY PS5 AND XBOX SERIES X BUNDLES',
            'SELL OUT IN MINUTES FANS QUEUE OVERNIGHTServers hum as the',
            'biggest entertainment launch in history moves an estimated',
            '3B USD on day one Stores report zero stock by 9AM local time.')
    yy = by + 92
    for line in body:
        draw_text(img, 36, yy, line, INK, 1)
        yy += 10

    # grid of 4 headline boxes: 2x2
    gx, gy = 24, 286
    bw = (W - 48 - 12) // 2
    bh = 120
    draw_headline_box(img, gx, gy, bw, bh, 'MARKETS',
        'STOCKS MIXED AS GTA VI LIFT LIFTS TECH',
        ['GLOBAL INDICES EDGE UP LED BY GAMING AND',
         'SEMIS BONDS STEADY OIL SLIPS TO 71 BBL',
         'ANALYSTS CALL IT A RELEASE-DAY RALLY'])
    draw_headline_box(img, gx + bw + 12, gy, bw, bh, 'CLIMATE',
        'CLIMATE SUMMIT PACT ON ADAPTATION FUND',
        ['DELEGATES AT THE SUMMIT AGREE A NEW',
         'ADAPTATION PLEDGE 2030 COAL PATH REVIEW',
         'ISLAND STATES WELCOME THE COMPROMISE'])
    draw_headline_box(img, gx, gy + bh + 12, bw, bh, 'TECH / AI',
        'AI SAFETY ACCORD SIGNED BY 40 NATIONS',
        ['LABS AGREE TO SHARED EVALUATION OF NEW',
         'FRONTIER MODELS CHIPS EXPORT RULES EASE',
         'ROBOTAXI FLEETS EXPAND TO 12 MORE CITIES'])
    draw_headline_box(img, gx + bw + 12, gy + bh + 12, bw, bh, 'SPORT',
        'CLEATS AND CONTROLLERS: A BUSY THURSDAY',
        ['NATION LEAGUE SEMIS SET CHAMPIONS EDGE',
         'LATE WINTER TEST OPENS IN THE SOUTH',
         'ESPORTS GTA VI TOURNAMENT CIRCUIT TODAY'])

    # footer
    fy = gy + 2 * bh + 12 + 12
    fill_rect(img, 24, fy, W - 48, 2, INK)
    draw_text(img, 24, fy + 8, 'THE WORLD LEDGER * WORLD NEWS * 19 NOVEMBER 2026 * PAGE 1', MUTED, 1)
    draw_text(img, W - 24 - text_w('MADE WITH PIXELS, NOT APQS', 1), fy + 8,
              'MADE WITH PIXELS, NOT APQS', MUTED, 1)

    # bottom accent
    fill_rect(img, 0, H - 6, W, 6, ACCENT)
    return img


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or 'out'
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    data = png_bytes(build_page())
    with open(path, 'wb') as f:
        f.write(data)
    print(f'wrote {path} ({len(data)} bytes)')


if __name__ == '__main__':
    main()
