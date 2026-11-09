# HomeOwners

A map of owner-occupied homes in Seminole County, FL: every parcel with a homestead exemption,
which in Florida means the owner lives there as their permanent residence. Filter by city, ZIP,
property type, value, size, sale history and more; tap a home for owner and sales details; export
results to CSV. Works on PC and phone, with a "find me" location button.

The site is static: `docs/` is served by GitHub Pages, and the browser does all the filtering.

## Update the data (e.g. next year's roll)

1. Drop the new Property Appraiser CSV export into `SeminoleCounty\` (the folder is not committed).
2. Rebuild and publish:

```
python build_db.py      # CSVs -> homeowners.db (~30s)
python build_site.py    # homeowners.db -> docs/data/*.json
git add docs && git commit -m "Update data" && git push
```

Also change `dataYear` in `build_site.py` if the year changed.

## Preview locally

```
python -m http.server 8770 --directory docs
```

Then open http://localhost:8770 (location works on localhost too).

## Notes

- Only homesteaded parcels are published (about 107,500).
- "Tax bill mailed to the home itself" is a second owner-occupancy signal: the mailing address matches the property.
- Sales history comes from `AllSales.csv` and includes non-market transfers (e.g. $100 quit-claim deeds)
  and multi-parcel sales. "Last sale price" is the amount on the most recent record.
- Map tiles: OpenStreetMap.
