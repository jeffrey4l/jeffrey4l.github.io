#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import sys
sys.path.append('/home/jeffrey/temp/pelican-plugins')

AUTHOR = u'Jeffrey4l'
SITENAME = u'Xcodest'
SITEURL = 'http://xcodest.me'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'cn'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = True
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('My Git', 'http://github.com/jeffrey4l'),
        )

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

#PAGE_PATHS = ['author']

YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'


PLUGIN_PATHS = [ '/home/jeffrey/temp/pelican-plugins']

PLUGINS = ['assets', 'sitemap', 'gravatar']

SITEMAP= {'format': 'xml'}

STATIC_PATHS = ['images', 'extra/CNAME', 'theme']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True


DISQUS_SITENAME = u'xcodest'

#MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'

MENUITEMS = (
    ('Home', '/index.html'),
    ('Archives', '/archives.html'),
    )

GOOGLE_ANALYTICS = 'UA-41808584-1'

USE_FOLDER_AS_CATEGORY = True

AUTHORS_SAVE_AS = ''

DISPLAY_CATEGORIES_ON_MENU = False

THEME_STATIC_DIR = 'themes'
THEME = 'theme/xcodest'

ARTICLE_EXCLUDES =  ['theme']
