from __future__ import annotations

# Flood-It using ButtonPad
# - Top: 18 x 18 grid of color cells
# - Middle row: controls and scores
# - Bottom row: six 3x1 color buttons to pick the next color

from typing import List, Tuple, Dict
import random

try:
    import buttonpad  # local module name
except Exception:
    import ButtonPad as buttonpad  # type: ignore

TITLE = "Flood-It"
COLS = 18
ROWS = 18  # board only; layout adds 2 more rows (info + palette)

# UI
CELL_W = 26
CELL_H = 26
HGAP = 2
VGAP = 2
BORDER = 10
WINDOW_BG = "#f5f5f5"
TEXT_COLOR = "#222222"

# After random fill, perform extra smoothing iterations by copying
# a random neighbor's color into random cells to increase contiguity.
# Adjustable constant; default ties to board size.
SMOOTHING_STEPS = COLS * ROWS // 4

# Six distinct pleasant colors
PALETTE = [
    "green",
    "red",
    "blue",
    "yellow",
    "purple",
    "orange",
]

Coord = Tuple[int, int]


def build_layout(initial_seed: int) -> str:
    # Top 18x18: no-merge labels (blank text)
    top_row = ",".join(["`''"] * COLS)
    top = "\n".join([top_row for _ in range(ROWS)])

    # Info row (y = ROWS):
    # 3x 'Puzzle Seed:' label (we'll set newlines programmatically)
    # 4x [seed]
    # 3x 'New\nPuzzle' button
    # 3x 'Best\nScore:' label
    # 2x '' label (best value)
    # 2x 'Current\nScore:' label
    # 1x '' label (current value)
    info: List[str] = []
    info += ["'Puzzle Seed:'"] * 3
    info += [f"[{initial_seed}]"] * 4
    info += ["New Puzzle"] * 3
    info += ["'Best Score:'"] * 3
    info += ["''"] * 2
    info += ["'Current Score:'"] * 2
    info += ["''"] * 1
    info_row = ",".join(info)

    # Bottom palette row (y = ROWS+1): six groups of 3 identical tokens
    # Use unique tokens C1..C6 so they merge by 3 columns each
    pal_tokens: List[str] = []
    for i in range(6):
        token = f"C{i+1}"
        pal_tokens += [token] * 3
    palette_row = ",".join(pal_tokens)

    return "\n".join([top, info_row, palette_row])


def all_same_color(board: List[List[int]]) -> bool:
    first = board[0][0]
    for row in board:
        for v in row:
            if v != first:
                return False
    return True


def flood_fill(board: List[List[int]], x: int, y: int, new_color: int) -> int:
    """Flood fill from (x,y); returns number of cells changed. Uses iterative BFS."""
    rows = len(board)
    cols = len(board[0]) if rows else 0
    orig = board[y][x]
    if orig == new_color:
        return 0
    q: List[Coord] = [(x, y)]
    changed = 0
    while q:
        cx, cy = q.pop()
        if board[cy][cx] != orig:
            continue
        board[cy][cx] = new_color
        changed += 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and board[ny][nx] == orig:
                q.append((nx, ny))
    return changed


def main() -> None:
    # Initial random seed for the first puzzle: 4-digit number
    initial_seed = random.randint(1000, 9999)
    layout = build_layout(initial_seed)
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=CELL_W,
        cell_height=CELL_H,
        h_gap=HGAP,
        v_gap=VGAP,
        border=BORDER,
        title=TITLE,
        default_bg_color=WINDOW_BG,
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )

    # Board state: ints 0..5
    board: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    moves = {"count": 0}
    best_scores: Dict[int, int] = {}

    # Element references (using merged top-left cells)
    # Info row y = ROWS
    seed_label = pad[0, ROWS]
    seed_entry = pad[3, ROWS]       # 4-wide merged entry starts at x=3
    new_btn = pad[7, ROWS]
    best_label = pad[10, ROWS]
    best_val_label = pad[13, ROWS]  # 2-wide label starts at x=13
    cur_label = pad[15, ROWS]
    cur_val_label = pad[17, ROWS]

    # Palette row y = ROWS + 1, starts at x = 0,3,6,9,12,15
    palette_buttons = [pad[i * 3, ROWS + 1] for i in range(6)]

    # Style palette buttons
    for i, el in enumerate(palette_buttons):
        el.text = ""
        el.background_color = PALETTE[i]

    # Multi-line texts set programmatically (to ensure newlines render)
    seed_label.text = "Puzzle\nSeed:"
    new_btn.text = "New\nPuzzle"
    best_label.text = "Best\nScore:"
    cur_label.text = "Current\nScore:"

    # Helper: update visuals of the 18x18 board
    def update_board_ui() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                el = pad[x, y]  # type: ignore[index]
                el.text = ""
                el.background_color = PALETTE[board[y][x]]

    def update_scores_ui(seed_val: int) -> None:
        # Best score for this seed (if any)
        if seed_val in best_scores:
            best_val_label.text = str(best_scores[seed_val])
        else:
            best_val_label.text = "-"
        cur_val_label.text = str(moves["count"])

    current_seed = {"value": initial_seed}

    def parse_seed() -> int:
        try:
            return int(seed_entry.text.strip())
        except Exception:
            # If invalid, generate a new one and set it
            s = random.randint(1000, 9999)
            seed_entry.text = str(s)
            return s

    def new_puzzle() -> None:
        # Use the seed from the entry
        s = parse_seed()
        random.seed(s)
        current_seed["value"] = s
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = random.randrange(0, 6)
        # Optional: avoid starting with full board same color
        if all_same_color(board):
            board[0][0] = (board[0][0] + 1) % 6
        # Increase contiguous regions by copying colors from neighbors
        for _ in range(SMOOTHING_STEPS):
            x = random.randrange(0, COLS)
            y = random.randrange(0, ROWS)
            neighbors = []
            if x > 0:
                neighbors.append((x - 1, y))
            if x < COLS - 1:
                neighbors.append((x + 1, y))
            if y > 0:
                neighbors.append((x, y - 1))
            if y < ROWS - 1:
                neighbors.append((x, y + 1))
            if neighbors:
                nx, ny = random.choice(neighbors)
                board[y][x] = board[ny][nx]
        moves["count"] = 0
        update_board_ui()
        update_scores_ui(s)

    def maybe_finish_and_update_best(seed_val: int) -> None:
        if all_same_color(board):
            cur = moves["count"]
            prev = best_scores.get(seed_val)
            if prev is None or cur < prev:
                best_scores[seed_val] = cur
                best_val_label.text = str(cur)

    def make_pick_handler(color_index: int):
        def _handler(_el, _x, _y):
            s = current_seed["value"]
            # Apply move only if it changes color
            if board[0][0] != color_index:
                flood_fill(board, 0, 0, color_index)
                moves["count"] += 1
                cur_val_label.text = str(moves["count"])
                update_board_ui()
                maybe_finish_and_update_best(s)
        return _handler

    # Wire palette button handlers
    for idx, el in enumerate(palette_buttons):
        el.on_click = make_pick_handler(idx)

    # Wire new puzzle button
    new_btn.on_click = lambda _e, _x, _y: new_puzzle()

    # Set initial seed in entry (already done via layout) and generate first board
    new_puzzle()

    pad.run()


if __name__ == "__main__":
    main()
