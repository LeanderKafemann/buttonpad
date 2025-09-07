from __future__ import annotations

from typing import Tuple
import buttonpad

COLS = 8
ROWS = 8

# UI
WINDOW_BG = "#0e1220"   # dark backdrop
BTN_BG = "#1f2640"       # default button background
BTN_FG = "#e6e6e6"       # default text color
CURSOR_BG = "#2b78ff"    # blue highlight for current position


def build_layout(cols: int, rows: int) -> str:
    # Use no-merge empty buttons so each cell is independent
    row = ",".join(["`"] * cols)
    return "\n".join([row for _ in range(rows)])


def main() -> None:
    layout = build_layout(COLS, ROWS)
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=48,
        cell_height=48,
        h_gap=4,
        v_gap=4,
        border=8,
        title="Keyboard Move Demo",
        default_bg_color=BTN_BG,
        default_text_color=BTN_FG,
        window_color=WINDOW_BG,
        resizable=True,
    )

    # current cursor position (start at 3,3)
    pos = {"x": 3, "y": 3}
    default_bg = BTN_BG

    def highlight(x: int, y: int) -> None:
        pad[x, y].background_color = CURSOR_BG  # type: ignore[index]
        pad[x, y].text = ""  # keep it clean

    def unhighlight(x: int, y: int) -> None:
        pad[x, y].background_color = default_bg  # type: ignore[index]
        pad[x, y].text = ""

    def move_to(nx: int, ny: int) -> None:
        # wrap and clamp
        nx %= COLS
        ny %= ROWS
        # if unchanged, do nothing
        if nx == pos["x"] and ny == pos["y"]:
            return
        # update visuals
        unhighlight(pos["x"], pos["y"])  # previous
        pos["x"], pos["y"] = nx, ny
        highlight(nx, ny)

    def on_cell_click(_el, x: int, y: int) -> None:
        move_to(x, y)

    # Wire all cell clicks
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_cell_click  # type: ignore[index]

    # Arrow key movement via Tk bindings on the underlying root window
    def on_left(_evt=None):
        move_to(pos["x"] - 1, pos["y"])  # wrap in move_to

    def on_right(_evt=None):
        move_to(pos["x"] + 1, pos["y"])

    def on_up(_evt=None):
        move_to(pos["x"], pos["y"] - 1)

    def on_down(_evt=None):
        move_to(pos["x"], pos["y"] + 1)

    # Bind arrows and WASD (both lowercase/uppercase) for robustness
    try:
        pad.root.bind_all("<Left>", on_left)
        pad.root.bind_all("<Right>", on_right)
        pad.root.bind_all("<Up>", on_up)
        pad.root.bind_all("<Down>", on_down)
        # WASD
        pad.root.bind_all("<KeyPress-a>", on_left)
        pad.root.bind_all("<KeyPress-A>", on_left)
        pad.root.bind_all("<KeyPress-d>", on_right)
        pad.root.bind_all("<KeyPress-D>", on_right)
        pad.root.bind_all("<KeyPress-w>", on_up)
        pad.root.bind_all("<KeyPress-W>", on_up)
        pad.root.bind_all("<KeyPress-s>", on_down)
        pad.root.bind_all("<KeyPress-S>", on_down)
    except Exception:
        pass

    # Initialize cursor
    highlight(pos["x"], pos["y"])  # starting location

    pad.run()


if __name__ == "__main__":
    main()
