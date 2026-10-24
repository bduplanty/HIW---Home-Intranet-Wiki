# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- README instructions for creating, activating and deactivating the virtual environment.
- Page editing with EasyMDE (vendored in `static/easymde/`, works offline): pill-style "Edit" button in the header, `/_edit/<page>/` and `/_edit/<ns>/<page>/` routes, atomic saves, new pages can be created by editing them.
- Editor name is asked on first edit and kept in a 30-day cookie (`hiw_editor`); "not you?" lets it be changed.
- Every save is snapshotted to `Pages/.history/<page>.md/<timestamp>__<editor>.md`; the page footer shows who last edited and when.
- Edit conflict protection: a save is refused (and the editor text kept) if the page changed since it was opened.
- Documentation in the `docs` namespace (`Pages/docs/`), linked from the sidebar.
- `.hiwright` / `.hiwcenter` / `.pill` CSS classes.
- `==text==` highlighting (rendered as `<mark>`), now built into `hiwmd.py`.

### Removed
- TinyMCE (was never wired up).

### Changed
- Default port is now 5001.
- Page rendering uses shared `readpage()` / `renderpage()` helpers and a single `MD_EXTENSIONS` list.

### Fixed
- Page names are validated and resolved with `safe_join`, closing a path traversal hole.
- Missing pages return 404 instead of a 500 error.
- Page and sidebar files are read with `with` and UTF-8 encoding.
- A missing sidebar no longer renders "None".
- Blank lines in fenced code blocks no longer lose their background; the background is now on `pre`.
- `.hiwcenter` used invalid `float: center`; it now centers as a block element.

### Security
- Raw HTML in page source is now escaped instead of passed through, preventing stored XSS.

## 2021-09-25

### Added
- Namespaces: `Pages/<namespace>/<page>.md` with per-namespace `_assets`.
- Image embeds with sizing: `![[image.png|300]]` and `![[image.png|300x200]]`.
- Wikilinks with titles: `[[ns:page|title]]` and `[[page|title]]`.

### Changed
- Updated requirements; fixed a MarkdownHighlight hang.

## 2021-08-29

### Added
- Initial templates, requirements and README.
- Beginning of namespace support.

## 2021-08-28

### Added
- Initial commit.
