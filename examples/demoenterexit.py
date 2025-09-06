import buttonpad

bp = buttonpad.ButtonPad(
    """
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    `'',`'',`'',`'',`'',`''
    """,
    window_color = "lightgray",
    default_bg_color = "lightgray",
    )

def on_enter(widget, x, y):
    print(f"Entered {x}, {y}")
    widget.background_color = "lightblue"

def on_exit(widget, x, y):
    print(f"Exited {x}, {y}")
    widget.background_color = "lightgray"

for x in range(6):
    for y in range(6):
        bp[x, y].on_enter = on_enter
        bp[x, y].on_exit = on_exit

bp.run()