from __future__ import annotations

# Othello (Reversi) vs CPU: 8x8 grid of buttons using ButtonPad.
# - Window background is brown
# - Cell background starts slightly dark green
# - Human is WHITE; CPU is BLACK; BLACK moves first
# - Legal human moves are shown as a yellow dot (text) on empty cells
# - CPU replies automatically
# - When no moves for either side, the winner's color slowly flashes for a few seconds, then the board resets

import buttonpad
from typing import List, Tuple, Optional

TITLE = "Othello (vs CPU)"
SIZE = 8

# UI
CELL_W = 46
CELL_H = 46
HGAP = 2
VGAP = 2
BORDER = 12
WINDOW_BG = "#6b4e2e"      # brown window
BOARD_BG = "#2f6d2f"       # slightly dark green for cells
WHITE_BG = "#ffffff"
BLACK_BG = "#111111"
TEXT_DEFAULT = "white"
HINT_COLOR = "#ffd54a"     # warm yellow for move hints
HINT_CHAR = "."
SYMBOL_FONT_SIZE = 18

# Players
EMPTY = 0
WHITE = 1  # human
BLACK = 2  # cpu

# Directions
DIRS: Tuple[Tuple[int, int], ...] = (
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1),
)


def build_layout() -> str:
    row = ",".join(["`"] * SIZE)
    return "\n".join([row for _ in range(SIZE)])


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < SIZE and 0 <= y < SIZE


def opponent(p: int) -> int:
    return BLACK if p == WHITE else WHITE


def find_flips(board: List[List[int]], p: int, x: int, y: int) -> List[Tuple[int, int]]:
    if board[y][x] != EMPTY:
        return []
    flips: List[Tuple[int, int]] = []
    opp = opponent(p)
    for dx, dy in DIRS:
        cx, cy = x + dx, y + dy
        line: List[Tuple[int, int]] = []
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


def legal_moves(board: List[List[int]], p: int) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] == EMPTY and find_flips(board, p, x, y):
                out.append((x, y))
    return out


def any_move(board: List[List[int]], p: int) -> bool:
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] == EMPTY and find_flips(board, p, x, y):
                return True
    return False


def choose_cpu_move(board: List[List[int]]) -> Optional[Tuple[int, int]]:
    """Pick a legal move for BLACK using a simple greedy strategy (maximize flips).
    If tie, prefer corners > center > edges.
    """
    moves = legal_moves(board, BLACK)
    if not moves:
        return None

    def move_score(mv: Tuple[int, int]) -> Tuple[int, int, int, int]:
        x, y = mv
        flips = len(find_flips(board, BLACK, x, y))
        # corner bonus
        corner = 1 if (x, y) in ((0, 0), (0, SIZE - 1), (SIZE - 1, 0), (SIZE - 1, SIZE - 1)) else 0
        # center proximity (smaller distance is better -> invert)
        cx = abs(x - (SIZE // 2 - 0)) + abs(y - (SIZE // 2 - 0))
        center_pref = -cx
        # edges slightly preferred
        edge = 1 if (x in (0, SIZE - 1) or y in (0, SIZE - 1)) else 0
        return (flips, corner, center_pref, edge)

    moves.sort(key=move_score, reverse=True)
    return moves[0]


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
        default_bg_color=BOARD_BG,
        default_text_color=TEXT_DEFAULT,
        window_color=WINDOW_BG,
        resizable=True,
    )

    board: List[List[int]] = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    cells = [pad[x, y] for y in range(SIZE) for x in range(SIZE)]  # type: ignore[list-item]

    state = {"turn": BLACK, "over": False}

    def set_cell_color(x: int, y: int, who: int) -> None:
        el = pad[x, y]  # type: ignore[index]
        if who == EMPTY:
            el.background_color = BOARD_BG
        elif who == WHITE:
            el.background_color = WHITE_BG
        else:
            el.background_color = BLACK_BG

    def update_ui(show_hints: bool = True) -> None:
        # Apply backgrounds according to board; clear text; optionally add hints for human
        for y in range(SIZE):
            for x in range(SIZE):
                set_cell_color(x, y, board[y][x])
                el = pad[x, y]  # type: ignore[index]
                el.text = ""
                el.text_color = TEXT_DEFAULT
                el.font_size = SYMBOL_FONT_SIZE
        if show_hints and state["turn"] == WHITE and not state["over"]:
            for x, y in legal_moves(board, WHITE):
                el = pad[x, y]  # type: ignore[index]
                el.text = HINT_CHAR
                el.text_color = HINT_COLOR
                el.font_size = SYMBOL_FONT_SIZE

    def reset_game() -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                board[y][x] = EMPTY
        mid = SIZE // 2
        board[mid - 1][mid - 1] = WHITE
        board[mid][mid] = WHITE
        board[mid - 1][mid] = BLACK
        board[mid][mid - 1] = BLACK
        state["turn"] = BLACK
        state["over"] = False
        # No human hints when BLACK starts; schedule first CPU move
        update_ui(show_hints=False)
        try:
            pad.root.after(250, cpu_move)
        except Exception:
            pass

    def end_and_flash_winner() -> None:
        # Count discs
        wcnt = sum(1 for row in board for v in row if v == WHITE)
        bcnt = sum(1 for row in board for v in row if v == BLACK)
        if wcnt == bcnt:
            # tie: flash between board green and both colors? Keep simple: alternate white/black
            sequence = [WHITE_BG, BLACK_BG]
        else:
            winner_bg = WHITE_BG if wcnt > bcnt else BLACK_BG
            sequence = [winner_bg, BOARD_BG]

        state["over"] = True
        flashes = 10  # ~3 seconds at 300ms per toggle
        interval_ms = 300

        def step(i: int) -> None:
            color = sequence[i % len(sequence)]
            for el in cells:
                el.background_color = color
                el.text = ""
            if i + 1 < flashes:
                pad.root.after(interval_ms, lambda: step(i + 1))
            else:
                pad.root.after(300, reset_game)

        step(0)

    def place_and_flip(p: int, x: int, y: int) -> bool:
        flips = find_flips(board, p, x, y)
        if not flips:
            return False
        board[y][x] = p
        for fx, fy in flips:
            board[fy][fx] = p
        update_ui(show_hints=(p != BLACK))  # after placing, show hints only if next is human
        return True

    def advance_turn() -> None:
        # After a legal move, switch turns with pass logic; if no moves for either, end
        p = state["turn"]
        np = opponent(p)
        if any_move(board, np):
            state["turn"] = np
        elif any_move(board, p):
            state["turn"] = p  # opponent passes
        else:
            end_and_flash_winner()
            return
        update_ui(show_hints=(state["turn"] == WHITE))
        if state["turn"] == BLACK and not state["over"]:
            # Let UI breathe, then CPU moves
            pad.root.after(200, cpu_move)

    def handle_click(_el, x: int, y: int) -> None:
        if state["over"] or state["turn"] != WHITE:
            return
        if board[y][x] != EMPTY:
            return
        if not place_and_flip(WHITE, x, y):
            return
        advance_turn()

    def cpu_move() -> None:
        if state["over"] or state["turn"] != BLACK:
            return
        mv = choose_cpu_move(board)
        if mv is None:
            advance_turn()
            return
        x, y = mv
        if not place_and_flip(BLACK, x, y):
            # Shouldn't happen; try any legal move
            moves = legal_moves(board, BLACK)
            if not moves:
                advance_turn()
                return
            x, y = moves[0]
            place_and_flip(BLACK, x, y)
        advance_turn()

    # Wire handlers
    for y in range(SIZE):
        for x in range(SIZE):
            pad[x, y].on_click = handle_click  # type: ignore[index]
            pad[x, y].font_size = SYMBOL_FONT_SIZE  # type: ignore[index]

    reset_game()
    pad.run()


if __name__ == "__main__":
    main()
