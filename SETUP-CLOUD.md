# Google Drive and OneDrive backups

## How it works now (no setup)

**Filters › My notes › Share backup / Restore backup**

- **Phone:** Share backup opens the normal share menu; pick Google Drive, OneDrive, Gmail or any app.
  Restore backup opens the file picker; pick the file from Drive, OneDrive, Downloads or anywhere.
- **PC (Chrome or Edge):** Share backup opens a Save dialog; pick any folder (e.g. your OneDrive or
  Google Drive folder). It opens in the same folder next time.

Backups are named `homeowners-notes-<date>-<time>.json` (Android shares them as `.backup.txt`; both restore).

## Optional later: direct connection

For one-tap backup and "restore latest" on phones too, the site must be registered once with Google and
Microsoft and the client IDs put in `CLOUD_BUILT_IN` in `docs/index.html`. The connection code is already in
`docs/index.html` but no button uses it right now; it would need to be wired back in.

| Service | Field | Value |
|---|---|---|
| Google | Authorized JavaScript origin | `https://matmatmathew.github.io` |
| Google | Scope | `https://www.googleapis.com/auth/drive.file` |
| Microsoft | Redirect URI (Single-page application) | `https://matmatmathew.github.io/HomeOwners/auth.html` |
| Microsoft | Delegated permissions | `Files.ReadWrite`, `offline_access` |
| Microsoft | Account types | Any organizational directory and personal Microsoft accounts |
