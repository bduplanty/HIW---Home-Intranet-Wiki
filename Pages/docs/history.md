# History and recovery

There is no database. Instead, **every save also writes a copy** of the page into a hidden folder:

    Pages/.history/<page>.md/<YYYYmmddTHHMMSS>__<editor>.md
    Pages/.history/<namespace>/<page>.md/20261024T144410__Bruce.md

The filename holds the date and time and the editor's name. The newest file is what the page footer uses for *Last edited by*. A page that was never saved through the editor shows only its file's modified time.

## Looking at old versions

Open the folder for the page in Finder or a terminal and read the files; they are plain Markdown. Folders starting with a dot are hidden in Finder (press Cmd+Shift+. to show them).

## Restoring a version

 1. Open the old snapshot and copy its text.
 2. Click **Edit** on the page, replace the text, and **Save**.

The restore is itself saved as a new version, so nothing is ever lost, including the version you replaced.

## Notes

 - Snapshots are full copies, not diffs. For small text pages this is a few kilobytes per save.
 - Delete old snapshot files by hand if you want to prune.
 - Pages edited outside the wiki (in a text editor, or by git) are not snapshotted until they are next saved through the editor.
 - `Pages/.history/` can be added to `.gitignore` if you do not want snapshots committed.
