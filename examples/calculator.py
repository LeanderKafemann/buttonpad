# simple_calculator.py
from __future__ import annotations

import ast
import operator as op
from buttonpad import ButtonPad  # adjust import to your package name if needed

# ---------- safe evaluator (supports + - * / // % ** and parentheses) ----------
_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def _safe_eval(expr: str) -> float | int:
    """Evaluate a simple arithmetic expression safely."""
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Num):         # py<3.8
            return node.n
        if isinstance(node, ast.Constant):    # numbers only
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numbers are allowed.")
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED_BINOPS:
                raise ValueError("Operator not allowed.")
            return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in _ALLOWED_UNARYOPS:
                raise ValueError("Operator not allowed.")
            return _ALLOWED_UNARYOPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Expr):
            return _eval(node.value)
        if isinstance(node, ast.Tuple):
            raise ValueError("Invalid expression.")
        if isinstance(node, ast.Call):
            raise ValueError("Function calls are not allowed.")
        if isinstance(node, ast.Name):
            raise ValueError("Names are not allowed.")
        if isinstance(node, ast.Subscript):
            raise ValueError("Subscripts are not allowed.")
        if isinstance(node, ast.Attribute):
            raise ValueError("Attributes are not allowed.")
        raise ValueError("Invalid expression.")
    tree = ast.parse(expr, mode="eval")
    return _eval(tree)

# ---------- ButtonPad layout ----------
# Row 0: wide Entry field spanning all 4 columns.
# Rows 1-5: calculator buttons.
LAYOUT = """
[0],[0],[0],[0]
C,(,),⌫
7,8,9,/
4,5,6,*
1,2,3,-
0,.,=,+
""".strip()

def main() -> None:
    pad = ButtonPad(
        layout=LAYOUT,
        cell_width=70,
        cell_height=[50, 60, 60, 60, 60, 60],  # taller display row
        h_gap=6,
        v_gap=6,
        window_color="white",
        default_bg_color="white",
        default_text_color="#2c2c2c",
        title="ButtonPad Calculator",
        resizable=False,
        border=10,
    )

    # The display is the Entry mapped at the top-left cell (it spans all columns).
    display = pad[0, 0]
    display.background_color = "white"
    display.text_color = "#101010"
    display.font_name = "TkDefaultFont"
    display.font_size = 18
    display.text = ""  # start empty

    # Helpers to read/write the expression:
    def get_expr() -> str:
        return display.text

    def set_expr(s: str) -> None:
        display.text = s

    def append(s: str) -> None:
        set_expr(get_expr() + s)

    # Handlers now receive (element, x, y)
    def do_clear(_el, _x, _y):
        set_expr("")

    def do_backspace(_el, _x, _y):
        s = get_expr()
        if s:
            set_expr(s[:-1])

    def do_equals(_el, _x, _y):
        s = get_expr().strip()
        if not s:
            return
        try:
            result = _safe_eval(s)
            set_expr(str(result))
        except Exception:
            set_expr("Error")

    # Map of button labels to handlers (default = append label)
    SPECIAL = {
        "C": do_clear,
        "⌫": do_backspace,
        "=": do_equals,
    }

    # Style some buttons and wire up click handlers.
    # (x, y): x=0..3, y=1..5 for buttons; the top entry is at (0,0).
    labels = [
        # y=1
        ("C", 0, 1), ("(", 1, 1), (")", 2, 1), ("⌫", 3, 1),
        # y=2
        ("7", 0, 2), ("8", 1, 2), ("9", 2, 2), ("/", 3, 2),
        # y=3
        ("4", 0, 3), ("5", 1, 3), ("6", 2, 3), ("*", 3, 3),
        # y=4
        ("1", 0, 4), ("2", 1, 4), ("3", 2, 4), ("-", 3, 4),
        # y=5
        ("0", 0, 5), (".", 1, 5), ("=", 2, 5), ("+", 3, 5),
    ]

    for label, x, y in labels:
        el = pad[x, y]
        el.font_size = 16

        # light styling
        if label in ("+", "-", "*", "/", "=", "(", ")", "."):
            el.text_color = "#3a3a3a"
        if label == "=":
            el.text_color = "#007acc"
        if label == "C":
            el.text_color = "#7a1f1f"
        if label == "⌫":
            el.text_color = "#444444"

        # click behavior — new signature: (element, x, y)
        if label in SPECIAL:
            handler = SPECIAL[label]
            el.on_click = handler
        else:
            el.on_click = lambda _el, _x, _y, s=label: append(s)

    # Keyboard mappings (keysym -> label)
    key_to_label = {
        # digits
        "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
        "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
        # ops
        "+": "+", "-": "-", "*": "*", "/": "/", ".": ".",
        "parenleft": "(", "parenright": ")",
        # actions
        "Return": "=", "KP_Enter": "=", "equal": "=",  # Enter / keypad enter
        "BackSpace": "⌫", "Escape": "C",
    }

    # Build a lookup from label -> (x, y) for mapping keys
    label_pos = {label: (x, y) for (label, x, y) in labels}

    # Map keys to the associated button positions
    for keysym, label in key_to_label.items():
        if label in label_pos:
            x, y = label_pos[label]
            pad.map_key(keysym, x, y)

    pad.run()


if __name__ == "__main__":
    main()
