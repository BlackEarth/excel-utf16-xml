
import os, re, sys, json, logging
from lxml.etree import Entity
from bl.string import String
from bl.text import Text
from bxml import XML
from bxml.builder import Builder

log = logging.getLogger(__name__)

NS = {
    'aid': "http://ns.adobe.com/AdobeInDesign/4.0/",
    'aid5': "http://ns.adobe.com/AdobeInDesign/5.0/",
}
AID_PSTYLE_KEY = "{%(aid)s}pstyle" % NS

def csv_to_data(fn, encoding='UTF-16', delimiter='\t', quote='"', headers=True, omit_empty=True):
    t = Text(fn=fn, encoding=encoding)
    text = normalize_text(t.text, quote=quote)
    lines = text.split('\n')
    if headers==True:
        keys = [String(v).hyphenify().strip('-').resub('-r$', '') for v in lines.pop(0).split(delimiter)]
    else:
        keys = [excel_key(i) for i in range(len(lines[0].split(delimiter)))]
    data = []
    for line in lines:
        item = {}
        values = [v.replace('\\t', '\t').replace('\\n', '\n').replace('\\r', '\n') for v in line.split(delimiter)]
        for i in range(len(values)):
            if values[i].strip() != '' or omit_empty==False:        # omit empty elements
                item[keys[i]] = values[i]
        if len(item.keys()) > 0:
            data.append(item)
    return data

def csv_to_xml(fn, encoding='UTF-16', delimiter='\t', quote='"', headers=True, tag='item', namespace=None, aid=False, omit_empty=True):
    t = Text(fn=fn, encoding=encoding)
    text = normalize_text(t.text, quote=quote)
    root = normalized_text_to_xml(text, delimiter=delimiter, headers=headers, tag=tag, namespace=namespace, aid=aid, omit_empty=omit_empty)
    x = XML(fn=fn+'.xml', root=root)
    return x

def normalize_text(text, quote='"', escape='\\'):
    """Ensures that the lines of the Excel UTF-16 are importable
    + Escape newline and tab characters in the input when between straight quotes.
    + Double quotes are escaped quotes
    + Remove the quotes from the text.
    """
    quoted = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        # log.debug("%d %c" % (i, c))
        if c in [escape, quote] and i < n-1 and text[i+1]==quote:
            # log.debug('escaped quote,', text[i+1])
            text = text[:i] + text[i+1:]
            # i += 1
        elif c=='\r':
            # log.debug('linebreak')
            text = text[:i] + '\\r' + text[i+1:]
            n = len(text)
            i -= 1
        elif c==quote:
            quoted = not(quoted)
            # log.debug('quote, quoted = %r' % quoted)
            text = text[:i] + text[i+1:]
            n = len(text)
            i -=1 
        elif quoted==True:
            if c=='\n':
                # log.debug('newline')
                text = text[:i] + '\\n' + text[i+1:]
                n = len(text)
                i += 1
            elif c=='\t':
                # log.debug('tab')
                text = text[:i] + '\\t' + text[i+1:]
                n = len(text)
                i += 1
        i += 1
    return text

def excel_key(index):
    """create a key for index by converting index into a base-26 number, using A-Z as the characters."""
    X = lambda n: ~n and X((n // 26)-1) + chr(65 + (n % 26)) or ''
    return X(int(index))

def normalized_text_to_xml(text, delimiter='\t', headers=True, tag='item', tagpl=None, 
        namespace=None, aid=False, omit_empty=True):
    if aid==True:
        B = Builder(default=namespace, **NS)._
    else:
        B = Builder.single(namespace=namespace)
    if tagpl is None: 
        tagpl = tag+'s'
    lines = text.split('\n')
    if headers==True:
        keys = [String(v).hyphenify().strip('-').resub('-r$', '') for v in lines.pop(0).split(delimiter)]
    else:
        keys = [excel_key(i) for i in range(len(lines[0].split(delimiter)))]
    root = B(tagpl)
    for line in lines:
        item = B(tag)
        values = [v.replace('\\t', '\t').replace('\\n', '\n').replace('\\r','\n') for v in line.split(delimiter)]
        for i in range(len(values)):
            if values[i].strip() != '' or omit_empty==False:        # omit empty elements
                elem = B(keys[i], values[i])
                if aid==True:
                    elem.set(AID_PSTYLE_KEY, keys[i])
                    elem.append(Entity('#xA'))
                item.append(elem)
        root.append(item)
    return root

# if __name__=='__main__':
#     args = sys.argv[1:]
#     if '--aid' in args:
#         aid = True
#         _ = args.pop(args.index('--aid'))
#     else:
#         aid = False
#     for fn in args:
#         x = csv_to_xml(fn, aid=aid)
#         x.write(canonicalized=False, pretty_print=True)
#         print(x.fn)
