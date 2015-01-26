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
RELATIVE_URLS = True

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

PLUGINS = ['assets', 'gravatar', 'pelican_gist']

SITEMAP= {'format': 'xml'}

STATIC_PATHS = ['images', 'extra/CNAME']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}}


DISQUS_SITENAME = 'xcodest'

#MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'

MENUITEMS = (
    ('Archives', '/archives.html'),
    )

GOOGLE_ANALYTICS = 'UA-41808584-2'

USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = 'Others'

AUTHORS_SAVE_AS = ''

DISPLAY_CATEGORIES_ON_MENU = False

ARTICLE_EXCLUDES =  ['themes', 'plugins', 'output']

THEME = 'themes/x'

GITHUB_URL = 'http://githbu.com/jeffrey4l'

LANDING_PAGE_ABOUT = {
    'title': 'Code for fun',
    'details': '''
<ul>
    <li>Email: zhang.lei.fly(#)gmail.com
</ul>

    '''
}
