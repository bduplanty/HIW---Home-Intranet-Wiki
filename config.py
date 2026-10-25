#!/usr/bin/env python

import os

## Site Settings
siteName = "Home Intranet Wiki"  # title shown in the top bar and the browser tab; any text
siteHostname = "0.0.0.0"  # address to listen on: "0.0.0.0" = every device on your network, "127.0.0.1" = this computer only
sitePort = int(os.environ.get('PORT', 5001))  # port to listen on; set the PORT environment variable to override, e.g. PORT=8080 python3 hiw.py

## Directories
siteBase = os.getcwd()  # folder that contains sitePages; defaults to where you start the server, so run it from the project folder
siteStatic = "static"  # folder (inside the project) holding the stylesheet, logo and editor files
sitePages = "Pages"  # folder (inside siteBase) holding the wiki pages; one .md file per page, subfolders are namespaces
siteAssets = "_assets"  # name of the folders holding images and files; also the URL prefix they are served from (/_assets/..., /<namespace>/_assets/...)
siteHistory = ".history"  # folder (inside sitePages) holding one saved copy per edit; keep the leading dot to hide it from the site map
siteHome = "start"  # page opened at "/"; a page name without .md, e.g. "start"
siteSidebar = "wiki/sidebar"  # page shown in the left sidebar, as "page" or "namespace/page"; a missing page just gives an empty sidebar

## Editing
siteEditorCookie = "hiw_editor"  # name of the browser cookie that remembers who is editing; change only if it clashes with another site on the same host
siteEditorCookieDays = 30  # days the editor's name is remembered (renewed on every save); 0 = until the browser closes

## Branding
siteSidebarPills = True  # True: sidebar links are shown as buttons; False: plain text links
siteLogo = "logo.png"  # image in siteStatic used in the top bar and as the browser tab icon; PNG, SVG or ICO

## CSS
siteCSS = "default.css"  # stylesheet inside siteStatic; copy default.css, edit it and point this at the copy to restyle the site
