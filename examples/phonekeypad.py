# This just simulates a phone keypad's layout using ButtonPad.

import buttonpad

if __name__ == "__main__":
    bp = buttonpad.ButtonPad(
        """1,2,3
        4,5,6
        7,8,9
        *,0,#""",
        title="Telephone Keypad Demo",
    )
    bp.run()
