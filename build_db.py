"""Build homeowners.db (SQLite) from the county CSV exports.

Usage:
    python build_db.py                               # SeminoleCounty\\*.csv -> homeowners.db
    python build_db.py path\\to\\CountyFolder
    python build_db.py path\\to\\CountyFolder --db other.db

Normally run for you by update_data.py. The database is rebuilt from scratch each time.
"""
import csv
import os
import re
import sqlite3
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
_args = [a for a in sys.argv[1:]]
DB_PATH = os.path.join(HERE, "homeowners.db")
if "--db" in _args:
    _i = _args.index("--db")
    DB_PATH = os.path.abspath(_args[_i + 1])
    del _args[_i:_i + 2]
DATA_DIR = _args[0] if _args else os.path.join(HERE, "SeminoleCounty")

# Site-address cities seen in Seminole County data. Longest names first so
# "ALTAMONTE SPRINGS" wins over a shorter partial match.
CITIES = sorted([
    "ALTAMONTE SPRINGS", "APOPKA", "CASSELBERRY", "CHULUOTA", "DEBARY", "DELTONA",
    "FERN PARK", "GENEVA", "GOLDENROD", "HEATHROW", "LAKE MARY", "LAKE MONROE",
    "LONGWOOD", "MAITLAND", "MIDWAY", "ORLANDO", "OSTEEN", "OVIEDO", "SANFORD",
    "WINTER PARK", "WINTER SPRINGS",
], key=len, reverse=True)

ADDR_RE = re.compile(r"^(.*?)\s+FL\s+(\d{5})(?:-\d{4})?\s*$")


def split_site_address(addr):
    """'619 CRICKLEWOOD TER LAKE MARY FL 32746' -> ('619 CRICKLEWOOD TER', 'LAKE MARY', '32746')."""
    addr = " ".join((addr or "").split())
    m = ADDR_RE.match(addr)
    if not m:
        return addr, None, None
    head, zip5 = m.group(1), m.group(2)
    for city in CITIES:
        if head == city or head.endswith(" " + city):
            return head[: -len(city)].strip(), city, zip5
    return head, None, zip5


def norm(s):
    return " ".join((s or "").upper().replace(",", " ").split())


def num(v, cast=float):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return cast(float(v))
    except ValueError:
        return None


def iso_date(v):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return datetime.strptime(v.split(" ")[0], "%m/%d/%Y").date().isoformat()
    except ValueError:
        return None


def boolean(v):
    return 1 if (v or "").strip().lower() == "true" else 0


def read_csv(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)


def main():
    t0 = time.time()
    tmp = DB_PATH + ".building"
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.executescript("""
        PRAGMA journal_mode = OFF;
        PRAGMA synchronous = OFF;
        CREATE TABLE parcels (
            id INTEGER PRIMARY KEY,
            parcel TEXT, parcel_fmt TEXT, owner TEXT,
            site_address TEXT, street TEXT, city TEXT, zip TEXT,
            mailing_address TEXT, mail_matches_site INTEGER,
            property_type TEXT, dor_code TEXT, subdivision TEXT,
            homestead INTEGER, vacant TEXT,
            year_built INTEGER, living_area INTEGER, bedrooms INTEGER, bathrooms REAL,
            pool INTEGER, fireplace INTEGER, acres REAL,
            just_value INTEGER, assessed_value INTEGER, taxable_value INTEGER,
            last_sale_date TEXT, last_sale_year INTEGER, last_sale_amount INTEGER,
            lat REAL, lon REAL
        );
        CREATE TABLE sales (
            parcel TEXT, sale_date TEXT, amount INTEGER, deed TEXT,
            qualification TEXT, vacant_improved TEXT, book TEXT, page TEXT
        );
    """)

    # --- parcels
    rows = []
    unmatched_city = 0
    for r in read_csv("Parcels.csv"):
        street, city, zip5 = split_site_address(r["PrimaryAddress"])
        if city is None and r["PrimaryAddress"].strip():
            unmatched_city += 1
        mailing = r["MailingAddress"]
        mail_match = 1 if street and norm(mailing).startswith(norm(street) + " ") else 0
        rows.append((
            r["Parcel"], r["ParcelFormat"], r["OwnerName"].strip(),
            " ".join(r["PrimaryAddress"].split()), street, city, zip5,
            " ".join(mailing.split()), mail_match,
            r["PrimaryPropertyType"], r["DORCode"], r["Subdivision"].strip(),
            boolean(r["HasHomestead"]), r["VacantImproved"],
            num(r["YearBuilt"], int), num(r["TotalLivingArea"], int),
            num(r["TotalBedrooms"], int), num(r["TotalBathrooms"]),
            boolean(r["Pool"]), boolean(r["Fireplace"]),
            num(r["SUM_LegalAcres"]) or num(r["SUM_GISAcres"]),
            num(r["TotalJustValue"], int), num(r["AssessedValue"], int), num(r["TaxableValue"], int),
            iso_date(r["LastSaleDate"]), num(r["LastSaleYear"], int), None,
            num(r["Latitude"]), num(r["Longitude"]),
        ))
    db.executemany(f"INSERT INTO parcels VALUES (NULL{',?' * 29})", rows)
    print(f"parcels: {len(rows):,} rows ({unmatched_city:,} site addresses with no recognised city)")

    # --- sales history
    sales = []
    for r in read_csv("AllSales.csv"):
        sales.append((
            r["Parcel"], iso_date(r["SaleDate"]), num(r["SaleAmt"], int), r["DeedDescription"].strip(),
            r["QualificationDescription"].strip(), r["VacImp"], r["PlatBook"], r["PlatPage"],
        ))
    db.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?)", sales)
    print(f"sales: {len(sales):,} rows")

    db.executescript("""
        CREATE INDEX sales_parcel ON sales(parcel, sale_date);
        -- last sale amount = amount on the parcel's most recent sale record
        UPDATE parcels SET last_sale_amount = (
            SELECT s.amount FROM sales s WHERE s.parcel = parcels.parcel
            ORDER BY s.sale_date DESC, s.amount DESC LIMIT 1);
        CREATE INDEX p_homestead ON parcels(homestead);
        CREATE INDEX p_city ON parcels(city);
        CREATE INDEX p_zip ON parcels(zip);
        CREATE INDEX p_dor ON parcels(dor_code);
        CREATE INDEX p_latlon ON parcels(lat, lon);
        CREATE INDEX p_parcel ON parcels(parcel);
        ANALYZE;
    """)
    db.commit()
    db.close()
    os.replace(tmp, DB_PATH)
    print(f"wrote {DB_PATH} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
