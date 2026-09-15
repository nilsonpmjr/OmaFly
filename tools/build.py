#!/usr/bin/env python3
"""Build only the tiny native CPU core; no runtime compilation."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
(root / "build").mkdir(exist_ok=True)
subprocess.run(["g++", "-std=c++17", "-O3", "-fPIC", "-shared", "-Wall", "-Wextra",
                str(root / "native/core.cpp"), "-o", str(root / "build/libfruitfly.so")], check=True)
print(root / "build/libfruitfly.so")
