import codecs
import contextlib
import os

import markdown
import premailer
from pelican import signals


CUR_DIR = os.path.abspath(os.path.dirname(__file__))


MARKDOWN_EXT = [
    'markdown.extensions.codehilite',
    'markdown.extensions.extra',
    'markdown.extensions.meta',
    'markdown.extensions.toc'
]

MARKDOWN_EXT_CONFIG = {
    'markdown.extensions.codehilite': {
        'linenums': False,
        'guess_lang': False,
        'use_pygments': True,
        'noclasses': True
    },
    'markdown.extensions.extra': {
        'BACKLINK_TEXT': ''
    }
}


@contextlib.contextmanager
def safe_open(path, mode):
    with codecs.open(path, mode, 'utf8') as f:
        yield f


def convert(text):
    md = markdown.Markdown(extensions=MARKDOWN_EXT,
                           extension_configs=MARKDOWN_EXT_CONFIG)
    return md.convert(text)


def is_markdown(src_path):
    filename = os.path.basename(src_path)
    name, ext = os.path.splitext(filename)
    return ext in ['.md', '.markdown']


def get_template():
    with safe_open(os.path.join(CUR_DIR, 'template.html'), 'r') as f:
        return f.read()


def add_postfix(filename, postfix):
    name, ext = os.path.splitext(filename)
    return '%s%s%s' % (name, postfix, ext)


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def wechat_output(content_object):

    src_path = content_object.source_path

    if not is_markdown(src_path):
        return

    if "pages" in src_path:
        return

    output = content_object.settings.get('OUTPUT_PATH')

    wechat_output_name = add_postfix(content_object.save_as, '-wechat')

    dest_fullpath = os.path.join(output, wechat_output_name)

    ensure_folder(os.path.dirname(dest_fullpath))

    with safe_open(src_path, 'r') as f:
        md_content = f.read()

    html = convert(md_content)
    tpl = get_template()

    html = tpl % html

    wechat_css = [os.path.join(
        content_object.settings['THEME'],
        'static/css/wechat.css')]

    with safe_open(dest_fullpath, 'w') as f:
        p = premailer.Premailer(
            html,
            external_styles=wechat_css)
        f.write(p.transform())


def register():
    signals.content_object_init.connect(wechat_output)
