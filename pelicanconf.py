#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import sys
sys.path.append('/home/jeffrey/temp/pelican-plugins')

AUTHOR = u'Jeffrey4l'
SITENAME = u'Xcodest'
SITEURL = ''

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
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

#PAGE_PATHS = ['author']

YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'


PLUGIN_PATHS = [ '/home/jeffrey/temp/pelican-plugins']

PLUGINS = ['assets', 'sitemap', 'gravatar']

SITEMAP= {'format': 'xml'}

STATIC_PATHS = ['images', 'extra/CNAME']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
