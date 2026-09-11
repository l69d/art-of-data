#!/usr/bin/env python3
"""Extract plain text from the downloaded PDFs into derived/doc_text/."""
import os, glob, sys
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "derived", "doc_text")
os.makedirs(OUT, exist_ok=True)

for f in sorted(glob.glob(os.path.join(ROOT, "docs", "*.pdf"))):
    dest = os.path.join(OUT, os.path.basename(f)[:-4] + ".txt")
    if os.path.exists(dest):
        continue
    try:
        r = PdfReader(f)
        with open(dest, "w") as fh:
            for i, p in enumerate(r.pages):
                fh.write(f"\n\n=== [page {i+1}] ===\n")
                fh.write(p.extract_text() or "")
        print(os.path.basename(dest), len(r.pages), "pages", os.path.getsize(dest) // 1024, "KB")
    except Exception as e:
        print("ERR", f, e)
