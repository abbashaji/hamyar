#!/usr/bin/env python3
"""Concatenate spec/*.md (sorted by filename) into 'Hamyar — Product Specification.md'."""
import glob, sys
parts = sorted(p for p in glob.glob("spec/*.md") if not p.endswith("00-conventions.md") or "--with-conventions" in sys.argv)
out = "\n\n---\n\n".join(open(p, encoding="utf-8").read().strip() for p in parts)
open("Hamyar — Product Specification.md", "w", encoding="utf-8").write(out + "\n")
print("assembled", len(parts), "parts")
