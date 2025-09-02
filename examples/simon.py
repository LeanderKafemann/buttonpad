from __future__ import annotations

"""
Simon: 2x2 button grid Simon game using ButtonPad.
- The game shows a growing sequence by lighting buttons.
- Player repeats the pattern by clicking buttons.
- On mistake, show an alert with the achieved sequence length, then start a new game.
- No sound; feedback is via button highlight.
"""

import random
from typing import List

try:
    import buttonpad
except Exception:
    import ButtonPad as buttonpad  # type: ignore

TITLE = "Simon"
COLS = 2
ROWS = 2

# UI
CELL_W = 120
CELL_H = 120
HGAP = 8
VGAP = 8
BORDER = 10
WINDOW_BG = "#0e1220"  # dark backdrop
TEXT_COLOR = "#ffffff"

# Base and lit colors per quadrant (index: y*2 + x)
BASE_COLORS = [
    "#2ecc71",  # green
    "#e74c3c",  # red
    "#3498db",  # blue
    "#f1c40f",  # yellow
]
LIT_COLORS = [
    "#6ff7a8",  # light green
    "#ff8a73",  # light red
    "#7cbcff",  # light blue
    "#ffe27a",  # light yellow
]

FLASH_MS = 450
GAP_MS = 160
BETWEEN_ROUNDS_MS = 500
CLICK_FLASH_MS = 180


def build_layout() -> str:
    # Two rows of two independent buttons
    row = ",".join(["`"] * COLS)
    return "\n".join([row for _ in range(ROWS)])


essential_indices = [0, 1, 2, 3]


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
        default_bg_color=BASE_COLORS[0],  # we'll set per-cell below
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )

    # Apply per-cell base colors and clear text
    for y in range(ROWS):
        for x in range(COLS):
            idx = y * COLS + x
            el = pad[x, y]  # type: ignore[index]
            el.background_color = BASE_COLORS[idx]
            el.text = ""

    sequence: List[int] = []
    state = {"busy": False, "expect": 0, "accept": False}

    def set_lit(idx: int, lit: bool) -> None:
        x, y = idx % COLS, idx // COLS
        pad[x, y].background_color = (LIT_COLORS[idx] if lit else BASE_COLORS[idx])  # type: ignore[index]

    def flash_idx(idx: int, on_ms: int, after_cb) -> None:
        set_lit(idx, True)
        pad.root.after(on_ms, lambda: (set_lit(idx, False), after_cb()))

    def playback_sequence() -> None:
        state["busy"] = True
        state["accept"] = False
        state["expect"] = 0
        i = 0

        def next_step():
            nonlocal i
            if i >= len(sequence):
                state["busy"] = False
                state["accept"] = True
                return
            idx = sequence[i]
            def cont():
                pad.root.after(GAP_MS, advance)
            flash_idx(idx, FLASH_MS, cont)

        def advance():
            nonlocal i
            i += 1
            next_step()

        next_step()

    def add_step_and_play() -> None:
        # Append a new random index and play back
        sequence.append(random.choice(essential_indices))
        pad.root.after(BETWEEN_ROUNDS_MS, playback_sequence)

    def game_over() -> None:
        # Report the last fully completed sequence length
        length_achieved = max(0, len(sequence) - 1)
        try:
            buttonpad.alert(f"Game Over\nYou reached a sequence length of {length_achieved}")
        except Exception:
            pass
        new_game()

    def on_cell_click(_el, x: int, y: int) -> None:
        if state["busy"] or not state["accept"]:
            return
        idx = y * COLS + x
        # brief click flash
        set_lit(idx, True)
        pad.root.after(CLICK_FLASH_MS, lambda: set_lit(idx, False))

        expected = sequence[state["expect"]]
        if idx == expected:
            state["expect"] += 1
            # completed the whole sequence correctly -> extend
            if state["expect"] == len(sequence):
                state["accept"] = False
                add_step_and_play()
        else:
            game_over()

    # Wire clicks
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_cell_click  # type: ignore[index]

    def new_game() -> None:
        sequence.clear()
        state["busy"] = False
        state["accept"] = False
        state["expect"] = 0
        add_step_and_play()

    # Start
    new_game()

    pad.run()


if __name__ == "__main__":
    main()
