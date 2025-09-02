from __future__ import annotations

# Magic 8-Ball using ButtonPad
# - 5x5 grid of buttons
# - Center shows a white tile with a black "8" when idle
# - Clicking any tile plays an animation:
#   * center goes black
#   * other tiles rapidly randomize among dark colors
#   * tiles fade to black one-by-one
#   * pause on all-black for 1s
#   * center turns dark blue with white answer text
# - Clicking any tile when answer is shown resets to idle

from typing import List, Tuple
import random

try:
    import buttonpad  # local module name
except Exception:
    import ButtonPad as buttonpad  # type: ignore

TITLE = "Magic 8-Ball"
COLS = 5
ROWS = 5

# UI
CELL_W = 120
CELL_H = 120
HGAP = 6
VGAP = 6
BORDER = 14
WINDOW_BG = "#0b0b0b"

# Colors
BLACK = "#000000"
WHITE = "#ffffff"
DARK_GRAY = "#2b2b31"
DARK_PURPLE = "#2a1548"
DARK_BLUE = "#0f1d3a"
RANDOM_COLORS = [BLACK, DARK_GRAY, DARK_PURPLE, DARK_BLUE]

# Animation timing
RANDOM_TICKS = 30
RANDOM_TICK_MS = 50
FADE_DELAY_MS = 20
PAUSE_BLACK_MS = 1000

# Fonts
ANSWER_FONT_SIZE = 12  # adjust the revealed answer text size here

ANSWERS = [
    "IT IS\nCERTAIN",
    "IT IS\nDECIDEDLY\nSO",
    "YES\nDEFINITELY",
    "REPLY HAZY\nTRY AGAIN",
    "ASK\nAGAIN\nLATER",
    "CONCENTRATE\nAND\nASK\nAGAIN",
    "MY REPLY\nIS NO",
    "OUTLOOK\nNOT SO\nGOOD",
    "VERY\nDOUBTFUL",
]

Coord = Tuple[int, int]
CENTER = (COLS // 2, ROWS // 2)


def build_layout() -> str:
    row = ",".join(["`"] * COLS)
    return "\n".join([row for _ in range(ROWS)])


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
        default_bg_color=BLACK,
        default_text_color=WHITE,
        window_color=WINDOW_BG,
        resizable=True,
    )

    state = {"mode": "idle", "after": []}  # modes: idle | anim | answer

    def clear_after() -> None:
        ids = state["after"]
        state["after"] = []
        for aid in ids:
            try:
                pad.root.after_cancel(aid)  # type: ignore[arg-type]
            except Exception:
                pass

    def all_cells() -> List[Coord]:
        return [(x, y) for y in range(ROWS) for x in range(COLS)]

    def set_cell(x: int, y: int, bg: str, text: str = "", fg: str = WHITE, size: int | None = None) -> None:
        el = pad[x, y]  # type: ignore[index]
        el.background_color = bg
        el.text_color = fg
        el.text = text
        if size is not None:
            el.font_size = size

    def set_idle_ui() -> None:
        # All black except center: white with black "8"
        for x, y in all_cells():
            set_cell(x, y, BLACK, "", WHITE)
        cx, cy = CENTER
        set_cell(cx, cy, WHITE, "8", BLACK, size=48)
        state["mode"] = "idle"

    def randomize_tick(remaining: int) -> None:
        if remaining <= 0:
            fade_to_black()
            return
        # center stays black during randomization
        for x, y in all_cells():
            if (x, y) == CENTER:
                continue
            set_cell(x, y, random.choice(RANDOM_COLORS), "")
        aid = pad.root.after(RANDOM_TICK_MS, lambda: randomize_tick(remaining - 1))
        state["after"].append(aid)

    def fade_to_black() -> None:
        cells = [(x, y) for x, y in all_cells()]
        random.shuffle(cells)
        # ensure center is first or already black
        if CENTER in cells:
            cells.remove(CENTER)
        cells.insert(0, CENTER)

        def step(i: int) -> None:
            if i >= len(cells):
                pause_then_answer()
                return
            x, y = cells[i]
            set_cell(x, y, BLACK, "")
            aid = pad.root.after(FADE_DELAY_MS, lambda: step(i + 1))
            state["after"].append(aid)

        step(0)

    def pause_then_answer() -> None:
        aid = pad.root.after(PAUSE_BLACK_MS, show_answer)
        state["after"].append(aid)

    def show_answer() -> None:
        # Pick and display an answer on center with dark blue bg & white text
        ans = random.choice(ANSWERS)
        cx, cy = CENTER
        for x, y in all_cells():
            set_cell(x, y, BLACK, "")
        set_cell(cx, cy, DARK_BLUE, ans, WHITE, size=ANSWER_FONT_SIZE)
        state["mode"] = "answer"

    def start_animation() -> None:
        state["mode"] = "anim"
        clear_after()
        # Center goes black
        set_cell(*CENTER, BLACK, "")
        # Begin randomization
        randomize_tick(RANDOM_TICKS)

    def on_click(_el, _x, _y) -> None:
        if state["mode"] == "anim":
            return
        if state["mode"] == "answer":
            clear_after()
            set_idle_ui()
            return
        # idle -> start animation
        start_animation()

    # Wire all buttons
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_click  # type: ignore[index]

    # Initialize
    set_idle_ui()
    pad.run()


if __name__ == "__main__":
    main()
