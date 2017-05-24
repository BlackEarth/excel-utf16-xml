
import os, re, sys, json
from lxml.etree import Entity
from bl.string import String
from bl.text import Text
from bxml import XML
from bxml.builder import Builder

NS = {
    'aid': "http://ns.adobe.com/AdobeInDesign/4.0/",
    'aid5': "http://ns.adobe.com/AdobeInDesign/5.0/",
}
AID_PSTYLE_KEY = "{%(aid)s}pstyle" % NS

def normalize_text(text, quote='"'):
    """Ensures that the lines of the Excel UTF-16 are importable
    + Escape newline and tab characters in the input when between straight quotes.
    + Remove the quotes from the text.
    """
    quoted = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        # print(i, c)
        if c=='\\' and text[i+1]==quote:
            # print('escaped quote,', text[i+1])
            i += 1
        elif c=='\r':
            # print('linebreak')
            text = text[:i] + text[i+1:]
            n = len(text)
            i -= 1
        elif c==quote:
            quoted = not(quoted)
            # print('quote, quoted =', quoted)
            text = text[:i] + text[i+1:]
            n = len(text)
            i -=1 
        elif quoted==True:
            if c=='\n':
                # print('newline')
                text = text[:i] + '\\n' + text[i+1:]
                n = len(text)
                i += 1
            elif c=='\t':
                # print('tab')
                text = text[:i] + '\\t' + text[i+1:]
                n = len(text)
                i += 1
        i += 1
    return text

def excel_key(index):
    """create a key for index by converting index into a base-26 number, using A-Z as the characters."""
    X = lambda n: ~n and X((n // 26)-1) + chr(65 + (n % 26)) or ''
    return X(int(index))

def normalized_text_to_xml(text, delimiter='\t', headers=True, tag='item', tagpl=None, namespace=None, aid=False):
    if aid==True:
        B = Builder(default=namespace, **NS)._
    else:
        B = Builder.single(namespace=namespace)
    if tagpl is None: 
        tagpl = tag+'s'
    lines = text.split('\n')
    if headers==True:
        keys = [String(v).hyphenify() for v in lines.pop(0).split(delimiter)]
    else:
        keys = [excel_key(i) for i in range(len(lines[0].split(delimiter)))]
    root = B(tagpl)
    for line in lines:
        item = B(tag)
        values = [v.replace('\\t', '\t').replace('\\n', '\n') for v in line.split(delimiter)]
        for i in range(len(values)):
            elem = B(keys[i], values[i])
            if aid==True:
                elem.set(AID_PSTYLE_KEY, keys[i])
                elem.append(Entity('#xA'))
            item.append(elem)
        root.append(item)
    return root

def csv_to_xml(fn, encoding='UTF-16', delimiter='\t', quote='"', headers=True, tag='item', namespace=None, aid=False):
    t = Text(fn=fn, encoding=encoding)
    text = normalize_text(t.text, quote=quote)
    x = XML(fn=fn+'.xml', root=normalized_text_to_xml(text, delimiter=delimiter, headers=headers, tag=tag, namespace=namespace, aid=aid))
    return x

if __name__=='__main__':
    args = sys.argv[1:]
    if '--aid' in args:
        aid = True
        _ = args.pop(args.index('--aid'))
    else:
        aid = False
    for fn in args:
        print(fn)
        x = csv_to_xml(fn, aid=aid)
        x.write(canonicalized=False, pretty_print=True)
        print(x.fn)
