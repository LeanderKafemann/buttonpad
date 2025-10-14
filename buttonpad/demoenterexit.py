"""Demonstration of the on_enter / on_exit hover callbacks in ButtonPad.

Beginner notes:
    * Each cell in the 6x6 grid is a Label-like widget you can interact with.
    * on_enter is called when the mouse cursor moves into a cell.
    * on_exit is called when the mouse cursor leaves that cell.
    * We simply change the background color and print which cell was entered
        or exited so you can see the events firing.
"""

import buttonpad

bp = buttonpad.ButtonPad(
    """
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    """,  # 6 lines each with 6 cells gives us a 6x6 grid
    window_bg_color="lightgray",
    default_bg_color="lightgray",
    title="Mouse Enter/Exit Demo"
)

def on_enter(widget, x, y):
    """Called when mouse cursor enters a cell.

    Parameters:
        widget: The ButtonPad cell element object.
        x, y: The coordinates of the cell in the grid.
    """
    print(f"Entered {x}, {y}")  # Show event in terminal
    widget.bg_color = "lightblue"  # Highlight cell under cursor

def on_exit(widget, x, y):
    """Called when mouse cursor leaves a cell.

    We revert the highlight color back to the default.
    """
    print(f"Exited {x}, {y}")
    widget.bg_color = "lightgray"

for x in range(6):
    for y in range(6):
        # Assign the same handlers to every cell in the grid.
        bp[x, y].on_enter = on_enter
        bp[x, y].on_exit = on_exit

bp.run()  # Start the Tkinter event loop.