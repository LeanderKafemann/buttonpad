"""Interactive telephone keypad demo using ButtonPad.

Differences from the simpler `demophonekeypad.py` example:
    * Includes a top "Display" area (a merged text box) that shows the digits
        pressed.
    * Each key updates the display and a status bar message.
    * A delete/backspace key (Unicode erase symbol) removes the last digit.

Beginner notes:
    * ButtonPad builds the interface from a multi-line layout string.
    * Square brackets like [Display] create a merged cell spanning all repeated
        occurrences in that row.
    * We look up cells by (x, y) coordinates starting at (0,0) in the upper-left.
    * Event handler functions always receive (widget, x, y) arguments.
"""

import buttonpad

def press_label(widget, x, y):
    """Handler for normal digit / symbol buttons.

    Appends the button's text to the display and shows a status bar message.
    """
    print(widget.text)  # Also echo to terminal
    display.text += widget.text  # Append the pressed key to the display
    bp.status_bar = f"Pressed {widget.text}"  # Feedback for the user

def press_del(widget, x, y):
    """Handler for the delete key: remove the last character from display."""
    display.text = display.text[:-1]

if __name__ == "__main__":
    # Layout string: first row is a merged [Display] across 3 columns.
    # Last row places the delete key (Unicode BACKSPACE ERASE SYMBOL) at the center.
    delete_symbol = chr(9003)  # Looks like ⌫
    bp = buttonpad.ButtonPad(
        f"""
        [Display], [Display], [Display]
        1,2,3
        4,5,6
        7,8,9
        *,0,#
        '',{delete_symbol},''""",
        title="Telephone Keypad Demo",
        cell_width=70,
        cell_height=100,
        padx=20,
        pady=10,
        border=40,
        default_bg_color='khaki',
        default_text_color='darkblue',
        window_bg_color='DarkSeaGreen1',
    )

    # Status bar shows recent key presses.
    bp.status_bar = ''

    # The display text box resides at (0,0); since it's merged we only access its top-left cell.
    display: buttonpad.BPTextBox = bp[0,0]

    # Assign digit/symbol handlers (skip delete row y=5 and the display row y=0)
    for x in range(3):
        for y in range(1, 5):  # rows 1-4 contain keys 1..9,*,0,#
            bp[x,y].on_click = press_label

    # Delete key lives at center bottom (column 1, row 5)
    bp[1, 5].on_click = press_del

    # Start with an empty display.
    bp[0,0].text = ''

    bp.run()  # Start the GUI event loop.
