from __future__ import annotations

# Othello (Reversi): 8x8 grid of buttons.
# - Window background is black
# - Buttons start with a slightly dark green background
# - Enforces Othello rules: legal moves flip bracketing discs
# - Standard starting position is set

import buttonpad
from typing import List, Tuple

SIZE = 8

# UI
WINDOW_BG = "#6b4e2e"      # brown window
BOARD_BG = "#2f6d2f"       # slightly dark green for cells
WHITE_BG = "#ffffff"
BLACK_BG = "#111111"


def build_layout() -> str:
    row = ",".join(["`"] * SIZE)
    return "\n".join([row for _ in range(SIZE)])


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=46,
        cell_height=46,
        h_gap=2,
        v_gap=2,
        border=12,
        title="Othello",
        default_bg_color=BOARD_BG,
        default_text_color="white",
        window_color=WINDOW_BG,
        resizable=True,
        status_bar="White: 2  Black: 2",
    )

    # 0 empty, 1 white, 2 black
    board: List[List[int]] = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    turn = {"who": 2}  # black starts

    # Directions for scanning flips
    DIRS: Tuple[Tuple[int, int], ...] = (
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),          (1,  0),
        (-1,  1), (0,  1), (1,  1),
    )

    def in_bounds(x: int, y: int) -> bool:
        return 0 <= x < SIZE and 0 <= y < SIZE

    def opponent(p: int) -> int:
        return 2 if p == 1 else 1

    def set_cell_color(x: int, y: int, who: int) -> None:
        widget = pad[x, y]  # type: ignore[index]
        if who == 0:
            widget.background_color = BOARD_BG
        elif who == 1:
            widget.background_color = WHITE_BG
        else:
            widget.background_color = BLACK_BG

    def update_ui() -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                set_cell_color(x, y, board[y][x])
        update_status()

    def update_status() -> None:
        # Count discs and update status bar
        wcnt = sum(1 for row in board for v in row if v == 1)
        bcnt = sum(1 for row in board for v in row if v == 2)
        pad.status_bar = f"White: {wcnt}  Black: {bcnt}"

    def find_flips(p: int, x: int, y: int) -> List[Tuple[int, int]]:
        if board[y][x] != 0:
            return []
        flips: List[Tuple[int, int]] = []
        opp = opponent(p)
        for dx, dy in DIRS:
            cx, cy = x + dx, y + dy
            line: List[Tuple[int, int]] = []
            # Must have at least one opponent disc first
            if not in_bounds(cx, cy) or board[cy][cx] != opp:
                continue
            while in_bounds(cx, cy) and board[cy][cx] == opp:
                line.append((cx, cy))
                cx += dx
                cy += dy
            if not in_bounds(cx, cy):
                continue
            if board[cy][cx] == p and line:
                flips.extend(line)
        return flips

    def has_any_move(p: int) -> bool:
        for yy in range(SIZE):
            for xx in range(SIZE):
                if board[yy][xx] == 0 and find_flips(p, xx, yy):
                    return True
        return False

    def place_and_flip(p: int, x: int, y: int) -> bool:
        flips = find_flips(p, x, y)
        if not flips:
            return False
        board[y][x] = p
        for fx, fy in flips:
            board[fy][fx] = p
        update_ui()
        return True

    # Starting position (center four)
    mid = SIZE // 2
    board[mid - 1][mid - 1] = 1  # white
    board[mid][mid] = 1          # white
    board[mid - 1][mid] = 2      # black
    board[mid][mid - 1] = 2      # black
    update_ui()

    def announce_winner() -> None:
        wcnt = sum(1 for row in board for v in row if v == 1)
        bcnt = sum(1 for row in board for v in row if v == 2)
        if wcnt == bcnt:
            msg = f"Tie game!\nWhite: {wcnt}  Black: {bcnt}"
        elif wcnt > bcnt:
            msg = f"White wins!\nWhite: {wcnt}  Black: {bcnt}"
        else:
            msg = f"Black wins!\nWhite: {wcnt}  Black: {bcnt}"
        try:
            buttonpad.alert(msg, title="Othello Result")
        except Exception:
            pass
        # Reset board state
        for yy in range(SIZE):
            for xx in range(SIZE):
                board[yy][xx] = 0
        mid2 = SIZE // 2
        board[mid2 - 1][mid2 - 1] = 1
        board[mid2][mid2] = 1
        board[mid2 - 1][mid2] = 2
        board[mid2][mid2 - 1] = 2
        turn["who"] = 2
        update_ui()

    def handle_click(_el, x: int, y: int) -> None:
        p = turn["who"]
        moved = place_and_flip(p, x, y)
        if not moved:
            return  # illegal move
        np = opponent(p)
        if has_any_move(np):
            turn["who"] = np
        elif has_any_move(p):
            turn["who"] = p  # opponent passes
        else:
            announce_winner()
            return

    # Wire handlers for all cells
    for y in range(SIZE):
        for x in range(SIZE):
            pad[x, y].on_click = handle_click  # type: ignore[index]

    pad.run()


if __name__ == "__main__":
    main()
