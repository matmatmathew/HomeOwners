# HomeOwners user guide

HomeOwners is a map of every **owner-occupied home in Seminole County, FL**: every home with a
homestead exemption, which in Florida means the owner lives there as their permanent residence. Rentals,
second homes and vacant lots aren't shown. You can filter the homes, look up owners and sales, and keep
your own notes, photos, voice notes and contacts for any home.

- **Website (PC or phone):** https://matmatmathew.github.io/HomeOwners/
- **Android app:** https://matmatmathew.github.io/HomeOwners/app/HomeOwners.apk (see [Android app](#android-app))

---

## The screen

| PC | Phone |
|---|---|
| Filters on the left, the map in the middle, the results list on the right. | The top bar has **Filters**, the number of homes, and **List**. Filters and List slide in over the map. |

- **Green dot:** an owner-occupied home.
- **Purple dot:** a home with your notes, photos, voice notes or contacts.
- **Numbered circles:** groups of homes. Zoom in or tap them to split them up.

The line under the title shows how many homes are loaded and the date of the county data.

## Find homes

Open **Filters** and use any combination of:

| Filter | What it does |
|---|---|
| Owner, address or parcel | Search text, e.g. `SMITH` or `CRICKLEWOOD`. Parcel numbers work with or without dashes. |
| City / ZIP code / Property type | Tick or select one or more. The numbers show how many homes each has. |
| Subdivision contains | Part of a subdivision name. |
| Market (just) value $ | The Property Appraiser's market value, min and max. |
| Year built, bedrooms / bathrooms, living area | Ranges and minimums. |
| Last sale date / Last sale price | When it last sold and for how much. Some "sales" are $100 family transfers. |
| Tax bill mailed to | **The home itself** is a second sign the owner lives there. **A different address** can mean a trust, an out-of-area owner, or a mailing service. |
| Has pool | Only homes with a pool. |
| Only homes with my notes | Only the purple homes. |
| Only what's visible on the map | Limits the list to the part of the map you're looking at. |

The map and list update as you type. On a phone, tap **Show results** to close Filters.

- **Export CSV** saves the current list as a spreadsheet file that opens in Excel or Google Sheets.
- **Reset** clears every filter.
- **List** shows the results as a table. Tap a column heading to sort by it, and tap a row to jump to that home.

## Look at a home

Tap a dot to open the home's card. It shows the owner, address, parcel number, value, size, year
built, the mailing address if it's different, and the full **sales history**. The card also has your
notes for that home.

## Your notes

Everything below is saved **on this device only** (in this browser or in the app). Nobody else can see it.
Back it up to keep it safe (see [Back up and restore](#back-up-and-restore)).

- **Text note:** type anything. It saves as you type and shows when it was last saved.
- **Voice notes:** tap **● Record**, speak, and tap the button again to stop (up to 5 minutes per clip). Each clip has a player and a **Delete** button.
  The first time, allow the microphone.
- **Photos:** **📷 Take photo** opens the camera inside the page. **🖼 Choose photo** picks existing pictures.
  Photos are shrunk to save space. Tap a photo to view it full size, where **Delete photo** removes it. The first time, allow the camera.
- **Contacts:** **Pick from contacts** links a person from your phone's contacts to the home. You can then call or
  text them from the card. This works in the Android app and in Chrome on Android. A PC browser can't open your contacts.
- **📨 Messages** (Android app only): shows your text messages with a linked contact. Tap **Add to note** on a
  message, or **Add all to this home's note**. Messages already in the note aren't added again.
- **Text shared from another app:** in Messages (or any app), use **Share** and pick **HomeOwners**. A banner
  appears. Open the right home and tap **Add to this home**.

As soon as a home has any note, photo, voice note or contact, its dot turns purple.

## Back up and restore

Open **Filters**. The purple **My notes** card at the top shows how many homes have notes and when you last backed up.

- **Share backup**
  - On a phone, the share menu opens. Pick **Drive**, **OneDrive**, Gmail, or any other app to save the file there.
  - On a PC, a Save dialog opens. Pick any folder, for example your OneDrive folder.
- **Download a copy** saves the backup to the phone's or PC's Downloads folder.
- **Restore backup** opens a file picker. Pick a backup file from Drive, OneDrive, Downloads, or anywhere else.

One backup file holds **everything**: text notes, voice notes, photos and contacts. Backups are named
`homeowners-notes-<date>-<time>` and end in `.json`, or `.txt` when shared from a phone. Both kinds restore.

Restoring **merges**: it adds what's missing and keeps the newer copy of a text note. It never deletes anything,
so it's safe to restore the same file twice.

Use backups to **move notes to another device**, or between Chrome and the Android app (each keeps its own notes).
Back up on one, then restore on the other.

> Notes stay on the device until you back them up. Clearing the browser's site data, or uninstalling the
> app, deletes them. Back up regularly.

## Location

Tap the **location button** (bottom right of the map, next to the zoom buttons) to show where you are. Tap it again to **follow** you
as you walk. The map keeps you centered and an arrow shows the direction you're facing. Drag the map to stop
following, and tap the button to start again. While following, the screen stays on.
The first time, allow location access.

## Android app

The app is the same map and notes, plus phone features the website can't use: Android's contact picker, your text
messages with a linked contact, and **Share › HomeOwners** from other apps.

**Install**

1. On your phone, open the website in Chrome and tap **📱 Get the Android app**. The button only shows in phone
   browsers, not inside the app.
2. Open the downloaded file. If Android blocks it, tap **Settings**, turn on **Allow from this source**, and go back.
3. Tap **Install**. If Play Protect warns that the app is unknown (it isn't from the Play Store), choose **Install anyway**.

**Permissions** are asked the first time each feature is used: location, camera, microphone, and text messages
(Android says "send and view". The app only reads them).

**Updates:** the app shows the live website, so new features and new county data appear without reinstalling.
It needs an internet connection to open.

## The data

The homes come from the **Seminole County Property Appraiser's** public parcel download. It is refreshed when
the site owner loads a new download (see `README.md`). The line under the title shows the date of that download.

When the data is updated, your notes stay attached to their homes, because they're tied to the parcel number. A
home that loses its homestead exemption (sold to an investor, for example) disappears from the map, but its notes
stay on your device and in your backups. They reappear if the home qualifies again.
