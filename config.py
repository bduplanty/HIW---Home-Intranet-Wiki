#!/usr/bin/env python

import os

## Site Settings
siteName = "Home Intranet Wiki"
siteHostname = "0.0.0.0"
sitePort = int(os.environ.get('PORT', 5001))

## Directories
siteBase = os.getcwd()
siteStatic = "static"
sitePages = "Pages"
siteAssets = "_assets"
siteHistory = ".history"  # under sitePages; one snapshot per save
siteHome = "start"

## CSS
siteCSS = "default.css"  # Not needed?
siteCSSOverride = True
