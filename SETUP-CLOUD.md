# Google Drive and OneDrive backups

## How it works now (no setup)

The **Back up to / Restore from Google Drive / OneDrive** buttons (Filters › My notes) use what's
already on the device, where you're signed in:

- **Phone:** Back up opens the share menu with the backup attached; tap Drive or OneDrive and pick the
  HomeOwners folder. Restore opens the file picker; open ☰ › Drive (or OneDrive) › HomeOwners.
- **PC (Chrome or Edge):** the first backup to each service asks you to choose that service's folder
  (Google Drive for desktop "My Drive", usually G:, or your OneDrive folder). After that, backups go straight
  into `<folder>\HomeOwners\` and Restore loads the newest one from there. "Change PC folders" forgets the choice.

Backups are named `homeowners-notes-<date>-<time>.json` (Android shares them as `.backup.txt`; both restore).

## Optional later: direct connection

For one-tap backup and "restore latest" on phones too, the site must be registered once with Google and
Microsoft and the client IDs put in `CLOUD_BUILT_IN` in `docs/index.html`. The code for that is already in
place and switches on by itself when the IDs are filled in.

| Service | Field | Value |
|---|---|---|
| Google | Authorized JavaScript origin | `https://matmatmathew.github.io` |
| Google | Scope | `https://www.googleapis.com/auth/drive.file` |
| Microsoft | Redirect URI (Single-page application) | `https://matmatmathew.github.io/HomeOwners/auth.html` |
| Microsoft | Delegated permissions | `Files.ReadWrite`, `offline_access` |
| Microsoft | Account types | Any organizational directory and personal Microsoft accounts |
