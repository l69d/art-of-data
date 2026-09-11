#!/usr/bin/env python3
"""Flatten the mirrored Fourth/Fifth/Sixth Report pages into readable text.

The site served each report under two URL schemes: ?ch=N&pa=M returns the whole
of chapter N (identical for every pa), while ?ID=n returns one section. So the
chapter pages are taken once each, and a section page is kept only if its text
is not already inside a chapter we have.

Writes derived/report_text/<report>.txt and derived/report_sections.csv.
"""
import re, os, csv, glob, html, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "derived")
TXT = os.path.join(OUT, "report_text")
os.makedirs(TXT, exist_ok=True)

REPORTS = {"4r": "fourth_report", "5r": "fifth_report", "6r": "sixth_report"}
DROP = re.compile(r"^(Print [Vv]ersion|Reports|Published by The Shipman Inquiry|"
                  r"© Crown Copyright.*|Previous|Next|Back to .*|Home|>)$")


def lines_of(path):
    b = open(path, "rb").read()
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        t = b.decode("cp1252", errors="replace")
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", "\n", t)
    t = html.unescape(t).replace("\xa0", " ").replace("�", " ")
    out = []
    for l in (re.sub(r"\s+", " ", x).strip() for x in t.split("\n")):
        if not l:
            continue
        if l in ("st", "nd", "rd", "th") and out and out[-1][-1:].isdigit():
            out[-1] += l          # <sup>th</sup> split "12" and "th" onto separate lines
        else:
            out.append(l)
    return out


def parse(path):
    L = lines_of(path)
    m = re.match(r"The Shipman Inquiry - (?:The )?(\w+) Report - (.*)", L[0] if L else "")
    section = m.group(2) if m else ""
    crumb = max((i for i, l in enumerate(L[:40]) if l == ">"), default=-1)
    body = L[crumb + 2:] if crumb >= 0 else L[1:]
    chapter = next((l for l in L[:max(crumb, 0)]
                    if re.match(r"(?i)^(chapter|appendix|annex|part)\b", l)), "")
    body = [l for l in body if not DROP.match(l)]
    while body and re.match(r"(?i)^(published by|crown copyright)", body[-1]):
        body.pop()
    return chapter, section, body


def key_of(f):
    """Sort key + scheme: chapter pages first, in chapter order; then section pages by id."""
    if (m := re.search(r"ch=(\d+)", f)):
        return ("ch", int(m.group(1)), 0)
    if (m := re.search(r"(?i)id=(\d+)", f)):
        return ("id", int(m.group(1)), 0)
    return ("id", 0, 0)


def main():
    rows = []
    for prefix, name in REPORTS.items():
        files = sorted(set(glob.glob(f"{ROOT}/raw/reports/{prefix}*page.asp*")), key=key_of)
        chapters, sections, seen = [], [], set()

        for f in files:
            chapter, section, body = parse(f)
            if not body:
                continue
            sig = hash("\n".join(body))
            if sig in seen:                      # same chapter under a different ?pa=
                continue
            seen.add(sig)
            (chapters if key_of(f)[0] == "ch" else sections).append(
                (chapter, section, body, os.path.basename(f)))

        # Chapter and section views overlap heavily, so emit each paragraph once,
        # in first-seen order: chapter pages lay down the spine, section pages fill gaps.
        written, kept = set(), 0
        with open(os.path.join(TXT, name + ".txt"), "w") as fh:
            last = None
            for chapter, section, body, src in chapters + sections:
                fresh = [l for l in body if l not in written]
                if not fresh:
                    continue
                written.update(fresh)
                kept += 1
                if chapter and chapter != last:
                    fh.write(f"\n\n{'=' * 72}\n{chapter}\n{'=' * 72}\n")
                    last = chapter
                fh.write(f"\n--- {section} ---\n" + "\n".join(fresh) + "\n")
                rows.append({"report": name, "chapter": chapter, "section": section,
                             "words": sum(len(l.split()) for l in fresh), "source_file": src})
        kb = os.path.getsize(os.path.join(TXT, name + ".txt")) // 1024
        print(f"{name}.txt  {kept} sections with new text  {kb} KB")

    with open(os.path.join(OUT, "report_sections.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, ["report", "chapter", "section", "words", "source_file"])
        w.writeheader(); w.writerows(rows)
    print("report_sections.csv", len(rows), "rows")


if __name__ == "__main__":
    main()
