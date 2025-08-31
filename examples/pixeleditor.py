from __future__ import annotations

# Pixel Editor using ButtonPad
# - 24 x 24 grid of buttons
# - Clicking a button cycles through a palette of basic colors
# - Window is resizable; h_gap and v_gap are 0

from typing import List

try:
    import buttonpad  # local module name
except Exception:
    import ButtonPad as buttonpad  # type: ignore

TITLE = "Pixel Editor"
COLS = 24
ROWS = 24

# UI
CELL_W = 22
CELL_H = 22
HGAP = 0
VGAP = 0
BORDER = 10
WINDOW_BG = "#f0f0f0"

# Basic color palette (cycle order)
PALETTE: List[str] = [
    "#ffffff",  # white
    "#000000",  # black
    "#ff0000",  # red
    "#00ff00",  # green
    "#0000ff",  # blue
    "#ffff00",  # yellow
    "#00ffff",  # cyan
    "#ff00ff",  # magenta
]


def build_layout() -> str:
    # Backtick ensures no-merge so each button is distinct
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
        default_bg_color=PALETTE[0],
        default_text_color="black",
        window_color=WINDOW_BG,
        resizable=True,
    )

    # Track palette index per cell
    board: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    def set_cell(x: int, y: int, idx: int) -> None:
        board[y][x] = idx % len(PALETTE)
        el = pad[x, y]  # type: ignore[index]
        el.background_color = PALETTE[board[y][x]]
        el.text = ""

    def cycle_color(el, x: int, y: int) -> None:
        idx = (board[y][x] + 1) % len(PALETTE)
        set_cell(x, y, idx)

    # Initialize grid and handlers
    for y in range(ROWS):
        for x in range(COLS):
            set_cell(x, y, 0)
            pad[x, y].on_click = cycle_color  # type: ignore[index]
            # Tooltip shows coordinates
            try:
                pad[x, y].tooltip = f"{x}, {y}"  # type: ignore[index]
            except Exception:
                pass

    pad.run()


if __name__ == "__main__":
    main()
