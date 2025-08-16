# ButtonPad

ButtonPad is a tkinter-based grid of buttons and multiline text fields using only the Python standard library.

## Text Fields

Any label beginning with `_` becomes a **scrollable, multiline text field**.  
Fields can span cells like buttons.

```python
labels = """_Notes, _Notes, 3
_Notes, _Notes, 6
7, 8, 9
*, 0, #"""
```

## Access

- `pad.buttons` → list of `Button` objects
- `pad.fields` → list of `TextField` objects

Each `TextField` supports:
- `.text` (get/set)
- `.fg`, `.bg`
- `.font` (tuple)
- `.wrap` (property: "word", "char", or "none")

## License

MIT
