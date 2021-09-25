#!/usr/bin/env python

import logging
from flask import Flask, redirect, send_from_directory, flash, g, render_template, request, url_for
import config
import os
import markdown
from MarkdownHighlight.highlight import HighlightExtension
from hiwmd import hiwExtension

logging.basicConfig(level=logging.INFO)

# source env/bin/activate

# if wiki:nav?? - display first x lines as navigation? otherwise home only?
# if wiki:footer - replace footer
# extend wikilinks extension to do namespace and ![[]]


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

@app.route("/<pagename>/")
def displaypage(pagename):
    logging.info('Page request(S): ' + pagename)
    page = open("./Pages/" + pagename + ".md", "r")
    logging.info("Sending: " + pagename)

    g.siteName = config.siteName
    g.pagename = pagename
    html = markdown.markdown(page.read(), extensions=['extra','wikilinks','toc','admonition','MarkdownHighlight.highlight:HighlightExtension','hiwmd:hiwExtension'])
    sidebar = showsidebar()
    return render_template("page.html", html=html, sidebarhtml=sidebar)

@app.route("/<namespace>/<pagename>/")
def displaynspage(namespace, pagename):
    logging.info('Page request: ' + pagename)
    page = open("./Pages/" + namespace + "/" + pagename + ".md", "r")
    logging.info("Sending: " + namespace + ":" + pagename)
    g.siteName = config.siteName
    g.pagename = namespace + ":" + pagename
    html = markdown.markdown(page.read(), extensions=['extra','wikilinks','toc','admonition'])
    
    return render_template("page.html", html=html)

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
        sidebar = open("./Pages/wiki/sidebar.md", "r")
    except OSError:
       logging.debug('Unable to open wiki:sidebar.md')
    else:
        sidebarhtml = markdown.markdown(sidebar.read(), extensions=['extra','wikilinks'])
        sidebar.close()
        logging.info('returning sidebar.md')
        return sidebarhtml


if __name__ == "__main__":
    app.run(host=config.siteHostname, port=config.sitePort)