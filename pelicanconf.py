#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os.path
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, 'plugins'))

AUTHOR = u'Jeffrey4l'
SITENAME = u'Xcodest'
SITEURL = 'http://xcodest.me'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'cn'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('My Git', 'http://github.com/jeffrey4l'),
        )

# Social widget
SOCIAL = (
    ('Github', 'http://github.com/jeffrey4l'),
  )

YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'


PLUGIN_PATHS = [ os.path.join(ROOT, 'plugins')]

PLUGINS = ['assets', 'sitemap', 'gravatar', 'pelican_gist']

SITEMAP= {'format': 'xml'}

STATIC_PATHS = ['images', 'extra/CNAME', 'theme']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True


DISQUS_SITENAME = 'xcodest'

#MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'

MENUITEMS = (
    ('Archives', '/archives.html'),
    )

GOOGLE_ANALYTICS = 'UA-41808584-1'

USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = 'Others'

AUTHORS_SAVE_AS = ''

DISPLAY_CATEGORIES_ON_MENU = False

ARTICLE_EXCLUDES =  ['theme', 'themes', 'plugins', 'output']

THEME = 'themes/gum'

GITHUB_URL = 'http://githbu.com/jeffrey4l'
