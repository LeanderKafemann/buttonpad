# ButtonPad

`ButtonPad` is a simple Python package that creates a GUI window consisting of a
grid of buttons, labels, or text boxes using only the Python standard library
(`tkinter`). The layout is specified using a string that resembles a CSV format,
where commas separate columns and newlines separate rows.

Cells in the layout string may represent:
- A **button**: any normal word (e.g. `A`, `Click`, `7`)
- A **label**: a cell that begins **and ends** with a matching `'` or `"` (e.g. `"Hello"`)
- An **editable text box**: a cell that begins **and ends** with `_` (e.g. `_Notes_`)
- Blank / empty cells result in an empty label

Adjacent duplicate labels in the layout will merge into a larger button (like
row/column spans in HTML tables).

If `auto_func=True`, the package automatically assigns a callback to a button if
a global function exists whose name matches the button text (spaces removed).
