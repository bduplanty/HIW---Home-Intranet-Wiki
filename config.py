#!/usr/bin/env python

import os

## Site Settings
siteName = "Home Intranet Wiki"
siteHostname = "0.0.0.0"
sitePort = int(os.environ.get('PORT', 5000))

## Directories
siteBase = os.getcwd()
siteStatic = "static"
sitePages = "Pages"
siteAssets = "_assets"
siteHome = "start"

## CSS
siteCSS = "default.css"  # Not needed?
siteCSSOverride = True
