#!/usr/bin/env python3
"""Проверка места на диске. Нужен пакет python3-psutil."""
import shutil

import psutil


def main():
    usage = shutil.disk_usage("/")
    memory = psutil.virtual_memory()
    print("disk_report.py")
    print("psutil", psutil.__version__)
    print(f"path / total_bytes {usage.total}")
    print(f"path / used_bytes {usage.used}")
    print(f"path / free_bytes {usage.free}")
    print(f"path / free_gib {usage.free / 1024 ** 3:.2f}")
    print(f"memory_total_bytes {memory.total}")
    print(f"memory_available_bytes {memory.available}")
    if usage.free < 500 * 1024 * 1024:
        print("RESULT low_space")
    else:
        print("RESULT space_ok")


if __name__ == "__main__":
    main()
