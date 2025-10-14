from __future__ import annotations
import buttonpad

# ---------- ButtonPad layout ----------
# Row 0: wide label spanning all 4 columns.
# Rows 1-5: calculator buttons.
LAYOUT = f"""
'','','',''
C,(,),{chr(9003)}
7,8,9,÷
4,5,6,x
1,2,3,-
0,.,=,+
""".strip()

def handle_click_equals(widget: buttonpad.BPWidgetType, x: int, y: int) -> None:
    """
    Handle click event for the equals button.
    """
    s = display.text.strip()
    if not s:
        return
    try:
        # Translate display symbols to Python operators
        result = eval(s.replace("x", "*").replace("÷", "/"))
        # Normalize int-like floats
        if isinstance(result, float) and result.is_integer():
            display.text = str(int(result))
        else:
            display.text = str(result)
    except Exception:
        display.text = "Error"

def handle_click_clear(widget: buttonpad.BPWidgetType, x: int, y: int) -> None:
    """
    Handle click event for the clear button.
    """
    display.text = ""

def handle_click_backspace(widget: buttonpad.BPWidgetType, x: int, y: int) -> None:
    """
    Handle click event for the backspace button.
    """
    display.text = display.text[:-1]

def handle_click_button(widget: buttonpad.BPWidgetType, x: int, y: int) -> None:
    """
    Handle click event for a number/operator button.
    """
    display.text += widget.text


def main() -> None:
    global display
    
    bp = buttonpad.ButtonPad(
        layout=LAYOUT,
        cell_width=70,
        cell_height=[50, 60, 60, 60, 60, 60],  # taller display row
        padx=6,
        pady=6,
        window_bg_color="gray",
        default_bg_color="white",
        default_text_color="#2c2c2c",
        title="ButtonPad Calculator",
        resizable=True,
        border=10,
    )

    # Set up buttons to add their label to the display:
    for x in range(3):
        for y in range(1, 6):
            el = bp[x, y]
            el.on_click = handle_click_button
            el.font_size = 16

    # Assign widgets to variables for readability:
    display = bp[0, 0]
    clear_button = bp[0, 1]
    equal_button = bp[2, 5]
    backspace_button = bp[3, 1]
    divide_button = bp[3, 2]
    multiply_button = bp[3, 3]
    subtract_button = bp[3, 4]
    add_button = bp[3, 5]

    # The display is the merged label at the top-left cell (it spans all columns).
    display.anchor = 'w'
    display.bg_color = "white"
    display.font_size = 18
    display.text = ""  # start empty

    # Set up clear button:
    clear_button.bg_color = "#7a1f1f"
    clear_button.text_color = "white"
    clear_button.on_click = handle_click_clear
    clear_button.hotkey = ("Escape", "c")

    # Set up equal button:
    equal_button.bg_color = "#007acc"
    equal_button.text_color = "white"
    equal_button.on_click = handle_click_equals
    equal_button.hotkey = "Return"  # Enter key

    # Set up backspace button:
    backspace_button.bg_color = "#444444"
    backspace_button.text_color = "white"
    backspace_button.on_click = handle_click_backspace
    backspace_button.hotkey = "BackSpace"

    # Set up math operator buttons:
    for y in range(2, 6):
        bp[3, y].on_click = handle_click_button
        bp[3, y].bg_color = "#3a3a3a"
        bp[3, y].text_color = "white"
    
    # Setup hotkeys:
    backspace_button.hotkey = "BackSpace"
    for x in range(3):
        for y in range(1, 6):
            bp[x, y].hotkey = bp[x, y].text
    clear_button.hotkey += ("Escape",)
    equal_button.hotkey += ("Return",)  # Enter key
    divide_button.hotkey = "/"
    multiply_button.hotkey = "*"
    subtract_button.hotkey = "-"
    add_button.hotkey = "+"

    bp.run()


if __name__ == "__main__":
    main()
