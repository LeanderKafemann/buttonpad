# This just simulates a phone keypad's layout using ButtonPad.

import buttonpad

def press1():
    print('1')
    display.text += '1'

def press2():
    print('2')
    display.text += '2'

def press3():
    print('3')
    display.text += '3'

def press4():
    print('4')
    display.text += '4'

def press5():
    print('5')
    display.text += '5'

def press6():
    print('6')
    display.text += '6'

def press7():
    print('7')
    display.text += '7'

def press8():
    print('8')
    display.text += '8'

def press9():
    print('9')
    display.text += '9'

def press0():
    print('0')
    display.text += '0'

def presspound():
    print('#')
    display.text += '#'

def pressstar():
    print('*')
    display.text += '*'

def pressdel():
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
    display: buttonpad.BPTextBox = bp[0,0]
    bp[0, 1].on_click = press1
    bp[1, 1].on_click = press2
    bp[2, 1].on_click = press3
    bp[0, 2].on_click = press4
    bp[1, 2].on_click = press5
    bp[2, 2].on_click = press6
    bp[0, 3].on_click = press7
    bp[1, 3].on_click = press8
    bp[2, 3].on_click = press9
    bp[0, 4].on_click = pressstar
    bp[1, 4].on_click = press0
    bp[2, 4].on_click = presspound
    bp[1, 5].on_click = pressdel

    bp[0,0].text = ''

    bp.run()
