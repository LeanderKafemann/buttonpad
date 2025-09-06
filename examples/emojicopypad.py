from __future__ import annotations

# Emoji Category Pad: 8x5 grid (top row = categories, 4x8 emoji grid below).
# - Top row buttons have a slightly darker gray background and tooltips with category names.
# - Clicking a category repopulates the bottom 4x8 with that category's emoji.
# - Clicking any emoji copies it to the clipboard (pyperclip if available; Tk clipboard fallback).

from typing import Dict, List, Sequence
import sys
import tkinter.font as tkfont
import unicodedata as _ucd

try:
    import pyperclip  # type: ignore
except Exception:
    pyperclip = None  # optional; we'll fall back to Tk clipboard

try:
    import buttonpad  # local package/module name
except Exception:
    # Fallback for environments where it's installed with different casing
    import ButtonPad as buttonpad  # type: ignore

TITLE = "Emoji Category Pad"
COLS = 8
ROWS = 5  # 1 category row + 4 emoji rows (total 8x5)

# UI
CELL_W = 48
CELL_H = 48
HGAP = 4
VGAP = 4
BORDER = 10
TOP_BG = "#d6d6d6"      # slightly darker gray
BOTTOM_BG = "#f3f3f3"

# Categories: name -> (icon, emoji list)
# Clothing category removed per request; trimmed to 8 categories to match 8 columns (dropped Flags to keep common sets).
CATEGORIES: List[Dict[str, object]] = [
    {"name": "Smileys", "icon": "😊", "emojis": [
        "😀","😃","😄","😁","😆","😅","😂","🙂","🙃","😉","😊","😇","😍","🤩","😘","🥰","😗","😙","😚","😋","😛","😝","😜","🤪","🤗","🤭","🫢","🫣","🤫","🤔","🤐","🤨","😐","😑","😶","🫥","🙄","😏","😣","😥","😮\u200d💨","😮","😯","😲","🥱","😴","🤤","😪","😵","😵\u200d💫","🤒","🤕","🤧","🤮","🤢","🥴","😎","🤓","🧐","🤠","🥳","🤯","🤥","🥹"
    ]},
    {"name": "People & Body", "icon": "🧑", "emojis": [
        # 32 unique entries (exactly fills 4x8 grid) – duplicates & invalid placeholders removed/replaced
        "🧑","👶","👧","👦","👵","👴","👩","👨","👷",
        "🧑\u200d🎓","🧑\u200d🏫","🧑\u200d💻","🧑\u200d🔬","🧑\u200d🎨","🧑\u200d🚀","🧑\u200d🌾",
        "🧑\u200d🔧","🧑\u200d⚕️","🧑\u200d✈️","🧑\u200d🍳","🧑\u200d🚒","🧑\u200d🎤","🧑\u200d💼",
        "🤰","�","�","�","🧑\u200d🦽","🧑\u200d🦯","🧑\u200d🩼","🧑\u200d🦼","🧑\u200d⚖️"
    ]},
    {"name": "Hand Gestures", "icon": "✋", "emojis": [
        "👍","👎","👌","✌️","🤞","🤟","🤘","🤌","🤏","✋","🤚","🖐️","🖖","👋","🤙","💪","🙏","☝️","👆","👇","👈","👉","🖕","✍️","🤲","🫶","🫰","🫵"
    ]},
    {"name": "Animals", "icon": "🐶", "emojis": [
        "🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐻\u200d❄️","🐨","🐯","🦁","🐮","🐷","🐸","🐵","🐔","🐧","🐦","🐤","🦆","🦅","🦉","🦇","🐺","🦄","🐝","🪲","🦋","🐢","🐍","🦖","🦕","🐙","🦑","🦞","🦀","🐡","🦔","🦝"
    ]},
    {"name": "Nature", "icon": "🌿", "emojis": [
        "🌲","🌳","🌴","🌵","🌾","🌿","☘️","🍀","🍁","🍂","🍃","🌱","🌸","🌼","🌻","🌺","🌷","🌹"
    ]},
    {"name": "Weather & Sky", "icon": "☀️", "emojis": [
        "☀️","🌤️","⛅","🌥️","☁️","🌧️","⛈️","🌩️","🌨️","❄️","🌬️","🌪️","🌫️","🌈","🌙","🌕","🌖","🌗","🌘","🌑","🌒","🌓","🌔","⭐","✨","☔"
    ]},
    {"name": "Symbols", "icon": "❤️", "emojis": [
        "❤️","🧡","💛","💚","💙","💜","🖤","🤍","💟","💖","💘","💝","⭕","✅","❌","⚠️","‼️","❓","❗","➡️","⬅️","⬆️","⬇️","↔️","↕️","🔁","♻️","♾️","™️","©️","®️","☮️","⚛️","✝️","☪️","☯️","☸️","✡️"
    ]},
    {"name": "Food & Drink", "icon": "🍎", "emojis": [
        "🍎","🍊","🍋","🍌","🍉","🍇","🍓","🫐","🍒","🍑","🥭","🍍","🥝","🍅","🍆","🥑","🥦","🥬","🥒","🌶️","🧄","🧅","🥔","🍠","🍞","🥐","🥖","🥨","🥯","🧇","🥞","🧈","🧀","🍗","🥩","🥓","🍔","🍟","🍕","🌭","🥪","🌮","🌯","🫔","🥙","🥗","🍝","🍜","🍣","🍱","🍦","🍩","🍪","🎂","🍰","🧁","🍫","🍬","🍭","🍯","☕","🍺"
    ]},
]


def build_layout() -> str:
    # First row: category icons (no-merge)
    top = ",".join("`" + str(cat["icon"]) for cat in CATEGORIES)
    # Bottom 12x12: placeholder distinct buttons (use no-merge ".")
    row = ",".join(["`."] * COLS)
    body = "\n".join([row for _ in range(ROWS - 1)])
    return "\n".join([top, body])


def cycle_fill(emojis: Sequence[str], count: int) -> List[str]:
    # Repeat/truncate the list to fill count cells
    if not emojis:
        return [""] * count
    out: List[str] = []
    i = 0
    n = len(emojis)
    for _ in range(count):
        out.append(emojis[i % n])
        i += 1
    return out


def _sanitize_emojis(seq: Sequence[str]) -> List[str]:
    """Drop invalid or placeholder entries (e.g., U+FFFD replacement chars)."""
    cleaned: List[str] = []
    for s in seq:
        if not s:
            continue
        if "\ufffd" in s or "�" in s:
            continue
        cleaned.append(s)
    return cleaned


def _pick_emoji_font(root) -> str:
    """Pick a platform emoji font if available; otherwise return TkDefaultFont."""
    families = set(tkfont.families(root))
    # Common emoji fonts by OS
    candidates = []
    if sys.platform == "darwin":
        candidates = ["Apple Color Emoji", "LastResort", "Helvetica"]
    elif sys.platform.startswith("win"):
        candidates = ["Segoe UI Emoji", "Segoe UI Symbol", "Arial Unicode MS"]
    else:
        candidates = ["Noto Color Emoji", "EmojiOne Color", "DejaVu Sans"]
    for name in candidates:
        if name in families:
            return name
    return "TkDefaultFont"


def _emoji_name(s: str) -> str:
    """Best-effort human-readable name for an emoji string.
    - Try unicodedata.name on whole string
    - Else join component code point names (skip ZWJ/VS16)
    - Special-case regional indicator flags to FLAG: XY
    """
    if not s:
        return ""
    try:
        return _ucd.name(s)
    except Exception:
        pass
    # Flag composed of regional indicators
    ris = [ord(ch) for ch in s if 0x1F1E6 <= ord(ch) <= 0x1F1FF]
    if ris:
        try:
            letters = ''.join(chr(65 + (cp - 0x1F1E6)) for cp in ris)
            return f"FLAG: {letters}"
        except Exception:
            pass
    # Build from components, skipping joiners/variation selectors
    parts: List[str] = []
    for ch in s:
        cp = ord(ch)
        if cp == 0x200D or cp == 0xFE0F:  # ZWJ, VS16
            continue
        nm = _ucd.name(ch, None)
        if nm:
            parts.append(nm)
    if parts:
        return " + ".join(parts)
    return "emoji"


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=CELL_W,
        cell_height=CELL_H,
        h_gap=HGAP,
        v_gap=VGAP,
        border=BORDER,
        title=TITLE,
        default_bg_color=BOTTOM_BG,
        default_text_color="black",
        window_color="#f0f0f0",
        resizable=True,
    )

    # References
    cat_buttons: List[buttonpad.BPButton] = [pad[x, 0] for x in range(COLS)]  # type: ignore[list-item]
    # Flattened list of bottom 4×8 cells, row-major (y then x)
    grid_cells: List[buttonpad.BPButton] = [pad[x, y] for y in range(1, ROWS) for x in range(COLS)]  # type: ignore[list-item]

    # Choose an emoji-capable font for consistent rendering
    EMOJI_FONT = _pick_emoji_font(pad.root)

    # Style top row darker and add tooltips
    for x, cat in enumerate(CATEGORIES):
        btn = cat_buttons[x]
        btn.background_color = TOP_BG
        btn.font_name = EMOJI_FONT
        btn.font_size = 20
        # Tooltip with category name (if supported)
        try:
            btn.tooltip = str(cat["name"])  # type: ignore[attr-defined]
        except Exception:
            pass

    # Copy-to-clipboard handler
    def copy_emoji(el: buttonpad.BPButton, _x: int, _y: int) -> None:
        emoji = el.text
        if pyperclip is not None:
            try:
                pyperclip.copy(emoji)  # type: ignore[attr-defined]
                return
            except Exception:
                pass
        try:
            pad.root.clipboard_clear()
            pad.root.clipboard_append(emoji)
            pad.root.update()
        except Exception:
            pass

    # Populate grid with a category
    current = {"index": 0}

    def show_category(idx: int) -> None:
        current["index"] = idx
        emojis = CATEGORIES[idx]["emojis"]  # type: ignore[index]
        sanitized = _sanitize_emojis(list(emojis))  # type: ignore[list-item]
        if not sanitized:
            sanitized = ["🙂"]
        flat = cycle_fill(sanitized, (ROWS - 1) * COLS)
        for k, cell in enumerate(grid_cells):
            cell.text = flat[k]
            cell.font_name = EMOJI_FONT
            cell.font_size = 22
            cell.on_click = copy_emoji
            # Tooltip with emoji name
            try:
                cell.tooltip = _emoji_name(cell.text)  # type: ignore[attr-defined]
            except Exception:
                pass
        # Ensure UI refresh for platforms/widgets that delay redraw
        try:
            pad.root.update_idletasks()
        except Exception:
            pass

    # Wire category buttons
    for i in range(COLS):
        def make_handler(idx: int):
            def handler(_el, _x, _y):
                show_category(idx)
            return handler
        cat_buttons[i].on_click = make_handler(i)

    # Set top icons (already placed by layout; ensure text is correct and no merge side-effects)
    for x, cat in enumerate(CATEGORIES):
        cat_buttons[x].text = str(cat["icon"])  # type: ignore[index]
        cat_buttons[x].font_name = EMOJI_FONT

    # Initial category
    show_category(0)

    pad.run()


if __name__ == "__main__":
    main()
