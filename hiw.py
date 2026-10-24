#!/usr/bin/env python

import hashlib
import logging
import tempfile
import threading
from datetime import datetime
from flask import Flask, abort, redirect, send_from_directory, flash, g, make_response, render_template, request, url_for
from werkzeug.utils import safe_join
import config
import os
import re
import markdown
from markdown import Extension
from MarkdownHighlight.highlight import HighlightExtension
from hiwmd import hiwExtension

logging.basicConfig(level=logging.INFO)

# source env/bin/activate

# if wiki:nav?? - display first x lines as navigation? otherwise home only?
# if wiki:footer - replace footer

app = Flask(__name__)

@app.route("/")
def index():
    return redirect('/start/')

@app.route("/_assets/<filename>")
## Send an image or file from asset directory
def sendfile(filename):
    directory = os.path.join(config.siteBase, config.sitePages, config.siteAssets) #app.config['UPLOAD_FOLDER'])
    logging.info("Asset requested: " + directory + " | " + filename)
    return send_from_directory(directory, filename)  #flask.send_from_directory

class EscapeHtmlExtension(Extension):
    """Escape raw HTML in page source instead of passing it through."""

    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


MD_EXTENSIONS = ['extra', 'wikilinks', 'toc', 'admonition', 'MarkdownHighlight.highlight:HighlightExtension', 'hiwmd:hiwExtension', EscapeHtmlExtension()]
SIDEBAR_EXTENSIONS = ['extra', 'wikilinks', 'MarkdownHighlight.highlight:HighlightExtension', 'hiwmd:hiwExtension', EscapeHtmlExtension()]
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
EDITOR_COOKIE = "hiw_editor"
EDITOR_COOKIE_AGE = 60 * 60 * 24 * 30


def cleanname(name):
    return re.sub(r'[^\w\- ]', '', name or '').strip()[:40]


def historydir(names):
    return os.path.join(config.siteBase, config.sitePages, config.siteHistory, *names[:-1], names[-1] + ".md")


def lastedit(names, path):
    """Return (editor, datetime) for a page; editor is None if it was never saved through the editor."""
    try:
        newest = sorted(os.listdir(historydir(names)))[-1]
        return newest[17:-3], datetime.strptime(newest[:15], TS_FORMAT)
    except (OSError, IndexError, ValueError):
        pass
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
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)
    hdir = historydir(names)
    os.makedirs(hdir, exist_ok=True)
    snapshot = "{}__{}.md".format(datetime.now().strftime(TS_FORMAT), editor)
    with open(os.path.join(hdir, snapshot), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    logging.info("Saved " + path + " as " + editor)


def renderpage(names, source):
    g.siteName = config.siteName
    g.pagename = ":".join(names)
    g.editurl = url_for("editpage", path="/".join(names))
    g.historyurl = url_for("pagehistory", path="/".join(names))
    g.editor, g.edited = lastedit(names, pagepath(names))
    html = markdown.markdown(source, extensions=MD_EXTENSIONS)
    return render_template("page.html", html=html, sidebarhtml=showsidebar())


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
    cookie = cleanname(request.cookies.get(EDITOR_COOKIE))
    editor = cookie
    error = None
    base = pageversion(names)
    if request.method == "POST":
        content = request.form.get("content", "").replace("\r\n", "\n")
        editor = cleanname(request.form.get("name")) or cookie
        if not editor:
            error = "Please enter your name."
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
                response.set_cookie(EDITOR_COOKIE, editor, max_age=EDITOR_COOKIE_AGE, samesite="Lax")
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

@app.route("/<namespace>/_assets/<filename>")
## Send an image or file from asset directory
def sendnsfile(namespace, filename):
    directory = os.path.join(config.siteBase, config.sitePages, namespace, config.siteAssets) #app.config['UPLOAD_FOLDER'])
    logging.info("Asset requested: " + directory + " | " + filename)
    return send_from_directory(directory, filename)  #flask.send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, config.siteStatic),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

def showsidebar():
    logging.debug('Showsidebar.')
    try:
        with open(os.path.join(config.siteBase, config.sitePages, "wiki", "sidebar.md"), "r", encoding="utf-8") as sidebar:
            source = sidebar.read()
    except OSError:
        logging.debug('Unable to open wiki:sidebar.md')
        return ""
    logging.info('returning sidebar.md')
    return markdown.markdown(source, extensions=SIDEBAR_EXTENSIONS)


if __name__ == "__main__":
    app.run(host=config.siteHostname, port=config.sitePort)