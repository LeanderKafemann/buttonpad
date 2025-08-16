# ButtonPad

ButtonPad is a tkinter-based grid of buttons and text fields using only the Python standard library.

## Text Fields

Any label beginning with `_` becomes a text field (`TextField`). These can span multiple cells just like buttons.

```python
labels = """_Name, _Name, _, 3
_Name, _Name, _, 6
7, 8, 9
*, 0, #"""
pad = ButtonPad(labels)
```

## Access

- `pad.buttons` → list of `Button` objects
- `pad.fields` → list of `TextField` objects

Each TextField has:
- `.text` (get/set)
- `.fg`, `.bg` (colors)
- `.font` (family/size tuple)

## License

MIT
