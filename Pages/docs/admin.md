# Running and configuring

## Setup

 1. Python 3 is required. Create and activate a virtual environment:
    ```python3 -m venv env``` then ```source env/bin/activate``` (macOS/Linux) or ```env\Scripts\activate``` (Windows). Leave it with ```deactivate```.
 2. `pip3 install -r requirements.txt`
 3. `python3 hiw.py`, then browse to `http://localhost:5001/`.

Run it from the project folder; page paths are relative to where you start it.

## Settings

Settings are in `config.py`.

| Setting | Meaning |
|---|---|
| `siteName` | name used in the page title |
| `siteHostname`, `sitePort` | where to listen (`0.0.0.0` means every device on your network; port can be set with the `PORT` environment variable, default 5001) |
| `sitePages` | folder holding the pages (`Pages`) |
| `siteAssets` | folder name for images and files (`_assets`) |
| `siteHistory` | folder under the pages folder for snapshots (`.history`) |

## Layout

    Pages/start.md                      the home page
    Pages/_assets/                      images and files for root pages
    Pages/<namespace>/<page>.md         a page in a namespace
    Pages/<namespace>/_assets/          images for that namespace
    Pages/wiki/sidebar.md               the sidebar
    Pages/.history/                     saved versions (see history)
    static/easymde/                     the bundled editor (works offline)

## Security

HIW has no logins. Anyone who can reach the server can read and edit pages, and the editor name is self-reported. Keep it on a trusted home network, or put it behind a reverse proxy with a password if it is exposed further.

See [[docs:history|History and recovery]] for undoing changes.
