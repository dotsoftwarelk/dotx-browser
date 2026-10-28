"""Entry point for PyInstaller; the source application remains runnable with python -m dotx."""
from dotx.__main__ import main

if __name__ == '__main__':
    raise SystemExit(main())
