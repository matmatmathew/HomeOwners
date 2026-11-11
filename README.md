# HomeOwners

A map of owner-occupied homes in Seminole County, FL: every parcel with a homestead exemption.
In Florida that means the owner lives there as their permanent residence. You can filter the homes, see
owner and sales details, export CSV, and keep private notes, voice notes, photos and linked contacts for any home.
It works on PC and phone, with live location, and comes as an Android app.

- **Live site:** https://matmatmathew.github.io/HomeOwners/
- **Android app:** https://matmatmathew.github.io/HomeOwners/app/HomeOwners.apk
- **How to use it:** [GUIDE.md](GUIDE.md)
- **Repository:** https://github.com/matmatmathew/HomeOwners (public). GitHub Pages serves the `docs/` folder on `main`.

---

## Contents

1. [Update the county data](#update-the-county-data)
2. [How it works](#how-it-works)
3. [Project files](#project-files)
4. [The data pipeline](#the-data-pipeline)
5. [The website (`docs/index.html`)](#the-website-docsindexhtml)
6. [Notes storage and backups](#notes-storage-and-backups)
7. [The Android app](#the-android-app)
8. [Publishing and Git](#publishing-and-git)
9. [Troubleshooting](#troubleshooting)

---

## Update the county data

The Property Appraiser publishes a new download every day:
**Current Year Seminole County Parcel Data**, https://files.scpafl.org/data/cama/SeminoleCounty.zip (about 96 MB).
Updating every week or month is plenty.

1. Download `SeminoleCounty.zip`. Leave it in **Downloads**, or put it in this project folder.
2. Double-click **`update-data.bat`**. You can also drag a zip onto it.
3. Read the summary. Answer **Y** to publish.

The website and the Android app show the new data a minute or two later. **The APK does not need rebuilding.**
The app loads the live site.

What `update_data.py` does:

| Step | What happens |
|---|---|
| 1. Check and unzip | Finds the newest `SeminoleCounty*.zip` (from the command line, this folder, or Downloads). Checks that it's a valid zip containing `Parcels.csv` and `AllSales.csv`. Unzips to `SeminoleCounty.new\` and records the export date from inside the zip (`_source.json`). |
| 2. Build | Runs `build_db.py` into `homeowners.db.new`. Takes about 35 seconds. |
| 3. Safety check | Stops if there are fewer than 50,000 homes, if homes dropped more than 10% since the last build, or if there are no sales. Before this point **nothing is changed**. |
| 4. Rebuild site data | Swaps in the new folder and database, then runs `build_site.py` to rewrite `docs/data/`. Prints how many homes were added, removed, or changed owner. |
| 5. Publish | Asks first, then commits `docs/data` ("Update data: county export of …") and pushes. Skipped if the data is identical. |

Options: `python update_data.py [zip] [--no-publish] [--yes] [--year 2027] [--force]`

- `--no-publish` builds and checks, but doesn't commit or push. Preview it with [Preview locally](#preview-locally).
- `--yes` publishes without asking.
- `--year` overrides the tax-roll year shown on the site. The default is the year of the county's export date.
  If the county keeps publishing the previous year's roll into January, run with `--year` (for example `--year 2026`).
- `--force` publishes even when the safety check fails, for example after a real, large change in the county data.

Each update adds about 6 MB to the repository history. Monthly updates are fine for years. Daily updates would bloat it.

**Your notes survive updates.** Notes, photos, voice notes and contacts are stored on each device, keyed by
parcel number, and parcel numbers don't change. A home that loses its homestead exemption leaves the map, but its notes
stay on the device and in backups.

If the county ever renames columns in `Parcels.csv` or `AllSales.csv`, `build_db.py` stops with a `KeyError`
naming the column. Update the name in `build_db.py`.

### Preview locally

```
python -m http.server 8770 --directory docs
```

Open http://localhost:8770 in a browser. Location works on localhost too.

---

## How it works

```
SeminoleCounty.zip ──update_data.py──► SeminoleCounty\*.csv ──build_db.py──► homeowners.db (SQLite)
                                                                                   │
                                                                          build_site.py
                                                                                   ▼
                     GitHub Pages ◄──git push── docs\  (index.html + data\homes.json + data\sales\*.json)
                          │
         ┌────────────────┴────────────────┐
   any browser (PC / phone)        Android app (loads the same live site
                                    and adds native features)
```

- The site is **fully static**. The browser downloads all the homes once (17 MB, about 5.6 MB compressed) and does
  every filter and search itself, with no server.
- **Notes never leave the device** unless the user shares a backup file.
- The Android app is a thin native shell around the live website, so site changes reach the app without a reinstall.

---

## Project files

| Path | What it is | In Git? |
|---|---|---|
| `update-data.bat` | Double-click to load a new county download. | yes |
| `update_data.py` | The update steps above. | yes |
| `build_db.py` | County CSVs → `homeowners.db`. | yes |
| `build_site.py` | `homeowners.db` → `docs/data/*.json`. | yes |
| `docs/index.html` | **The whole web app**: HTML, CSS and JavaScript in one file. | yes |
| `docs/data/homes.json` | All homesteaded homes (generated). | yes |
| `docs/data/sales/0-63.json` | Sales history, split into 64 files (generated). | yes |
| `docs/manifest.webmanifest`, `docs/icons/` | Install-to-home-screen (PWA) settings and purple house icons. | yes |
| `docs/app/HomeOwners.apk` | The Android app download. | yes |
| `docs/auth.html` | Microsoft sign-in return page for the unused direct OneDrive connection ([SETUP-CLOUD.md](SETUP-CLOUD.md)). | yes |
| `docs/.nojekyll` | Tells GitHub Pages to serve files as they are. | yes |
| `android-app/` | The Android app project (Capacitor). See [The Android app](#the-android-app). | yes (not `node_modules`) |
| `GUIDE.md` | User guide. | yes |
| `SETUP-CLOUD.md` | Backups, plus notes on the optional direct Drive/OneDrive connection. | yes |
| `SeminoleCounty/` | The unzipped county CSVs, about 650 MB. | **no** |
| `homeowners.db` | Working database, about 200 MB. | **no** |
| `*.zip`, `*.new`, `*.old` | Temporary update files. | **no** |
| `android-app/.build-certs/` | School-network certificate store for builds. | **no** |

---

## The data pipeline

### Source files

Only two of the nine CSVs in the zip are used:

- **`Parcels.csv`**: one row per parcel (about 181,000), including owner, site and mailing address, `HasHomestead`,
  property type (DOR code), subdivision, year built, living area, beds, baths, pool, values, last sale date, and latitude/longitude.
- **`AllSales.csv`**: every recorded sale (about 856,000), including date, amount, deed type and qualification.

### `build_db.py`

- Splits the site address into street, city and ZIP. It matches against the known Seminole County city names, longest first.
- `mail_matches_site` is 1 when the mailing address starts with the site street address, which is a second owner-occupancy signal.
- Loads all sales. `last_sale_amount` is the amount on the parcel's most recent sale record.
- Writes to a temporary file and renames it at the end, so a failed build never leaves a half-written database.
- Usage: `python build_db.py [CountyFolder] [--db file]`.

### `build_site.py`

Exports only `homestead = 1` parcels that have coordinates, ordered by value, high to low.

**`docs/data/homes.json`**:

```json
{
  "county": "Seminole County, FL", "dataYear": 2026, "dataAsOf": "2026-11-11", "built": "2026-11-11",
  "cols": ["parcel","owner","street","city","zip","dor","sub","yearBuilt","sqft","beds","baths","pool",
           "value","lastSaleDate","lastSaleAmt","mailingIfDifferent","lat","lon"],
  "cities": [...], "dors": [...], "subs": [...],
  "rows": [["01202930000100000", "SMITH JOHN", "619 CRICKLEWOOD TER", 3, "32746", 0, 12, ...], ...]
}
```

- Each row is an array in `cols` order. `city`, `dor` and `sub` are indexes into the lookup lists, which keeps the file small.
- `mailingIfDifferent` is empty when the bill goes to the home itself.
- The column order must match the constants `P, OWNER, STREET, …` near the top of the script in `docs/index.html`.

**`docs/data/sales/N.json`**: `{ parcel: [[date, amount, deed, qualification], ...] }`, newest first.
A parcel's file is `N = hash(parcel) % 64`, where the hash is `h = (h*31 + charCode) & 0xFFFFFFFF`. This must stay the same as
`bucket()` in `build_site.py` and `bucketOf()` in `index.html`. A home's card downloads only its own file.

Usage: `python build_site.py [--db file] [--year N] [--as-of YYYY-MM-DD]`.

---

## The website (`docs/index.html`)

One self-contained file. The only outside libraries are **Leaflet 1.9.4** and **Leaflet.markercluster 1.5.3**, loaded from unpkg.
Map tiles come from **OpenStreetMap**.

**Layout**
- **PC** (wider than 800 px): filter panel on the left, map in the middle, results table on the right.
- **Phone:** a top bar with **Filters**, the home count and **List**. The filter drawer and list sheet slide over the map.

**Main parts of the script, in order**

| Area | Key names | Notes |
|---|---|---|
| Setup | `NATIVE`, `ho()` | `NATIVE` is true inside the Android app. `ho(method, opts)` calls the app's native plugin. |
| Columns | `P, OWNER, STREET, …` | Indexes into a `homes.json` row. |
| Text notes | `notes`, `NOTES_KEY` | localStorage `homeowners.notes.v1`: `{ parcel: { text, updated } }`. |
| Contacts | `contacts`, `CONTACTS_KEY` | localStorage `homeowners.contacts.v1`: `{ parcel: [{ id, name, tel, email, added }] }`. |
| Voice and photos | `mediaDb()`, `vstore()` | IndexedDB `homeowners` (version 3), stores `voice` and `photos` (each indexed by `parcel`) plus `settings`. |
| Map | `map`, `cluster`, `markerFor()`, `dotStyle()` | Canvas circle markers (radius 9), clustered until zoom 18. Green `#1a7f4b`, or purple `#7b3fe4` when `hasNote()`. |
| Home card | `popupHtml()`, `openHome()`, `salesFor()` | Details, sales table and the notes panel. |
| Voice | `startRec()`, `stopRec()` | MediaRecorder, 5-minute limit. |
| Contacts | `canPickContacts`, `addContacts()` | The app uses Android's picker. Chrome on Android uses the Contact Picker API. Duplicates are skipped by phone number. |
| Messages | `openMessages()`, `addMessagesToNote()` | App only. Reads SMS for the contact's number and appends them to the note, dated, with no duplicates. |
| Shared text | `pendingShare`, `showShareBanner()` | From the PWA `share_target` (`?text=`) or the app's Share intent. |
| Photos | `shrinkImage()`, `openCamera()` | Shrunk to 1600 px JPEG. An in-page camera (getUserMedia), because opening the phone's camera app made Android unload the page. |
| Session | `session`, `restoreSession()` | sessionStorage remembers the open home and map view, in case the page reloads. |
| Location | `onLocateTap()`, `onFix()`, `startCompass()`, `keepAwake()` | `watchPosition`. The heading uses the compass when available, otherwise the GPS heading. Keeps the screen on with Wake Lock, or the app's `keepAwake`. |
| Filters and list | `currentFilter()`, `matches()`, `search()`, `renderTable()` | Filtering is debounced 300 ms. The table shows the top rows of the sorted results. |
| Export | `saveFile()` | CSV of the current results. |
| Backups | `buildBackup()`, `restoreBackupText()` | See [Notes storage and backups](#notes-storage-and-backups). |
| Cloud (unused) | `CLOUD_BUILT_IN` | Direct Google Drive/OneDrive code. No button uses it. See [SETUP-CLOUD.md](SETUP-CLOUD.md). |
| Startup | the final `(async () => …)()` | Loads `homes.json`, fills the filters, shows "data as of", restores the session, and hooks up shared text in the app. |

**Install as a web app (PWA):** `manifest.webmanifest` lets Chrome "Add to Home screen". Its `share_target`
puts HomeOwners in Android's share menu, sending text to `./?text=…`.

---

## Notes storage and backups

All personal data stays **on the device**. Each browser and the Android app keep separate copies.

| What | Where |
|---|---|
| Text notes | localStorage `homeowners.notes.v1` |
| Linked contacts | localStorage `homeowners.contacts.v1` |
| Voice clips (audio blobs) | IndexedDB `homeowners` › `voice` |
| Photos (JPEG blobs) | IndexedDB `homeowners` › `photos` |
| Last backup / last change times | localStorage `homeowners.lastBackup`, `homeowners.lastChange` |

**Backup file** (version 4): one JSON document, saved as `homeowners-notes-YYYY-MM-DD-HHMM.json`.
Phone shares use `.txt` with type text/plain, because Android Chrome refuses to share `.json` ("Permission denied").

```json
{ "app": "HomeOwners", "kind": "notes-backup", "version": 4, "exported": "...",
  "textNotes": 3, "voiceNotes": 1, "photoNotes": 2, "contactCount": 1,
  "notes":    { "<parcel>": { "text": "...", "updated": "...", "address": "...", "owner": "..." } },
  "contacts": { "<parcel>": { "address": "...", "owner": "...", "list": [ { "name": "...", "tel": "..." } ] } },
  "voice":  [ { "parcel": "...", "created": "...", "duration": 5300, "type": "audio/webm", "audio": "data:..." } ],
  "photos": [ { "parcel": "...", "created": "...", "type": "image/jpeg", "image": "data:..." } ] }
```

**Restore merges.** It adds missing items, keeps the newer copy of a text note, skips duplicates, and never deletes anything.

**Share backup**
- **Phone:** the Web Share API. The file is built ahead of time when Filters opens, because sharing must start right after a tap.
- **PC:** a Save dialog (File System Access API).
- **App:** the native share chooser.

**Download a copy** saves to Downloads.

---

## The Android app

`android-app/` is a **Capacitor 7.6.10** project:

- `capacitor.config.json`:
  - appId `io.github.matmatmathew.homeowners`
  - `server.url` is the live site, so the app always shows the current site
  - `www/index.html` is only an offline placeholder
- `android/app/src/main/java/io/github/matmatmathew/homeowners/`
  - `MainActivity.java` registers the plugin.
  - `HomeOwnersPlugin.java` is the native features. The site calls them with `Capacitor.nativePromise('HomeOwners', method, opts)`:

| Method | What it does |
|---|---|
| `pickContact` | Android's contact picker. It needs no contacts permission. Returns `{ name, tel }`. |
| `readSms { phone, limit }` | Asks for READ_SMS the first time. Returns the messages whose number matches on its last 10 digits. |
| `shareText { name, text, mime }` | Writes a cache file and opens the share chooser (FileProvider). The chooser leaves out HomeOwners itself. |
| `saveDownload { name, text, mime }` | Saves to the phone's Downloads (MediaStore). |
| `keepAwake { on }` | Keeps the screen on while location tracking runs. |
| `getSharedText` / event `sharedText` | Text shared into the app (ACTION_SEND text/plain). |

- `AndroidManifest.xml` adds the Share target and these permissions: internet, location, camera, microphone, read SMS.
- **Icons:** a purple house, background `#7B3FE4`.

**Rebuild the APK only after changing `android-app/`.** Website or data changes don't need it.

```
cd android-app
npx cap sync android
cd android
set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
gradlew assembleDebug
copy app\build\outputs\apk\debug\app-debug.apk ..\..\docs\app\HomeOwners.apk
```

Then commit and push `docs/app/HomeOwners.apk`. Users install the new APK over the old one, and their notes are kept.

- **Signing:** the APK is debug-signed with this PC's debug key (`%USERPROFILE%\.android\debug.keystore`). Keep that file.
  An APK signed with a different key can't install over the old one; the user would have to uninstall the app (which deletes notes), so back up first.
- **Requirements:** Node.js (for `npx cap`), Android Studio (its bundled JDK and the Android SDK; `android/local.properties` points to the SDK).
- **SCPS network:** the school firewall inspects HTTPS, so Gradle needs `android-app/.build-certs/truststore.jks`.
  That's Java's `cacerts` plus the firewall's root certificate. `android/gradle.properties` points to it.
  On any other network, delete those two `systemProp.javax.net.ssl.trustStore…` lines.
- **Testing:** use the Android Studio emulator (AVD `Pixel_9_Pro_XL_API_35`). For WebView debugging, run `adb forward` and use `chrome://inspect`.

---

## Publishing and Git

- GitHub Pages publishes `docs/` from `main` about a minute after each push.
- Push as **matmatmathew**. This PC's credential manager defaults to a different GitHub account, so the remote URL
  includes the user name (`https://matmatmathew@github.com/matmatmathew/HomeOwners.git`). Keep it that way.
- Edit `docs/index.html`, preview locally, then commit and push. Changes reach the website and the app.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `update-data.bat`: "not a valid zip" | The download was incomplete. Download it again. |
| `update-data.bat`: "The new data looks wrong" | Open the zip and check it. If the county really changed that much, run `python update_data.py --force`. |
| `update-data.bat`: "Publishing failed" | The data is committed locally. Fix the sign-in (see above) and run `git push`. |
| `python` not found | Install Python 3 from python.org. No extra packages are needed. |
| The site shows old data after an update | Wait 2 minutes, then reload. On a phone, close and reopen the app or tab. |
| The site says "Could not load the home data" | Check the internet connection. The 17 MB file needs to download once per visit. |
| Notes disappeared | They're per device and per browser, and the app is separate from Chrome. Restore the latest backup. |
| Share backup says "Permission denied" (phone) | Fixed by sharing as `.txt`. If it returns, use **Download a copy**. |
| Gradle "PKIX path building failed" | The school firewall. See the SCPS network note in [The Android app](#the-android-app). |
