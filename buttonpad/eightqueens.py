"""Eight Queens puzzle using ButtonPad.

Goal: Place 8 queens (♛) on the 8x8 board so that none can attack another.
Click a square to toggle a queen on/off. When all 8 queens are placed with
no conflicts (no shared row, column, or diagonal), an alert is shown and
the board resets so you can try another arrangement.

Beginner notes:
  * We build an 8x8 grid layout (each ` token makes an independent button).
  * A set `queens` stores (x, y) tuples where queens are placed.
  * Clicking toggles a queen: add if absent, remove if present.
  * After each toggle we test for a solved board.
  * A board is solved when there are exactly 8 queens and none attack each other.
"""
from __future__ import annotations

from typing import Set, Tuple, Optional

import buttonpad  # local package

# Type alias for clarity
XYCoord = Tuple[int, int]

# Global references (assigned in main()) so callbacks can be simple top-level functions.
pad: Optional[buttonpad.ButtonPad] = None
queens: Set[XYCoord] = set()

# Checkerboard colors (use light gray instead of black). Lower-right (7,7) must be white.
WHITE_SQUARE = "#ffffff"
LIGHT_GRAY_SQUARE = "#d9d9d9"


def square_color(x: int, y: int) -> str:
    """Return the base background color for square (x,y) so that (7,7) is white.

    We choose white for even (x+y) so (7,7) -> 14 (even) -> white.
    """
    return WHITE_SQUARE if (x + y) % 2 == 0 else LIGHT_GRAY_SQUARE


def build_layout() -> str:
    """Return an 8x8 grid of independent buttons (backtick tokens)."""
    row = ",".join(["`"] * 8)
    return "\n".join([row for _ in range(8)])


def attacks(a: XYCoord, b: XYCoord) -> bool:
    """Return True if queens at positions a and b can attack each other.

    Queens attack along rows, columns, and diagonals. Positions are (x,y) with
    (0,0) at the top-left.
    """
    (ax, ay), (bx, by) = a, b
    return (
        ax == bx  # same column
        or ay == by  # same row
        or abs(ax - bx) == abs(ay - by)  # diagonal (slope ±1)
    )


def is_solved(queens: Set[XYCoord]) -> bool:
    """Return True if exactly 8 queens are placed and none attack each other."""
    if len(queens) != 8:
        return False
    qlist = list(queens)
    for i in range(len(qlist)):
        for j in range(i + 1, len(qlist)):
            if attacks(qlist[i], qlist[j]):
                return False
    return True


def redraw() -> None:
    """Update every cell's displayed text to reflect queen placements (global state)."""
    if pad is None:
        return
    
    # Find all attacking queen positions
    attacking_positions = set()
    qlist = list(queens)
    for i in range(len(qlist)):
        for j in range(i + 1, len(qlist)):
            if attacks(qlist[i], qlist[j]):
                attacking_positions.add(qlist[i])
                attacking_positions.add(qlist[j])
    
    for y in range(8):
        for x in range(8):
            cell = pad[x, y]  # type: ignore[index]
            cell.text = "♛" if (x, y) in queens else ""
            cell.font_size = 34
            
            # Choose background color: red for attacking queens, otherwise checkerboard
            if (x, y) in attacking_positions:
                cell.bg_color = "#ff6666"  # light red for attacking queens
            else:
                cell.bg_color = square_color(x, y)  # normal checkerboard


def toggle(_el, x: int, y: int) -> None:
    """Toggle a queen at (x,y); check for solution and reset if solved (global state)."""
    if pad is None:
        return
    if (x, y) in queens:
        queens.remove((x, y))
    else:
        queens.add((x, y))
    redraw()
    if is_solved(queens):
        buttonpad.alert("Puzzle solved.")
        queens.clear()
        redraw()


def main() -> None:
    """Create the UI, bind handlers, and start the event loop."""
    global pad, queens
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout,
        cell_width=60,
        cell_height=60,
        padx=0,
        pady=0,
        border=12,
        title="Eight Queens Puzzle",
        default_bg_color="#f0f0f0",
        default_text_color="black",
        resizable=True,
    )
    queens = set()  # reset
    for y in range(8):
        for x in range(8):
            pad[x, y].on_click = toggle  # type: ignore[index]
    redraw()
    pad.run()


if __name__ == "__main__":
    main()
