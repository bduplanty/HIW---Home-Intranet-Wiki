# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- MIT `LICENSE`.
- Automated tests (`pytest`) in `tests/`; development dependencies in `requirements-dev.txt`.
- README instructions for creating, activating and deactivating the virtual environment.
- Page editing with EasyMDE (vendored in `static/easymde/`, works offline): pill-style "Edit" button in the header, `/_edit/<page>/` and `/_edit/<ns>/<page>/` routes, atomic saves, new pages can be created by editing them.
- Editor name is asked on first edit and kept in a 30-day cookie (`hiw_editor`); "not you?" lets it be changed.
- Every save is snapshotted to `Pages/.history/<page>.md/<timestamp>__<editor>.md`; the page footer shows who last edited and when.
- "Site Map" link centered in the footer, leading to `/_sitemap/`, an automatically generated list of every page by namespace.
- "Navigation" pill on the left sidebar; it collapses and remembers its state like the Contents panel.
- Table of contents (level 1 and 2 headings) in a sticky right-hand panel that can be collapsed; the choice is remembered per browser.
- "View Page History" link in the footer: lists saved versions, view any of them, and restore one into the editor (`/_history/<page>/`).
- Edit conflict protection: a save is refused (and the editor text kept) if the page changed since it was opened.
- Documentation in the `docs` namespace (`Pages/docs/`), linked from the sidebar.
- `.hiwright` / `.hiwcenter` / `.pill` CSS classes.
- `==text==` highlighting (rendered as `<mark>`), now built into `hiwmd.py`.
- Responsive layout: below 800px the page becomes one column (contents panel above the page, sidebar below), with 16px form fields for iOS Safari and images/tables kept within the screen.

### Removed
- TinyMCE (was never wired up).
- The `MarkdownHighlight` dependency (unmaintained, and it broke newer Markdown releases); `???text???`, `___text___` and `==text==` are now all built into `hiwmd.py`.
- Unused dependencies (`requests`, `certifi`, `urllib3`, `idna`, `charset-normalizer`) and the frozen 2021 pins.

### Changed
- `requirements.txt` lists only direct dependencies with compatible-release pins (`Flask~=3.1`, `Markdown~=3.8`); tested on Python 3.9 and 3.14.
- Editor cookie name and lifetime are now `siteEditorCookie` and `siteEditorCookieDays` in `config.py`, and every setting there is commented.
- The asset URL prefix follows `siteAssets` and the sidebar page is set by the new `siteSidebar` setting, instead of being hardcoded.
- `siteHome` and `siteCSS` in `config.py` are now used (home redirect and stylesheet); removed unused `siteCSSOverride` and unused imports.
- Top bar logo is set by `siteLogo` in `config.py` (a file in `static/`); templates can read all settings through `site`.
- `siteSidebarPills` option: sidebar links render as pale rounded buttons that contrast with the solid action pills.
- Site name (`siteName` in `config.py`) shown in bold next to the logo in the top bar.
- Top bar now uses the logo (44px) as the home link, on a light blue bar that matches the header colors instead of gray.
- Layout is now three columns (sidebar 20%, page 60%, contents panel 20%) instead of four equal-ish ones.
- Default port is now 5001.
- Page rendering uses shared `readpage()` / `renderpage()` helpers and a single `MD_EXTENSIONS` list.

### Fixed
- Several `[[wikilinks]]` or image embeds on one line are matched separately (the patterns used to run across links).
- The newest save is always the latest attribution, even when two people save within the same second.
- Saved pages keep their file permissions instead of becoming owner-only.
- Attribution ignores stray files in a page's history folder.
- The missing-name error no longer resets the conflict check.
- Two saves within one second no longer overwrite each other's snapshot.
- Favicon: pages now declare an icon, and `/favicon.ico` serves the `siteLogo` image with its correct type (it was a PNG sent as an .ico).
- Removed the white gap between the top bar and the page title bar.
- The header's Edit / Back to page pill is vertically centered in the bar.
- Page names are validated and resolved with `safe_join`, closing a path traversal hole.
- Missing pages return 404 instead of a 500 error.
- Page and sidebar files are read with `with` and UTF-8 encoding.
- A missing sidebar no longer renders "None".
- Blank lines in fenced code blocks no longer lose their background; the background is now on `pre`.
- `.hiwcenter` used invalid `float: center`; it now centers as a block element.

### Security
- Raw HTML in page source is now escaped instead of passed through.
- Link and image URLs with schemes other than http, https and mailto (such as `javascript:`) are replaced with `#`.
- Name cookie is HttpOnly; namespace names are validated on the namespace asset route.

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
