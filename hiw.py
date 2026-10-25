#!/usr/bin/env python

import hashlib
import logging
import stat
import tempfile
import threading
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from flask import Flask, abort, redirect, send_from_directory, g, render_template, request, url_for
from werkzeug.exceptions import NotFound
from werkzeug.utils import safe_join
import config
import os
import re
import markdown
from markdown import Extension
from markdown.treeprocessors import Treeprocessor

logging.basicConfig(level=logging.INFO)

# source env/bin/activate

# if wiki:nav?? - display first x lines as navigation? otherwise home only?
# if wiki:footer - replace footer

app = Flask(__name__, static_folder=config.siteStatic)


@app.context_processor
def inject_site():
    return {"site": config}


@app.route("/")
def index():
    return redirect(url_for('displaypage', pagename=config.siteHome))

@app.route("/" + config.siteAssets + "/<filename>")
## Send an image or file from asset directory
def sendfile(filename):
    directory = os.path.join(config.siteBase, config.sitePages, config.siteAssets) #app.config['UPLOAD_FOLDER'])
    logging.info("Asset requested: " + directory + " | " + filename)
    return send_from_directory(directory, filename)  #flask.send_from_directory

SAFE_SCHEMES = ("", "http", "https", "mailto")


def safeurl(url):
    """Return url if it is relative or uses an allowed scheme, otherwise '#'."""
    # browsers ignore whitespace and control characters inside a scheme ("java\tscript:")
    cleaned = "".join(ch for ch in url if ord(ch) > 32)
    try:
        scheme = urlsplit(cleaned).scheme.lower()
    except ValueError:
        return "#"
    return url if scheme in SAFE_SCHEMES else "#"


class SafeUrlTreeprocessor(Treeprocessor):
    def run(self, root):
        for el in root.iter():
            for attr in ("href", "src"):
                if attr in el.attrib:
                    el.set(attr, safeurl(el.get(attr)))


class EscapeHtmlExtension(Extension):
    """Escape raw HTML in page source instead of passing it through, and drop unsafe link schemes such as javascript:."""

    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')
        md.treeprocessors.register(SafeUrlTreeprocessor(md), 'safeurl', 10)


MD_EXTENSIONS = ['extra', 'wikilinks', 'toc', 'admonition', 'hiwmd:hiwExtension', EscapeHtmlExtension()]
SIDEBAR_EXTENSIONS = ['extra', 'wikilinks', 'hiwmd:hiwExtension', EscapeHtmlExtension()]
NAME_RE = re.compile(r'^[\w\- ]+$')


def pagepath(names):
    """Return the .md path for a page, or abort(404) if the name is unsafe."""
    if not all(NAME_RE.match(name) for name in names):
        abort(404)
    base = os.path.join(config.siteBase, config.sitePages)
    path = safe_join(base, *names[:-1], names[-1] + ".md")
    if path is None:
        abort(404)
    return path


def readpage(*names):
    """Return the markdown source of a page, or abort(404) if it is missing or the name is unsafe."""
    path = pagepath(names)
    if not os.path.isfile(path):
        abort(404)
    with open(path, "r", encoding="utf-8") as page:
        return page.read()


## Edit history: every save is also written to Pages/.history/<page>/<YYYYmmddTHHMMSS>__<editor>.md
## The newest file there gives the page's attribution; restoring = saving an older file's text again.
TS_FORMAT = "%Y%m%dT%H%M%S"


def cleanname(name):
    return re.sub(r'[^\w\- ]', '', name or '').strip()[:40]


def historydir(names):
    return os.path.join(config.siteBase, config.sitePages, config.siteHistory, *names[:-1], names[-1] + ".md")


def lastedit(names, path):
    """Return (editor, datetime) for a page; editor is None if it was never saved through the editor."""
    saved = versions(names)
    if saved:
        return saved[0][1], saved[0][2]
    try:
        return None, datetime.fromtimestamp(os.path.getmtime(path))
    except OSError:
        return None, None


## Optimistic locking: the edit form carries a hash of the page as it was opened.
## A save is refused if the page has changed since, so edits are never silently overwritten.
SAVE_LOCK = threading.Lock()


def pageversion(names):
    try:
        with open(pagepath(names), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()
    except OSError:
        return ""


VERSION_RE = re.compile(r'^\d{8}T\d{6}__[\w\- ]+$')


def pageurl(names):
    if len(names) == 1:
        return url_for("displaypage", pagename=names[0])
    return url_for("displaynspage", namespace=names[0], pagename=names[1])


def versions(names):
    """Return saved versions of a page as (version, editor, datetime), newest first."""
    found = []
    try:
        files = os.listdir(historydir(names))
    except OSError:
        return found
    for name in sorted(files, reverse=True):
        stem = name[:-3]
        if name.endswith(".md") and VERSION_RE.match(stem):
            found.append((stem, stem[17:], datetime.strptime(stem[:15], TS_FORMAT)))
    return found


def readversion(names, version):
    if not VERSION_RE.match(version or ""):
        abort(404)
    path = safe_join(historydir(names), version + ".md")
    if path is None or not os.path.isfile(path):
        abort(404)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def savepage(names, content, editor):
    path = pagepath(names)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except OSError:
        mode = 0o644
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    hdir = historydir(names)
    os.makedirs(hdir, exist_ok=True)
    when = datetime.now()
    # snapshots sort by timestamp, so every save of a page needs its own second
    taken = {name[:15] for name in os.listdir(hdir)}
    while when.strftime(TS_FORMAT) in taken:
        when += timedelta(seconds=1)
    snapshot = "{}__{}.md".format(when.strftime(TS_FORMAT), editor)
    with open(os.path.join(hdir, snapshot), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    logging.info("Saved " + path + " as " + editor)


def flattentoc(tokens, maxlevel=2):
    """Flatten Markdown's nested toc_tokens into (level, id, name) for headings up to maxlevel."""
    flat = []
    for token in tokens:
        if token["level"] <= maxlevel:
            flat.append((token["level"], token["id"], token["name"]))
        flat.extend(flattentoc(token["children"], maxlevel))
    return flat


def renderpage(names, source):
    g.siteName = config.siteName
    g.pagename = ":".join(names)
    g.editurl = url_for("editpage", path="/".join(names))
    g.historyurl = url_for("pagehistory", path="/".join(names))
    g.editor, g.edited = lastedit(names, pagepath(names))
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    html = md.convert(source)
    return render_template("page.html", html=html, sidebarhtml=showsidebar(), toc=flattentoc(md.toc_tokens))


@app.route("/<pagename>/")
def displaypage(pagename):
    logging.info('Page request(S): ' + pagename)
    return renderpage((pagename,), readpage(pagename))

@app.route("/<namespace>/<pagename>/")
def displaynspage(namespace, pagename):
    logging.info('Page request: ' + namespace + ":" + pagename)
    return renderpage((namespace, pagename), readpage(namespace, pagename))

@app.route("/_edit/<path:path>/", methods=["GET", "POST"])
def editpage(path):
    names = tuple(path.split("/"))
    if len(names) > 2:
        abort(404)
    cookie = cleanname(request.cookies.get(config.siteEditorCookie))
    editor = cookie
    error = None
    base = pageversion(names)
    if request.method == "POST":
        content = request.form.get("content", "").replace("\r\n", "\n")
        editor = cleanname(request.form.get("name")) or cookie
        if not editor:
            error = "Please enter your name."
            base = request.form.get("base", base)  # keep the version the editor was opened on
        else:
            with SAVE_LOCK:
                current = pageversion(names)
                if request.form.get("base") == current:
                    savepage(names, content, editor)
                    error = None
                else:
                    who, when = lastedit(names, pagepath(names))
                    error = "This page was changed{} since you opened it. Your text is kept below; press Save again to overwrite their version, or open the current page in another tab first.".format(
                        " by {} at {}".format(who, when.strftime("%H:%M")) if who and when else "")
            if error is None:
                response = redirect(pageurl(names))
                response.set_cookie(config.siteEditorCookie, editor, max_age=config.siteEditorCookieDays * 86400 or None, samesite="Lax", httponly=True)
                return response
        source = request.form.get("content", "")
    elif request.args.get("restore"):
        source = readversion(names, request.args["restore"])
    elif os.path.isfile(pagepath(names)):
        source = readpage(*names)
    else:
        source = ""
    g.siteName = config.siteName
    g.pagename = ":".join(names)
    return render_template("edit.html", source=source, editor=editor, base=base, askname=(not cookie or "rename" in request.args or error),
                           error=error, sidebarhtml=showsidebar())

@app.route("/_history/<path:path>/")
def pagehistory(path):
    names = tuple(path.split("/"))
    if len(names) > 2:
        abort(404)
    pagepath(names)
    g.siteName = config.siteName
    g.pagename = ":".join(names)
    g.pageurl = pageurl(names)
    g.editurl = url_for("editpage", path=path)
    version = request.args.get("v")
    html = who = when = None
    if version:
        html = markdown.markdown(readversion(names, version), extensions=MD_EXTENSIONS)
        who, when = version[17:], datetime.strptime(version[:15], TS_FORMAT)
    return render_template("history.html", versions=versions(names), version=version, html=html,
                           who=who, when=when, sidebarhtml=showsidebar())

def listpages(directory):
    """Names of the pages (.md files) directly inside a directory, sorted."""
    try:
        files = os.listdir(directory)
    except OSError:
        return []
    names = [f[:-3] for f in files if f.endswith(".md") and NAME_RE.match(f[:-3])]
    return sorted(names, key=str.lower)


@app.route("/_sitemap/")
def sitemap():
    base = os.path.join(config.siteBase, config.sitePages)
    rootpages = [(name, url_for("displaypage", pagename=name)) for name in listpages(base)]
    namespaces = []
    for ns in sorted(os.listdir(base), key=str.lower):
        if NAME_RE.match(ns) and ns != config.siteAssets and os.path.isdir(os.path.join(base, ns)):
            pages = [(name, url_for("displaynspage", namespace=ns, pagename=name)) for name in listpages(os.path.join(base, ns))]
            if pages:
                namespaces.append((ns, pages))
    g.siteName = config.siteName
    g.pagename = "Site Map"
    return render_template("sitemap.html", rootpages=rootpages, namespaces=namespaces, sidebarhtml=showsidebar())

@app.route("/<namespace>/" + config.siteAssets + "/<filename>")
## Send an image or file from asset directory
def sendnsfile(namespace, filename):
    if not NAME_RE.match(namespace):
        abort(404)
    directory = os.path.join(config.siteBase, config.sitePages, namespace, config.siteAssets) #app.config['UPLOAD_FOLDER'])
    logging.info("Asset requested: " + directory + " | " + filename)
    return send_from_directory(directory, filename)  #flask.send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, config.siteStatic), config.siteLogo)

def showsidebar():
    logging.debug('Showsidebar.')
    try:
        with open(pagepath(tuple(config.siteSidebar.split("/"))), "r", encoding="utf-8") as sidebar:
            source = sidebar.read()
    except (OSError, NotFound):
        logging.debug('Unable to open sidebar page ' + config.siteSidebar)
        return ""
    logging.info('returning sidebar')
    return markdown.markdown(source, extensions=SIDEBAR_EXTENSIONS)


if __name__ == "__main__":
    app.run(host=config.siteHostname, port=config.sitePort)