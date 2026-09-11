#!/usr/bin/env python3
"""Mirror the archived Shipman Inquiry site from the Wayback Machine.

Usage: fetch.py <list-file> <out-dir> [workers]
List file lines: "<wayback-timestamp> <original-url>".
Polite: few workers, long backoff — archive.org drops connections when pushed.
"""
import os, re, sys, time, random, hashlib, threading
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (public-records research; shipman-inquiry mirror)"}
LOCK = threading.Lock()
STATS = {}

def slug(url):
    p = url.split("org.uk", 1)[1].lstrip("/").replace(":80/", "")
    p = re.sub(r"[^A-Za-z0-9._=-]+", "_", p) or "index"
    return p[:110] + "_" + hashlib.md5(url.encode()).hexdigest()[:8] + ".html"

def bump(k):
    with LOCK:
        STATS[k] = STATS.get(k, 0) + 1

def fetch(job, outdir, tries=5):
    ts, url = job
    dest = os.path.join(outdir, slug(url))
    if os.path.exists(dest) and os.path.getsize(dest) > 500:
        bump("skip"); return
    wb = f"https://web.archive.org/web/{ts}id_/{url}"
    for i in range(tries):
        try:
            req = urllib.request.Request(wb, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as f:
                body = f.read()
            if len(body) < 300:
                bump("tiny"); return
            with open(dest, "wb") as fh:
                fh.write(body)
            bump("ok"); return
        except Exception:
            time.sleep(min(60, 5 * 2 ** i) + random.uniform(0, 3))
    bump("fail")

def main():
    listfile, outdir = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    jobs = [tuple(l.split()[:2]) for l in open(listfile) if len(l.split()) >= 2]
    os.makedirs(outdir, exist_ok=True)
    print(f"{len(jobs)} urls -> {outdir} ({workers} workers)", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(fetch, j, outdir) for j in jobs]
        for n, _ in enumerate(futs, 1):
            _.result()
            if n % 50 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)} {STATS} {time.time()-t0:.0f}s", flush=True)
    print("DONE", outdir, STATS, flush=True)

if __name__ == "__main__":
    main()
