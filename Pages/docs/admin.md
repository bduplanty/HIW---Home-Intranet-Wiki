# Running and configuring

## Setup

 1. Python 3 is required. Create and activate a virtual environment:
    ```python3 -m venv env``` then ```source env/bin/activate``` (macOS/Linux) or ```env\Scripts\activate``` (Windows). Leave it with ```deactivate```.
 2. `pip3 install -r requirements.txt`
 3. `python3 hiw.py`, then browse to `http://localhost:5001/`.

Run it from the project folder; page paths are relative to where you start it.

## Starting automatically

To keep the wiki running without a terminal window, run it as a background service. In the
examples below, replace `/path/to/hiw` with the full path to your HIW folder.

### macOS (launchd)

Create `~/Library/LaunchAgents/com.example.hiw.plist`:

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.example.hiw</string>
        <key>ProgramArguments</key>
        <array>
            <string>/path/to/hiw/env/bin/python3</string>
            <string>/path/to/hiw/hiw.py</string>
        </array>
        <key>WorkingDirectory</key>
        <string>/path/to/hiw</string>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
        <key>StandardOutPath</key>
        <string>/tmp/hiw.log</string>
        <key>StandardErrorPath</key>
        <string>/tmp/hiw.log</string>
    </dict>
    </plist>

Then load it (it also starts at every login from now on):

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.hiw.plist

Restart, stop and remove:

    launchctl kickstart -k gui/$(id -u)/com.example.hiw    # restart (after changing config.py)
    launchctl bootout gui/$(id -u)/com.example.hiw         # stop
    rm ~/Library/LaunchAgents/com.example.hiw.plist        # remove for good

The agent starts when you log in, not at boot. `WorkingDirectory` matters because page paths
are relative to where HIW starts. Errors and requests are written to `/tmp/hiw.log`.

### Linux (systemd)

Create `~/.config/systemd/user/hiw.service`:

    [Unit]
    Description=HIW wiki

    [Service]
    WorkingDirectory=/path/to/hiw
    ExecStart=/path/to/hiw/env/bin/python3 hiw.py
    Restart=always

    [Install]
    WantedBy=default.target

Then run `systemctl --user enable --now hiw`. To keep it running when you are logged out, run
`loginctl enable-linger $USER` once.

### Windows

Use Task Scheduler: create a task that runs at log on, with the program
`C:\path\to\hiw\env\Scripts\python.exe`, the argument `hiw.py`, and "Start in" set to your HIW folder.

## Settings

Settings are in `config.py`.

| Setting | Meaning |
|---|---|
| `siteName` | name used in the page title |
| `siteHostname`, `sitePort` | where to listen (`0.0.0.0` means every device on your network; port can be set with the `PORT` environment variable, default 5001) |
| `sitePages` | folder holding the pages (`Pages`) |
| `siteAssets` | folder name for images and files (`_assets`); also the URL prefix they are served from |
| `siteSidebarPills` | `True` shows each sidebar link as a button, `False` shows plain text links |
| `siteEditorCookie`, `siteEditorCookieDays` | cookie name and the number of days an editor's name is remembered (`hiw_editor`, `30`) |
| `siteLogo` | image shown at the left of the top bar, a file inside the `static` folder (`logo.png`); drop your own image in `static/` and change this name |
| `siteHome` | page opened at `/` (`start`) |
| `siteSidebar` | page shown in the left sidebar (`wiki/sidebar`) |
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
