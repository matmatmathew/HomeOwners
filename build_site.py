"""Export homeowners.db into the static website in docs/ (served by GitHub Pages).

Usage (normally run for you by update_data.py):
    python build_site.py                         # homeowners.db -> docs/data/*.json
    python build_site.py --db other.db --year 2027 --as-of 2027-01-15

--as-of  date of the county's export (shown on the site as "Data as of ...").
         Default: read from SeminoleCounty/_source.json (written by update_data.py),
         otherwise the date of SeminoleCounty/Parcels.csv.
--year   tax-roll year shown on the site. Default: the year of --as-of.

Only homesteaded (owner-occupied) parcels are published.
"""
import argparse
import json
import os
import shutil
import sqlite3
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "homeowners.db")
DATA_DIR = os.path.join(HERE, "SeminoleCounty")
OUT = os.path.join(HERE, "docs", "data")
SALES_BUCKETS = 64


def bucket(parcel):
    """Must match bucketOf() in docs/index.html."""
    h = 0
    for ch in parcel:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % SALES_BUCKETS


def data_date():
    """Date of the county export: from _source.json, else from Parcels.csv's file date."""
    try:
        with open(os.path.join(DATA_DIR, "_source.json"), encoding="utf-8") as f:
            return json.load(f)["asOf"]
    except (OSError, ValueError, KeyError):
        pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(os.path.join(DATA_DIR, "Parcels.csv"))).date().isoformat()
    except OSError:
        return date.today().isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DB_PATH)
    ap.add_argument("--year", type=int)
    ap.add_argument("--as-of", dest="as_of")
    a = ap.parse_args()
    as_of = a.as_of or data_date()
    year = a.year or int(as_of[:4])
    db = sqlite3.connect(a.db)
    rows = db.execute("""
        SELECT parcel, owner, street, city, zip, dor_code, subdivision,
               year_built, living_area, bedrooms, bathrooms, pool,
               just_value,
               last_sale_date, last_sale_amount, mail_matches_site, mailing_address, lat, lon
        FROM parcels WHERE homestead = 1 AND lat IS NOT NULL
        ORDER BY just_value DESC""").fetchall()

    cities, dors, subs = {}, {}, {}

    def idx(table, v):
        v = v or ""
        if v not in table:
            table[v] = len(table)
        return table[v]

    out_rows = []
    for (parcel, owner, street, city, zip5, dor, sub, yb, sqft, bd, ba, pool,
         jv, lsd, lsa, mail_match, mailing, lat, lon) in rows:
        out_rows.append([
            parcel, owner, street, idx(cities, city), zip5 or "", idx(dors, dor), idx(subs, sub),
            yb, sqft, bd, ba, pool, jv, lsd or "", lsa,
            "" if mail_match else mailing, round(lat, 5), round(lon, 5),
        ])

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "sales"))

    homes = {
        "county": "Seminole County, FL",
        "dataYear": year,
        "dataAsOf": as_of,
        "built": date.today().isoformat(),
        "cols": ["parcel", "owner", "street", "city", "zip", "dor", "sub",
                 "yearBuilt", "sqft", "beds", "baths", "pool", "value",
                 "lastSaleDate", "lastSaleAmt", "mailingIfDifferent", "lat", "lon"],
        "cities": list(cities), "dors": list(dors), "subs": list(subs),
        "rows": out_rows,
    }
    with open(os.path.join(OUT, "homes.json"), "w", encoding="utf-8") as f:
        json.dump(homes, f, separators=(",", ":"), ensure_ascii=False)

    # sales history, split into buckets so a popup loads only a small file
    parcels = {r[0] for r in rows}
    buckets = [dict() for _ in range(SALES_BUCKETS)]
    n = 0
    for parcel, d, amt, deed, qual in db.execute(
            "SELECT parcel, sale_date, amount, deed, qualification FROM sales ORDER BY parcel, sale_date DESC"):
        if parcel in parcels:
            buckets[bucket(parcel)].setdefault(parcel, []).append([d or "", amt, deed, qual])
            n += 1
    for i, b in enumerate(buckets):
        with open(os.path.join(OUT, "sales", f"{i}.json"), "w", encoding="utf-8") as f:
            json.dump(b, f, separators=(",", ":"), ensure_ascii=False)

    size = os.path.getsize(os.path.join(OUT, "homes.json")) / 1e6
    print(f"data as of {as_of} ({year} tax roll)")
    print(f"homes.json: {len(out_rows):,} homes, {size:.1f} MB; sales: {n:,} records in {SALES_BUCKETS} files")


if __name__ == "__main__":
    main()
