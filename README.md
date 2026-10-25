# Home Intranet Wiki (HIW)

## Goals

- Python 3
- Flask
- Markdown extra
- Simple Folder namespace with _assets for media
- Text files
- Simple search
- Simple C R U D
- Simple Media _assets management

## WIP
This is a work in progress.  More to follow, if anyone is interested...

## What is it?

A small, self-hosted wiki for a home or small-team network. Pages are plain
Markdown files in folders: no database, no build step, nothing to sign up for.
Edit pages in the browser, see who changed what, and roll back any edit.

## Is it right for you?

**A good fit if you want:**
- A wiki for family notes, how-tos, server docs or a small team on a trusted network
- Files you own: every page is a `.md` file you can read, back up, grep or put in git
- Something you can understand and change: one small Flask app and a config file
- No external services: the editor and all assets are bundled, so it works offline

**Not a good fit if you need:**
- Logins, permissions or per-page access control (anyone who can reach the server can edit)
- Full-text search (not built yet)
- Deleting pages from the browser, or uploading images from the browser (not built yet;
  put files in an `_assets` folder by hand)
- A public-facing site or a large multi-user deployment

## Features

- **Markdown pages** with tables, fenced code, footnotes, admonitions and `==highlighting==`
- **Namespaces** (folders): `[[namespace:page|Title]]` links and `![[image.png|300x200]]` embeds
- **Browser editor** (EasyMDE) with toolbar and preview; new pages are created by editing them
- **History and recovery:** every save is kept; view any old version and restore it
- **Edit-conflict protection:** if someone saved first, you are warned and your text is kept
- **Attribution:** the footer shows who last edited a page and when
- **Navigation:** a sidebar you write yourself, a contents panel built from headings, an automatic site map
- **Works on phones**, and is configured through one commented config file
- **Safe by default:** raw HTML and `javascript:` links in pages are neutralised

## Installing

Requires Python 3 (tested with 3.9 and 3.14). Run every command from the project folder.

 1. Get the code:

        git clone https://github.com/bduplanty/HIW---Home-Intranet-Wiki.git
        cd HIW---Home-Intranet-Wiki

 2. Create a virtual environment (first time only). It keeps HIW's packages separate from the rest of your system:

        python3 -m venv env

 3. Enter (activate) the virtual environment. Your prompt will start with `(env)`:

        source env/bin/activate        # macOS / Linux
        env\Scripts\activate           # Windows

 4. Upgrade pip (first time only). A new virtual environment starts with the older pip that ships with Python:

        python -m pip install --upgrade pip

 5. Install the dependencies (first time only, with the environment active):

        python -m pip install -r requirements.txt

 6. Start the wiki:

        python3 hiw.py

 7. Open <http://localhost:5001/> in a browser.

To **stop** the wiki, press Ctrl+C in the terminal.

To **exit** the virtual environment, run `deactivate`. The `(env)` in your prompt goes away.

Next time, just repeat steps 3 and 6: enter the environment, then start the wiki. If the
packages are ever out of date, enter the environment and run step 5 again. To start over,
delete the `env` folder and repeat steps 2 to 5.

The repository includes a few sample pages in `Pages/`. Delete them or start editing.
To reach the wiki from other devices, use your computer's network address, for example
`http://192.168.1.20:5001/`, and read the security note in the documentation first.

## Documentation

Full usage docs live inside the wiki itself, in the `docs` namespace:
**<http://localhost:5001/docs/start/>** (or read the Markdown in `Pages/docs/`):

- Editing pages, your name, and edit conflicts
- History and recovery
- Page syntax (links, images, highlighting)
- Running and configuring (every setting in `config.py`)

See [CHANGELOG.md](CHANGELOG.md) for what has changed.

## Known gaps

Search, page deletion, media upload and management, and logins.

## Development

With the virtual environment active:

    python -m pip install -r requirements-dev.txt
    python3 -m pytest        # uses a throwaway wiki, never touches Pages/

Layout: `hiw.py` (the app), `hiwmd.py` (Markdown extension for links, embeds and highlighting),
`config.py` (settings), `templates/`, `static/`, `Pages/` (your content), `tests/`.

## License

MIT. You may use, modify and redistribute HIW freely, as long as you keep the copyright
notice and license text. See [LICENSE](LICENSE).

Bundled third-party files in `static/easymde/` keep their own licenses, which are stated in
their headers: EasyMDE (MIT) and Font Awesome 4.7 (CSS: MIT, font: SIL OFL 1.1).
