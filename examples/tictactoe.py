from __future__ import annotations

# Tic Tac Toe: 3x3 grid of buttons for two human players.
# - X goes first
# - Clicking a button places X or O
# - If tie, the board flashes with blank text on all nine spaces
# - If someone wins, their symbol (X or O) flashes on all spaces

import buttonpad
from typing import List, Optional, Tuple

TITLE = "Tic Tac Toe"
SIZE = 3

# UI tuning
CELL_W = 72
CELL_H = 72
HGAP = 4
VGAP = 4
BORDER = 12
EMPTY_BG = "#f0f0f0"
TEXT_COLOR = "#222222"


def build_layout() -> str:
    row = ",".join(["`"] * SIZE)
    return "\n".join([row for _ in range(SIZE)])


def winner(board: List[List[str]]) -> Optional[str]:
    # Returns "X" or "O" if someone has won, otherwise None
    lines: List[List[Tuple[int, int]]] = []
    # Rows and columns
    for i in range(SIZE):
        lines.append([(x, i) for x in range(SIZE)])
        lines.append([(i, y) for y in range(SIZE)])
    # Diagonals
    lines.append([(i, i) for i in range(SIZE)])
    lines.append([(i, SIZE - 1 - i) for i in range(SIZE)])

    for line in lines:
        vals = [board[y][x] for (x, y) in line]
        if vals[0] and all(v == vals[0] for v in vals):
            return vals[0]
    return None


def board_full(board: List[List[str]]) -> bool:
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] == "":
                return False
    return True


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
        default_bg_color=EMPTY_BG,
        default_text_color=TEXT_COLOR,
        window_color="#ffffff",
        resizable=False,
    )

    # Board state: "", "X", or "O"
    board: List[List[str]] = [["" for _ in range(SIZE)] for _ in range(SIZE)]
    cells = [pad[x, y] for y in range(SIZE) for x in range(SIZE)]  # type: ignore[list-item]

    state = {"who": "X", "over": False}

    def update_ui() -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                el = pad[x, y]  # type: ignore[index]
                el.text = board[y][x]
                el.font_size = 28

    def reset_board() -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                board[y][x] = ""
        update_ui()
        state["who"] = "X"
        state["over"] = False

    def flash_winner(sym: str, flashes: int = 6, interval_ms: int = 180) -> None:
        state["over"] = True

        def step(i: int) -> None:
            show = (i % 2 == 0)
            for el in cells:
                el.text = sym if show else ""
                el.font_size = 28
            if i + 1 < flashes:
                pad.root.after(interval_ms, lambda: step(i + 1))
            else:
                pad.root.after(220, reset_board)

        step(0)

    def flash_tie(flashes: int = 6, interval_ms: int = 180) -> None:
        state["over"] = True
        # Snapshot original texts to flash between blank and original
        snapshot = [el.text for el in cells]

        def step(i: int) -> None:
            blank_phase = (i % 2 == 0)
            for idx, el in enumerate(cells):
                el.text = "" if blank_phase else snapshot[idx]
                el.font_size = 28
            if i + 1 < flashes:
                pad.root.after(interval_ms, lambda: step(i + 1))
            else:
                pad.root.after(220, reset_board)

        step(0)

    def handle_click(el, x: int, y: int) -> None:
        if state["over"]:
            return
        if board[y][x] != "":
            return
        who = state["who"]
        board[y][x] = who
        el.text = who
        el.font_size = 28

        w = winner(board)
        if w is not None:
            flash_winner(w)
            return
        if board_full(board):
            flash_tie()
            return
        state["who"] = "O" if who == "X" else "X"

    # Wire handlers
    for y in range(SIZE):
        for x in range(SIZE):
            pad[x, y].on_click = handle_click  # type: ignore[index]
            pad[x, y].font_size = 28  # type: ignore[index]

    update_ui()
    pad.run()


if __name__ == "__main__":
    main()
