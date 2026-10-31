#!/usr/bin/env python3
"""Основной скрипт проверки локализации игры «Алтын Жол»."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from soz.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
