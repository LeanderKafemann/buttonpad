# This just simulates a phone keypad's layout using ButtonPad.

import buttonpad

def press_label(widget, x, y):
    print(widget.text)
    display.text += widget.text
    bp.status_bar = f"Pressed {widget.text}"

def press_del(widget, x, y):
    display.text = display.text[:-1]

if __name__ == "__main__":
    bp = buttonpad.ButtonPad(
        """
        [Display], [Display], [Display]
        1,2,3
        4,5,6
        7,8,9
        *,0,#
        '',%s,''""" % (chr(9003)),
        title="Telephone Keypad Demo",
        cell_width=70,
        cell_height=100,
        h_gap=20,
        v_gap=10,
        border=40,
        default_bg_color='#ff4444',
        default_text_color='darkblue',
        window_color='green',
    )
    bp.status_bar = ''
    display: buttonpad.BPTextBox = bp[0,0]
    for x in range(3):
        for y in range(1, 5):
            bp[x,y].on_click = press_label
    bp[1, 5].on_click = press_del

    bp[0,0].text = ''

    bp.run()
