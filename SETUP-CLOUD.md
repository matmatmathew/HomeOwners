# Connect Google Drive and OneDrive backups (one-time setup)

The "Back up to Google Drive / OneDrive" buttons need the site registered once with each
company. Both are free. Each registration gives you a **client ID**, a public identifier
(not a password) that goes into `docs/index.html`:

```js
const CLOUD = {
  googleClientId: '',      // paste the Google client ID here
  microsoftClientId: '',   // paste the Microsoft application (client) ID here
};
```

The site address is `https://matmatmathew.github.io` and the site lives under `/HomeOwners/`.

## Google Drive (about 15 minutes)

1. Go to https://console.cloud.google.com and sign in with the Google account whose Drive should hold the backups.
2. Create a project: project picker at the top → **New project** → name it `HomeOwners` → **Create**, then select it.
3. Turn on the Drive API: **APIs & Services → Library** → search **Google Drive API** → **Enable**.
4. Consent screen: **APIs & Services → OAuth consent screen** (may be called **Google Auth Platform**).
   - User type **External**, app name `HomeOwners`, your email for support and developer contact.
   - Scopes / Data access: add `.../auth/drive.file` ("See, edit, create and delete only the specific Google Drive files you use with this app").
   - Audience / Test users: add your own Google address. (Leaving the app in **Testing** is fine for personal use.)
5. Client ID: **APIs & Services → Credentials → Create credentials → OAuth client ID**.
   - Application type **Web application**, name `HomeOwners site`.
   - **Authorized JavaScript origins**: add `https://matmatmathew.github.io`
   - No redirect URIs are needed.
6. Copy the **Client ID** (ends in `.apps.googleusercontent.com`).

The site can only see files it created itself (the `HomeOwners` folder and its backups), not the rest of your Drive.

## OneDrive (about 10 minutes)

1. Go to https://portal.azure.com and sign in with the Microsoft account whose OneDrive should hold the backups.
   (A free personal Microsoft account works. If asked, the free Azure sign-up is not needed for app registrations.)
2. Search for **App registrations** → **New registration**.
   - Name `HomeOwners`.
   - Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**.
   - Redirect URI: platform **Single-page application (SPA)**, URI `https://matmatmathew.github.io/HomeOwners/auth.html`
   - **Register**.
3. **API permissions → Add a permission → Microsoft Graph → Delegated** → tick **Files.ReadWrite** and **offline_access** → **Add permissions**.
4. Copy the **Application (client) ID** from the **Overview** page.

## After both

Paste both IDs into `CLOUD` in `docs/index.html`, then commit and push. (Or send them to Claude to do it.)
The first tap on each button asks you to sign in and approve access; after that backups are one tap.
