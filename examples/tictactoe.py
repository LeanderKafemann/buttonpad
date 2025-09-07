from __future__ import annotations

import buttonpad
from typing import List, Optional, Tuple

SIZE = 3

# UI tuning
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
        cell_width=72,
        cell_height=72,
        h_gap=4,
        v_gap=4,
        border=12,
        title="Tic Tac Toe",
        default_bg_color=EMPTY_BG,
        default_text_color=TEXT_COLOR,
        window_color="#ffffff",
    resizable=False,
    status_bar="X Wins: 0  O Wins: 0  Ties: 0",
    )

    # Board state: "", "X", or "O"
    board: List[List[str]] = [["" for _ in range(SIZE)] for _ in range(SIZE)]
    cells = [pad[x, y] for y in range(SIZE) for x in range(SIZE)]  # type: ignore[list-item]

    state = {"who": "X", "over": False, "x_wins": 0, "o_wins": 0, "ties": 0}

    def update_status_bar() -> None:
        try:
            pad.status_bar = f"X Wins: {state['x_wins']}  O Wins: {state['o_wins']}  Ties: {state['ties']}"
        except Exception:
            pass

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
    def end_game(sym: Optional[str]) -> None:
        """Announce winner (sym) or tie (None) and reset."""
        state["over"] = True
        # Increment counters before alert
        if sym is None:
            state["ties"] += 1
        elif sym == "X":
            state["x_wins"] += 1
        else:
            state["o_wins"] += 1
        try:
            if sym is None:
                buttonpad.alert("It's a tie!")
            else:
                buttonpad.alert(f"{sym} wins!")
        except Exception:
            pass
        update_status_bar()
        reset_board()

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
            end_game(w)
            return
        if board_full(board):
            end_game(None)
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
