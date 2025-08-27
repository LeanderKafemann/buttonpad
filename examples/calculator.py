from __future__ import annotations
import ast
import operator as op
from buttonpad import ButtonPad, BPButton, BPLabel
import sys

CALC_CFG = """'','','',''
7,8,9,/
4,5,6,*
1,2,3,-
0,.,=,+
C,C,%s,%s
""" % (chr(9003), chr(9003))

# Safe evaluation of simple arithmetic
_ALLOWED_BINOPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv}
_ALLOWED_UNARY = {ast.UAdd: lambda x: x, ast.USub: op.neg}

def _safe_eval(expr: str) -> float:
    node = ast.parse(expr, mode="eval")
    def _eval(n):
        if isinstance(n, ast.Expression): return _eval(n.body)
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(n.op)](_eval(n.operand))
        if sys.version_info.major == 3 and sys.version_info.minor >= 13:
            if isinstance(n, ast.Constant): return n.value
        else:
            if isinstance(n, ast.Num): return n.n  # py<=3.7
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        raise ValueError("Unsupported expression")
    val = _eval(node)
    return float(val)

def make_calculator():
    bp = ButtonPad(
        CALC_CFG,
        title="ButtonPad Calculator",
    )

    # Top display is a merged BPLabel across 4 columns at row 0
    display: BPLabel = bp[0, 0]
    display.background_color = "white"
    display.text_color = "black"
    display.font_name = "TkFixedFont"
    display.font_size = 18
    display.anchor = "e"
    display.text = "0"

    state = {"expr": ""}

    def _update_display():
        display.text = state["expr"] if state["expr"] else "0"

    def _append(ch: str):
        if ch in "+-*/":
            if not state["expr"]:
                if ch != "-": return
                state["expr"] = "-"
            else:
                if state["expr"][-1] in "+-*/":
                    state["expr"] = state["expr"][:-1] + ch
                else:
                    state["expr"] += ch
        elif ch == ".":
            import re
            parts = re.split(r"([+\-*/])", state["expr"])
            if parts and "." in parts[-1]:
                return
            state["expr"] += "."
        else:
            state["expr"] += ch
        _update_display()

    def _backspace():
        if state["expr"]:
            state["expr"] = state["expr"][:-1]
            _update_display()

    def _clear():
        state["expr"] = ""
        _update_display()

    def _equals():
        if not state["expr"]: return
        expr = state["expr"].rstrip("+-*/")
        if not expr: return
        try:
            result = _safe_eval(expr)
            state["expr"] = str(int(result)) if result.is_integer() else (
                str(round(result, 10)).rstrip("0").rstrip(".")
            )
        except Exception:
            state["expr"] = "Error"
        _update_display()

    def bind_button(r: int, c: int):
        try:
            el = bp[r, c]
        except KeyError:
            return
        if not isinstance(el, BPButton):
            return
        cap = el.text
        if cap in {"0","1","2","3","4","5","6","7","8","9",".","+","-","*","/"}:
            el.on_click = (lambda w, ch=cap: _append(ch))
        elif cap == "=":
            el.on_click = lambda w: _equals()
        elif cap == "C":
            el.on_click = lambda w: _clear()
        elif cap == "⌫":
            el.on_click = lambda w: _backspace()
        else:
            el.on_click = lambda w: None
        el.font_name = "TkDefaultFont"
        el.font_size = 14

    lines = [ln for ln in CALC_CFG.strip().splitlines()]
    rows = len(lines)
    cols = max(len(ln.split(",")) for ln in lines)
    for rr in range(rows):
        for cc in range(cols):
            bind_button(rr, cc)

    return bp

if __name__ == "__main__":
    app = make_calculator()
    app.run()
