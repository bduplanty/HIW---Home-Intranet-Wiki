#!/usr/bin/env python

from flask import Flask, redirect, send_from_directory
import config
import os
import markdown

# source env/bin/activate

app = Flask(__name__)

@app.route("/")
def index():
    return redirect('/start/')

@app.route("/<pagename>/")
def displaypage(pagename):
    page = open("./Pages/" + pagename + ".md", "r")
    ## Remove me as template should do this
    csspage = open(os.path.join(config.siteBase, 'static', config.siteCSS), "r")
    html = "<html><head><style>" + csspage.read() + "</style></head>"
    ##

    html += markdown.markdown(page.read(), extensions=['extra','wikilinks','toc','admonition'])
    
    return html

@app.route("/_assets/<filename>")
## Send an image or file from asset directory
def sendfile(filename):
    directory = os.path.join(config.siteBase, 'Pages/_assets/') #app.config['UPLOAD_FOLDER'])
    print(directory) ###for debug
    return send_from_directory(directory, filename)  #flask.send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    app.run(host=host, port=port)