#!/usr/bin/env python

import logging
from flask import Flask, redirect, send_from_directory, flash, g, render_template, request, url_for
import config
import os
import markdown

logging.basicConfig(level=logging.INFO)

# source env/bin/activate

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
    logging.info('Page request: ' + pagename)
    page = open("./Pages/" + pagename + ".md", "r")
    logging.info("Sending: " + pagename)
    ## Remove me as template should do this
   ##csspage = open(os.path.join(config.siteBase, config.siteStatic, config.siteCSS), "r")
   ## html = "<html><head><style>" + csspage.read() + "</style></head>"
    ##
    g.siteName = config.siteName
    g.pagename = pagename
    html = markdown.markdown(page.read(), extensions=['extra','wikilinks','toc','admonition'])
    
    return render_template("page.html", html=html)

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

if __name__ == "__main__":
    app.run(host=config.siteHostname, port=config.sitePort)