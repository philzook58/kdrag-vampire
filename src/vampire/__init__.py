from pathlib import Path
import sys

vampire_path = str(Path(__file__).with_name("vampire.exe" if sys.platform == "win32" else "vampire"))

__all__ = ["vampire_path"]
