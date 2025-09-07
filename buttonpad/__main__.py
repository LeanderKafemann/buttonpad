"""Module entry point for `python -m buttonpad`.

Runs the bundled launcher (grid of demo apps). If the launcher import fails
for any reason we fall back to a simple message to avoid a hard stack trace.
"""

from __future__ import annotations

def main() -> None:  # small shim so other tools can call buttonpad.__main__.main()
	try:
		from . import launcher  # noqa: F401  (side-effect: creates and runs the UI)
		launcher.main()
	except Exception as e:  # pragma: no cover - defensive
		try:
			print("Unable to start ButtonPad launcher:", e)
		except Exception:
			pass


if __name__ == "__main__":  # executed via `python -m buttonpad`
	main()

