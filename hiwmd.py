"""Html HIW extension for Markdown.

Deals with:
  ![[image.jpg|300]]  - like obsidian, sets size -- https://help.obsidian.md/How+to/Embed+files
    one setting is width?
    two seetings is hightxwidth
    px defailt
    deal with percents?

  [[ns:page]]

Based and exapnded on the wikikinks extention
"""

'''
WikiLinks Extension for Python-Markdown
======================================

Converts [[WikiLinks]] to relative links.

See <https://Python-Markdown.github.io/extensions/wikilinks>
for documentation.

Original code Copyright [Waylan Limberg](http://achinghead.com/).

All changes Copyright The Python Markdown Project

License: [BSD](https://opensource.org/licenses/bsd-license.php)

'''

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re
import logging

logging.basicConfig(level=logging.INFO)

# Global Vars
NSLINK_RE =r'\[{2}(.*?)\:(.*?)\]{2}'
NSLINKT_RE =r'\[{2}(.*?)\:(.*?)\|(.*?)\]{2}'
NSLINKTA_RE = r'\[{2}([^:].[^:]*)\|(.*?)\]{2}'
IMAGENSIZE_RE =r'\!\[{2}(.*?)\]{2}' 
IMAGESSIZE_RE =r'\!\[{2}(.*?)\|(.*?)\]{2}'
IMAGEMSIZE_RE =r'\!\[{2}(.*?)\|(.*?)x(.*?)\]{2}'
#NS example - https://regex101.com/r/Ycdx5c/1
#NS with title - https://regex101.com/r/4KygKW/1
#NSTA - allow for root links with title
# https://regex101.com/r/dcvsJM/1
# embeded and single size == width
# https://regex101.com/r/rD4fbj/1
# embded and multiple size 300x200


def build_url(label, base, end):
    """ Build a url from the label, a base, and an end. """
    clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '{}{}{}'.format(base, clean_label, end)


class hiwExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'base_url': ['/', 'String to append to beginning or URL.'],
            'end_url': ['', 'String to append to end of URL.'],
            'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md

        # append to end of inline patterns
        wikilinkNSPattern = hiwInlineProcessor(NSLINK_RE, self.getConfigs())
        wikilinkNSPattern.md = md
        md.inlinePatterns.register(wikilinkNSPattern, 'nspattern', 75)
        logging.info("hiw NS registered")

        wikilinkNSTPattern = hiwInlineProcessor(NSLINKT_RE, self.getConfigs())
        wikilinkNSTPattern.md = md
        md.inlinePatterns.register(wikilinkNSTPattern, 'nstpattern', 76)
        logging.info("hiw NS-T registered")

        wikilinkNSTAPattern = hiwInlineProcessor(NSLINKTA_RE, self.getConfigs())
        wikilinkNSTAPattern.md = md
        md.inlinePatterns.register(wikilinkNSTAPattern, 'nstapattern', 77)
        logging.info("hiw NS-TA registered")

        wikilinkEmbedMultiSizePattern = hiwembedInlineProcessor(IMAGEMSIZE_RE, self.getConfigs())
        wikilinkEmbedMultiSizePattern.md = md
        md.inlinePatterns.register(wikilinkEmbedMultiSizePattern, 'embedmultisize', 80)
        logging.info("embedmultisize registered")

        wikilinkEmbedWidthSizePattern = hiwembedInlineProcessor(IMAGESSIZE_RE, self.getConfigs())
        wikilinkEmbedWidthSizePattern.md = md
        md.inlinePatterns.register(wikilinkEmbedWidthSizePattern, 'embedwithsize', 79)
        logging.info("embedwidthsize registered")

        wikilinkEmbedNoSizePattern = hiwembedInlineProcessor(IMAGENSIZE_RE, self.getConfigs())
        wikilinkEmbedNoSizePattern.md = md
        md.inlinePatterns.register(wikilinkEmbedNoSizePattern, 'embednosize', 78)
        logging.info("embednosize registered")

class hiwInlineProcessor(InlineProcessor):
    def __init__(self, pattern, config):
        super().__init__(pattern)
        self.config = config

    def handleMatch(self, m, data):
        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()

            if self.pattern == NSLINKTA_RE:
                ns = ''
                page = m.group(1).strip()
                label = m.group(2).strip()
            else:
                ns = m.group(1).strip()
                page = m.group(2).strip()
                if self.pattern == NSLINKT_RE:
                    label = m.group(3).strip()
                else:
                    label = ns + ':' + page 
            if ns > '':
                pagepath = ns + '/' + page
            else:
                pagepath = page
            url = self.config['build_url'](pagepath, base_url, end_url)
            a = etree.Element('a')
            a.text = label
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a, m.start(0), m.end(0)

    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if 'wiki_base_url' in self.md.Meta:
                base_url = self.md.Meta['wiki_base_url'][0]
            if 'wiki_end_url' in self.md.Meta:
                end_url = self.md.Meta['wiki_end_url'][0]
            if 'wiki_html_class' in self.md.Meta:
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class

class hiwembedInlineProcessor(InlineProcessor):
    def __init__(self, pattern, config):
        super().__init__(pattern)
        self.config = config

    def handleMatch(self, m, data):
        if m.group(1).strip():
            base_url, end_url, html_class = self._getMeta()
            image = m.group(1).strip()
            if self.pattern == IMAGENSIZE_RE:
                width = ''
            else: 
                width = m.group(2).strip()
            if self.pattern == IMAGEMSIZE_RE:
                height = m.group(3).strip()
            else:
                height = ''
            url = self.config['build_url'](image, base_url, end_url)
            logging.info("embed: "+image+' at width'+width+' height'+height)
            a = etree.Element('img')
            a.text = image
            a.set('src', url)
            #if html_class:
            #    a.set('class', html_class)
            a.set('alt', image)
            if width > '':
                a.set('width', width)
            if height > '':
                a.set('height', height)
        else:
            a = ''
        return a, m.start(0), m.end(0)

    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if 'wiki_base_url' in self.md.Meta:
                base_url = self.md.Meta['wiki_base_url'][0]
            if 'wiki_end_url' in self.md.Meta:
                end_url = self.md.Meta['wiki_end_url'][0]
            if 'wiki_html_class' in self.md.Meta:
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class


def makeExtension(**kwargs):  # pragma: no cover
    return hiwExtension(**kwargs)
