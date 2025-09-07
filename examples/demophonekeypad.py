"""Telephone keypad layout demo using ButtonPad.

Beginner notes:
    * ButtonPad creates a grid of clickable buttons/labels from a multi-line
        comma-separated string. Each line represents a row; commas separate cells.
    * Here we arrange the classic telephone keypad digits plus *, 0, and #.
    * There is no additional behavior besides showing the layout; you could add
        on_click handlers to each cell to build a dialer or capture input.
"""

import buttonpad

if __name__ == "__main__":
    # Multi-line string defines 4 rows of 3 cells each (a 3x4 grid).
    bp = buttonpad.ButtonPad(
        """1,2,3
        4,5,6
        7,8,9
        *,0,#""",
        title="Telephone Keypad Demo",
    )
    bp.run()  # Start the GUI event loop.
