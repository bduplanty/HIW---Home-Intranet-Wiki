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

## Branding
siteSidebarPills = True  # True: sidebar links are shown as buttons; False: plain text links
siteLogo = "logo.png"  # file inside siteStatic; replace it or point this at your own image

## CSS
siteCSS = "default.css"  # stylesheet inside siteStatic
