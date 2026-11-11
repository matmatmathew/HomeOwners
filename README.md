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

## Android app

`android-app/` is a Capacitor 7 app that loads the live site and adds native features through
`HomeOwnersPlugin.java`: Android's contact picker, a linked contact's text messages (READ_SMS),
share/save files, text shared in from other apps, and keep-screen-on. The site detects the app
(`NATIVE` in `docs/index.html`) and uses those features; on the web they stay off.

The installable file is `docs/app/HomeOwners.apk` (linked from the site on Android phones).
Website changes reach the app automatically; rebuild the APK only after changing `android-app/`:

```
cd android-app && npx cap sync android
cd android && set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr && gradlew assembleDebug
copy app\build\outputs\apk\debug\app-debug.apk ..\..\docs\app\HomeOwners.apk
```

On the SCPS network the build needs `android-app/.build-certs/truststore.jks` (Java's trust list plus the
school firewall certificate; see `android/gradle.properties`). On other networks remove those two lines.
