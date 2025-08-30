from __future__ import annotations

# Tic Tac Toe vs CPU (O): 3x3 grid.
# - Human is X and goes first
# - Clicking an empty cell places X; computer replies with O
# - If tie, board flashes blanks on all nine cells
# - If win, the winner's symbol flashes on all nine cells

import buttonpad
from typing import List, Optional, Tuple

TITLE = "Tic Tac Toe (vs CPU)"
SIZE = 3

# UI tuning
CELL_W = 72
CELL_H = 72
HGAP = 4
VGAP = 4
BORDER = 12
EMPTY_BG = "#f0f0f0"
TEXT_COLOR = "#222222"

Coord = Tuple[int, int]


def build_layout() -> str:
    row = ",".join(["`"] * SIZE)
    return "\n".join([row for _ in range(SIZE)])


def winner(board: List[List[str]]) -> Optional[str]:
    # Returns "X" or "O" if someone has won, else None
    lines: List[List[Coord]] = []
    for i in range(SIZE):
        lines.append([(x, i) for x in range(SIZE)])  # rows
        lines.append([(i, y) for y in range(SIZE)])  # cols
    lines.append([(i, i) for i in range(SIZE)])      # diag
    lines.append([(i, SIZE - 1 - i) for i in range(SIZE)])  # anti-diag

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


def empty_cells(board: List[List[str]]) -> List[Coord]:
    return [(x, y) for y in range(SIZE) for x in range(SIZE) if board[y][x] == ""]


def choose_cpu_move(board: List[List[str]]) -> Optional[Coord]:
    # Simple strategy: win if possible; block if needed; center; corner; side
    empties = empty_cells(board)
    if not empties:
        return None

    def try_place(sym: str) -> Optional[Coord]:
        for x, y in empties:
            board[y][x] = sym
            if winner(board) == sym:
                board[y][x] = ""
                return (x, y)
            board[y][x] = ""
        return None

    # 1) winning move for O
    mv = try_place("O")
    if mv:
        return mv
    # 2) block X
    mv = try_place("X")
    if mv:
        return mv
    # 3) center
    if board[1][1] == "":
        return (1, 1)
    # 4) corners
    for x, y in [(0, 0), (2, 0), (0, 2), (2, 2)]:
        if board[y][x] == "":
            return (x, y)
    # 5) sides
    for x, y in [(1, 0), (0, 1), (2, 1), (1, 2)]:
        if board[y][x] == "":
            return (x, y)
    # Fallback
    return empties[0]


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

    board: List[List[str]] = [["" for _ in range(SIZE)] for _ in range(SIZE)]
    cells = [pad[x, y] for y in range(SIZE) for x in range(SIZE)]  # type: ignore[list-item]

    state = {"who": "X", "over": False}  # X = human, O = cpu

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

    def after_move_checks() -> bool:
        w = winner(board)
        if w is not None:
            flash_winner(w)
            return True
        if board_full(board):
            flash_tie()
            return True
        return False

    def cpu_move() -> None:
        if state["over"] or state["who"] != "O":
            return
        mv = choose_cpu_move(board)
        if mv is None:
            # no move (should mean tie)
            if not after_move_checks():
                flash_tie()
            return
        x, y = mv
        if board[y][x] != "":
            # Safety: find any empty
            empties = empty_cells(board)
            if not empties:
                if not after_move_checks():
                    flash_tie()
                return
            x, y = empties[0]
        board[y][x] = "O"
        pad[x, y].text = "O"  # type: ignore[index]
        pad[x, y].font_size = 28  # type: ignore[index]
        if after_move_checks():
            return
        state["who"] = "X"

    def handle_click(el, x: int, y: int) -> None:
        if state["over"] or state["who"] != "X":
            return
        if board[y][x] != "":
            return
        board[y][x] = "X"
        el.text = "X"
        el.font_size = 28
        if after_move_checks():
            return
        state["who"] = "O"
        # Give a small delay for UX
        pad.root.after(120, cpu_move)

    # Wire handlers and baseline font size
    for y in range(SIZE):
        for x in range(SIZE):
            pad[x, y].on_click = handle_click  # type: ignore[index]
            pad[x, y].font_size = 28  # type: ignore[index]

    update_ui()
    pad.run()


if __name__ == "__main__":
    main()
