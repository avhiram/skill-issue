#!/usr/bin/env python3
"""Verify eJPT public HTML pages correspond to the deployed commit."""
import concurrent.futures
import json
import os
import time
import urllib.parse
import urllib.request
BASE = "https://avhiram.github.io/skill-issue/ejpt/"
REV = os.environ["GITHUB_SHA"]
STAMP = ('<meta name="skill-issue-build" content="' + REV + '">').encode()
def get(path):
    u=BASE+urllib.parse.quote(path,safe="/")+"?v="+REV[:12]
    with urllib.request.urlopen(u,timeout=20) as r:
        return r.read()
def check(path):
    try:
        data=get(path)
        if STAMP not in data:
            return path+" (stale)"
        if path.startswith("original/") and (b"data-ejpt-native" not in data or b"VPDoc" not in data or b"VPNav" not in data):
            return path+" (missing native theme)"
        return None
    except Exception as e:
        return path+" ("+str(e)+")"
deadline=time.monotonic()+660
while True:
    try:
        report=json.loads(get("original/import-report.json"))
        pages=report["pages"]
        if len(pages)!=80 or len(set(pages))!=80:
            raise RuntimeError("expected 80 distinct source pages")
        paths=["index.html","cours.html","cheatsheet.html"]+["original/"+p for p in pages]
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            failures=[e for e in pool.map(check,paths) if e]
        if not failures:
            print("Public eJPT verified: 83 HTML pages at revision "+REV)
            break
        print("Unverified eJPT pages:",len(failures),failures[:8],flush=True)
    except Exception as e:
        print("eJPT public manifest not ready:",e,flush=True)
    if time.monotonic()>=deadline:
        raise SystemExit("Public eJPT not verified")
    time.sleep(20)
