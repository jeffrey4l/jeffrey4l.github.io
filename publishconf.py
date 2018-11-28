#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)

from pelicanconf import *  # noqa

SITEURL = 'http://xcodest.me'
FEED_DOMAIN = SITEURL
RELATIVE_URLS = False

DELETE_OUTPUT_DIRECTORY = True

CNZZ = '1257099267'

GOOGLE_ANALYTICS = 'UA-41808584-2'

DISQUS_SITENAME = 'xcodest'

# Feed
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
