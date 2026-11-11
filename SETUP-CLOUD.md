# Google Drive and OneDrive backups

Setup happens inside the app: **Filters › My notes › ⚙ Cloud setup**. The screen walks through
registering the site with Google and Microsoft (links open the right pages, Copy buttons give the exact
addresses to paste), then you paste the client ID, tap **Save**, then **Connect**.

- Client IDs are saved on that device. **Copy setup link** makes a link that carries them to your other
  phone or PC, which then only needs **Connect**.
- To make the IDs work on every device without a setup link, put them in `CLOUD_BUILT_IN` in
  `docs/index.html` and push. Client IDs are public identifiers, not passwords.

Values the registration pages ask for:

| Service | Field | Value |
|---|---|---|
| Google | Authorized JavaScript origin | `https://matmatmathew.github.io` |
| Google | Scope | `https://www.googleapis.com/auth/drive.file` |
| Microsoft | Redirect URI (Single-page application) | `https://matmatmathew.github.io/HomeOwners/auth.html` |
| Microsoft | Delegated permissions | `Files.ReadWrite`, `offline_access` |
| Microsoft | Account types | Any organizational directory and personal Microsoft accounts |

Backups are saved as `HomeOwners/homeowners-notes-<date>-<time>.json` in each service.
The Google connection can only see files the site created (drive.file), not the rest of your Drive.
While the Google app is in "Testing", only the Google accounts listed as test users can connect.
