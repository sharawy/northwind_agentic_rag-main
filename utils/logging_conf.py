from __future__ import annotations
import logging, sys

def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s", "%H:%M:%S")
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(level)
    # Avoid dupes
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
