#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os.path
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, 'plugins'))

AUTHOR = u'Jeffrey4l'
SITENAME = u'代码杂货铺'
SITESUBTITLE = u'关注云计算，容器和Linux'
SITEURL = 'http://xcodest.me'
RELATIVE_URLS = True

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'cn'

# Feed generation is usually not desired when developing
FEED_ATOM = None
FEED_ALL_ATOM = None
AUTHOR_FEED_ATOM = None
TAG_FEED_ATOM = None
CATEGORY_FEED_ATOM = None

FEED_RSS = 'feeds/rss.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
AUTHOR_FEED_RSS = None
TAG_FEED_RSS = None
CATEGORY_FEED_RSS = None
RSS_FEED_SUMMARY_ONLY = False
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (
    ('99cloud(九州云)', 'http://99cloud.net'),
    ('陈沙克日志', 'http://chenshake.com/'),
    ('酷壳 - CoolShell.Cn', 'http://coolshell.cn'),
    ('Steven Dake', 'https://sdake.io/'),
    ('SÉBASTIEN HAN', 'https://sebastien-han.fr/'),
    ('技术并艺术着', 'http://blog.csdn.net/quqi99'),
)

# Social widget
SOCIALS = (
    ('Github', 'http://github.com/jeffrey4l'),
    ('Twitter', 'https://twitter.com/Jeffrey4l'),
    ('微博', 'http://weibo.com/jeffrey4l'),
)

YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}.html'

PLUGIN_PATHS = [os.path.join(ROOT, 'plugins'),
                os.path.join(ROOT, 'custom-plugins')]

PLUGINS = ['assets', 'gravatar', 'pelican_gist',
           'neighbors', 'extract_toc',
           'wechat']

SITEMAP = {'format': 'xml'}

STATIC_PATHS = ['images', 'extra', 'static']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}}


MENUITEMS = (
    ('Archives', '/archives.html'),
    ('Tags', '/tags.html'),
    )

USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = 'Others'

AUTHORS_SAVE_AS = ''

ARTICLE_EXCLUDES = ['themes', 'plugins', 'output', 'static', 'custom-plugins']

THEME = 'themes/x'

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_PAGINATION = 25

DISPLAY_PAGES_ON_MENU = True

MARKDOWN = {
        'extension_configs': {
            'admonition': {},
            'extra': {},
            'markdown.extensions.codehilite': {'css_class': 'highlight'},
            'markdown.extensions.extra': {},
            'markdown.extensions.toc': {},
            'markdown_newtab': {},
            'nl2br': {},
            'sane_lists': {},
            'wikilinks': {},
            },
        'output_format': 'html5'
        }
