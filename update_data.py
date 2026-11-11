"""Load a new Seminole County Property Appraiser download into the HomeOwners website.

Easiest: download SeminoleCounty.zip, then double-click update-data.bat.

    python update_data.py                     # finds the newest SeminoleCounty*.zip (project folder or Downloads)
    python update_data.py path\\to\\file.zip
    python update_data.py --no-publish        # build and check only; don't push to GitHub
    python update_data.py --yes               # don't ask before publishing
    python update_data.py --year 2027         # override the tax-roll year shown on the site
    python update_data.py --force             # publish even if the safety check fails

Steps: check the zip -> unzip to SeminoleCounty.new -> build homeowners.db.new -> safety check
-> rebuild docs/data -> swap in the new folder and database -> commit and push docs/data.
If anything fails before the website files are rebuilt, nothing is changed.
"""
import argparse
import glob
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "SeminoleCounty")
NEW_DIR = DATA_DIR + ".new"
DB = os.path.join(HERE, "homeowners.db")
NEW_DB = DB + ".new"
HOMES_JSON = os.path.join(HERE, "docs", "data", "homes.json")
NEEDED = ["Parcels.csv", "AllSales.csv"]       # the only files the build reads
MIN_HOMES = 50_000                              # sanity floor (about 107,000 in 2026)
MAX_DROP = 0.10                                 # stop if homes fall more than 10% from the last build


def say(msg=""):
    print(msg, flush=True)


def stop(msg):
    say()
    say("STOPPED: " + msg)
    say("Nothing on the website was changed.")
    sys.exit(1)


def find_zip(arg):
    if arg:
        if not os.path.isfile(arg):
            stop(f"There is no file at {arg}")
        return os.path.abspath(arg)
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    found = []
    for folder in (HERE, downloads):
        found += glob.glob(os.path.join(folder, "SeminoleCounty*.zip"))
    if not found:
        stop("Could not find SeminoleCounty.zip in the project folder or your Downloads folder.\n"
             "Download it from https://files.scpafl.org/data/cama/SeminoleCounty.zip and run this again.")
    return max(found, key=os.path.getmtime)


def unzip(path):
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        stop(f"{path} is not a valid zip file (the download may be incomplete). Download it again.")
    with z:
        by_name = {os.path.basename(i.filename).lower(): i for i in z.infolist() if not i.is_dir()}
        missing = [n for n in NEEDED if n.lower() not in by_name]
        if missing:
            stop(f"The zip is missing {', '.join(missing)}. Is this the Seminole County parcel data download?")
        info = by_name["parcels.csv"]
        as_of = "%04d-%02d-%02d" % info.date_time[:3]
        if os.path.exists(NEW_DIR):
            shutil.rmtree(NEW_DIR)
        os.makedirs(NEW_DIR)
        for name, i in by_name.items():
            if not name.endswith(".csv"):
                continue
            say(f"  unzipping {os.path.basename(i.filename)} ({i.file_size / 1e6:,.0f} MB)")
            try:
                with z.open(i) as src, open(os.path.join(NEW_DIR, os.path.basename(i.filename)), "wb") as dst:
                    shutil.copyfileobj(src, dst, 1 << 20)
            except (zipfile.BadZipFile, OSError, EOFError) as e:
                stop(f"Could not unzip {i.filename}: {e}. The download may be damaged; download it again.")
    with open(os.path.join(NEW_DIR, "_source.json"), "w", encoding="utf-8") as f:
        json.dump({"zip": os.path.basename(path), "asOf": as_of, "loaded": time.strftime("%Y-%m-%d %H:%M")}, f)
    return as_of


def run(args, what):
    r = subprocess.run([sys.executable] + args, cwd=HERE)
    if r.returncode != 0:
        stop(f"{what} failed (see the messages above).")


def previous_build():
    try:
        with open(HOMES_JSON, encoding="utf-8") as f:
            d = json.load(f)
        return d, {r[0]: r[1] for r in d["rows"]}
    except (OSError, ValueError, KeyError):
        return None, {}


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=HERE, capture_output=True, text=True)
    if check and r.returncode != 0:
        say(r.stdout + r.stderr)
        raise RuntimeError("git " + " ".join(args) + " failed")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", nargs="?")
    ap.add_argument("--year", type=int)
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    path = find_zip(a.zip)
    say(f"1/5  Checking and unzipping {path}")
    as_of = unzip(path)
    say(f"     County export date: {as_of}")

    say("2/5  Building the database (about a minute)")
    if os.path.exists(NEW_DB):
        os.remove(NEW_DB)
    run(["build_db.py", NEW_DIR, "--db", NEW_DB], "Building the database")

    say("3/5  Safety check")
    db = sqlite3.connect(NEW_DB)
    homes = db.execute("SELECT COUNT(*) FROM parcels WHERE homestead = 1 AND lat IS NOT NULL").fetchone()[0]
    sales = db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    db.close()
    old, old_owner = previous_build()
    old_n = len(old_owner)
    say(f"     Owner-occupied homes: {homes:,}" + (f" (last build: {old_n:,}, data as of {old.get('dataAsOf') or old.get('built')})" if old else ""))
    say(f"     Sales records: {sales:,}")
    problems = []
    if homes < MIN_HOMES:
        problems.append(f"only {homes:,} homes (expected more than {MIN_HOMES:,})")
    if old_n and homes < old_n * (1 - MAX_DROP):
        problems.append(f"homes dropped from {old_n:,} to {homes:,} (more than {MAX_DROP:.0%})")
    if sales == 0:
        problems.append("no sales records")
    if problems:
        if not a.force:
            os.remove(NEW_DB)
            shutil.rmtree(NEW_DIR, ignore_errors=True)
            stop("The new data looks wrong: " + "; ".join(problems) + ".\n"
                 "If you're sure it's right, run: python update_data.py --force")
        say("     Continuing anyway (--force): " + "; ".join(problems))

    say("4/5  Rebuilding the website data")
    shutil.rmtree(DATA_DIR + ".old", ignore_errors=True)
    if os.path.exists(DATA_DIR):
        os.replace(DATA_DIR, DATA_DIR + ".old")
    os.replace(NEW_DIR, DATA_DIR)
    os.replace(NEW_DB, DB)
    shutil.rmtree(DATA_DIR + ".old", ignore_errors=True)
    run(["build_site.py", "--db", DB, "--as-of", as_of] + (["--year", str(a.year)] if a.year else []),
        "Rebuilding the website data")

    new, new_owner = previous_build()
    added = sum(1 for p in new_owner if p not in old_owner)
    gone = sum(1 for p in old_owner if p not in new_owner)
    changed = sum(1 for p, o in new_owner.items() if p in old_owner and old_owner[p] != o)
    if old:
        say(f"     Changes since the last build: {added:,} homes added, {gone:,} removed, {changed:,} with a new owner name")

    if a.no_publish:
        say(f"\nDone in {time.time() - t0:.0f}s. Not published (--no-publish).")
        return
    say("5/5  Publishing to the website")
    git("add", "-A", "docs/data")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        say("     The website already has exactly this data. Nothing to publish.")
        return
    if not a.yes:
        ans = input("     Publish this data to the website now? [Y/n] ").strip().lower()
        if ans not in ("", "y", "yes"):
            say("     Not published. The new data is built locally; run this again to publish.")
            return
    try:
        git("commit", "-m", f"Update data: county export of {as_of} ({homes:,} homes)", "--", "docs/data")
        say("     Uploading (about 6 MB)...")
        git("push")
    except RuntimeError as e:
        say(f"\nPublishing failed: {e}. The data is committed locally; run 'git push' in this folder to retry.")
        sys.exit(1)
    say(f"\nDone in {time.time() - t0:.0f}s. The website and the Android app show the new data in a minute or two.")


if __name__ == "__main__":
    main()
