from __future__ import annotations

"""
Memory Puzzle using ButtonPad
- 6 x 4 grid of buttons (24 cards = 12 pairs of emojis)
- Click to reveal; match pairs to keep them permanently revealed with a distinct background
- Track number of tries (each pair attempt counts as 1)
- On win: alert with tries, then start a new game
"""

import random
from typing import List, Tuple

import buttonpad

COLS = 6
ROWS = 4

# UI
WINDOW_BG = "#0e1220"      # dark backdrop
HIDDEN_BG = "#1f2640"      # hidden card background
REVEAL_BG = "#2a3358"      # temporarily revealed background
MATCHED_BG = "#2e7d32"     # permanently matched background (greenish)
TEXT_COLOR = "#ffffff"
FONT_SIZE = 28

# 12 emoji pairs (visible and distinct)
EMOJIS = [
    "🍎", "🍌", "🍇", "🍓", "🍒", "🍍",
    "🍑", "🥝", "🍉", "🍋", "🍊", "🥥",
]


def build_layout(cols: int, rows: int) -> str:
    # Independent buttons: use backtick to mark no-merge empty tokens
    row = ",".join(["`"] * cols)
    return "\n".join([row for _ in range(rows)])


def main() -> None:
    layout = build_layout(COLS, ROWS)
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=80,
        cell_height=80,
        h_gap=6,
        v_gap=6,
        border=10,
        title="Memory Puzzle",
        default_bg_color=HIDDEN_BG,
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )

    # Game state
    board: List[List[str]] = [["" for _ in range(COLS)] for _ in range(ROWS)]
    revealed: List[List[bool]] = [[False for _ in range(COLS)] for _ in range(ROWS)]
    matched: List[List[bool]] = [[False for _ in range(COLS)] for _ in range(ROWS)]

    state = {
        "first": None,        # type: Tuple[int, int] | None
        "lock": False,
        "tries": 0,
    }

    def set_cell_ui(x: int, y: int) -> None:
        el = pad[x, y]  # type: ignore[index]
        val = board[y][x]
        if matched[y][x]:
            el.text = val
            el.background_color = MATCHED_BG
        elif revealed[y][x]:
            el.text = val
            el.background_color = REVEAL_BG
        else:
            el.text = ""
            el.background_color = HIDDEN_BG
        el.text_color = TEXT_COLOR
        el.font_size = FONT_SIZE

    def update_ui() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                set_cell_ui(x, y)

    def all_matched() -> bool:
        for y in range(ROWS):
            for x in range(COLS):
                if not matched[y][x]:
                    return False
        return True

    def new_game() -> None:
        # Prepare shuffled board of emoji pairs
        cards = EMOJIS * 2
        random.shuffle(cards)
        i = 0
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = cards[i]
                revealed[y][x] = False
                matched[y][x] = False
                i += 1
        state["first"] = None
        state["lock"] = False
        state["tries"] = 0
        update_ui()

    def reveal(x: int, y: int) -> None:
        revealed[y][x] = True
        set_cell_ui(x, y)

    def hide(x: int, y: int) -> None:
        revealed[y][x] = False
        set_cell_ui(x, y)

    def mark_matched(a: Tuple[int, int], b: Tuple[int, int]) -> None:
        ax, ay = a
        bx, by = b
        matched[ay][ax] = True
        matched[by][bx] = True
        set_cell_ui(ax, ay)
        set_cell_ui(bx, by)

    def on_cell_click(_el, x: int, y: int) -> None:
        if state["lock"]:
            return
        if matched[y][x] or revealed[y][x]:
            return

        # First reveal
        if state["first"] is None:
            state["first"] = (x, y)
            reveal(x, y)
            return

        # Second reveal
        fx, fy = state["first"]
        state["first"] = None
        reveal(x, y)
        state["tries"] += 1

        # Check match
        if board[fy][fx] == board[y][x]:
            mark_matched((fx, fy), (x, y))
            if all_matched():
                try:
                    buttonpad.alert(f"You win!\nTries: {state['tries']}")
                except Exception:
                    pass
                new_game()
        else:
            state["lock"] = True
            def flip_back():
                hide(fx, fy)
                hide(x, y)
                state["lock"] = False
            pad.root.after(700, flip_back)

    # Wire up clicks
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_cell_click  # type: ignore[index]
            # initialize styling
            el = pad[x, y]  # type: ignore[index]
            el.text = ""
            el.background_color = HIDDEN_BG
            el.text_color = TEXT_COLOR
            el.font_size = FONT_SIZE

    # Start the game
    new_game()

    pad.run()


if __name__ == "__main__":
    main()
