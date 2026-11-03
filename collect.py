"""Collect business listings from Open Brewery DB's published directory export."""
import argparse
import csv
import io
import json
from pathlib import Path
from urllib.request import urlopen

SOURCE = "https://raw.githubusercontent.com/openbrewerydb/openbrewerydb/master/breweries.csv"
OUTPUT = Path(__file__).parent / "data" / "directory.json"


def collect(stream, limit):
    listings = {}
    for row in csv.DictReader(stream):
        name, category, city, street = (
            row[key].strip() for key in ("name", "brewery_type", "city", "address_1")
        )
        if not all((name, category, city, street)) or category in {"closed", "planning"}:
            continue
        address = ", ".join(value.strip() for value in (
            street, row["address_2"], row["address_3"], city, row["state_province"],
            row["postal_code"], row["country"]
        ) if value.strip())
        phone = row["phone"].strip() or None
        if any(len(v) > n for v,n in ((name,200),(category,100),(city,100),(address,500),(phone or "",60))):
            continue
        identity = (name.casefold(), city.casefold(), address.casefold())
        listings.setdefault(identity, dict(business_name=name, category=category, city=city,
                                           address=address, phone=phone, source="Open Brewery DB"))
        if len(listings) == limit:
            return list(listings.values())
    raise ValueError(f"Only {len(listings)} qualifying listings found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="Use a downloaded directory CSV")
    args = parser.parse_args()
    stream = (args.csv.open(encoding="utf-8-sig", newline="") if args.csv else
              io.TextIOWrapper(urlopen(SOURCE, timeout=45), encoding="utf-8-sig", newline=""))
    with stream:
        records = collect(stream, 550)
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} directory listings to {OUTPUT}")
