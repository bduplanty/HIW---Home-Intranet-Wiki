# History and recovery

There is no database. Instead, **every save also writes a copy** of the page into a hidden folder:

    Pages/.history/<page>.md/<YYYYmmddTHHMMSS>__<editor>.md
    Pages/.history/<namespace>/<page>.md/20261024T144410__Bruce.md

The filename holds the date and time and the editor's name. The newest file is what the page footer uses for *Last edited by*. A page that was never saved through the editor shows only its file's modified time.

## Looking at old versions

Click **View Page History** at the right of the page footer, after the *Last edited* information. It lists every saved version, newest first, with the date, time and editor. **View** shows that version as it was rendered then.

## Restoring a version

Click **Restore** next to a version in the list (or **Restore this version** while viewing it). The editor opens with that version's text in it. Review it and press **Save**.

The restore is itself saved as a new version, so nothing is ever lost, including the version you replaced. If someone else changed the page after you opened the editor, the usual [[docs:editing|conflict warning]] appears.

You can also read the snapshot files directly: they are plain Markdown. Folders starting with a dot are hidden in Finder (press Cmd+Shift+. to show them).

## Notes

 - Snapshots are full copies, not diffs. For small text pages this is a few kilobytes per save.
 - Delete old snapshot files by hand if you want to prune.
 - History is at `/_history/<page>/` or `/_history/<namespace>/<page>/`.
 - Pages edited outside the wiki (in a text editor, or by git) are not snapshotted until they are next saved through the editor.
 - `Pages/.history/` can be added to `.gitignore` if you do not want snapshots committed.
