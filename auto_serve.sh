#!/bin/bash
# watchdog is required. To install it pls use following line
#     pip install watchdog
watchmedo auto-restart -d . -p '*.md' -D -R fab reserve
