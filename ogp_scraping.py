from html.parser import HTMLParser
import urllib.request
import re
import json

class OGP(HTMLParser):
    """
    Parser to retrieve OGP-related meta tags.
    """

    def __init__(self):
        super().__init__()
        self.progress_tag = None
        self.data = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.progress_tag = 'title'
        elif tag == 'meta':
            self.progress_tag = 'meta'
            d = dict(attrs)
            if d.get('name') != None:
                key = d.get('name')
            elif d.get('property') != None:
                key = d.get('property')
            else:
                return
            content = d.get('content')
            if content == None:
                return
            if key == 'description':
                self.data['description'] = content
            elif self.subarray(key, 'og:(.+)', 'ogp', content):
                pass
            elif self.subarray(key, 'twitter:(.+)', 'twitter', content):
                pass
            else: self.subarray(key, 'fb:(.+)', 'facebook', content)

    def handle_data(self, data):
        if self.progress_tag == 'title':
            self.data['title'] = data
            self.progress_tag = None

    def subarray(self, name, r, data_name, content):
        m = re.fullmatch(r, name)
        if m == None:
            return False
        key = m.group(1)
        if self.data.get(data_name) == None:
            self.data[data_name] = {}
        self.data[data_name][key] = content
        return True

def get_urllist(path):
    """
    Retrieves a list of URLs from a file.
    """
    try:
        f = open(path, 'r')
        list = []
        for line in f.readlines():
            m = re.match('[ \t]*(#?)[ \t]*(https?://.+)', line)
            if m == None or m.group(1) == '#':
                continue
            list.append(m.group(2))
        f.close()
        return list
    except Exception as e:
        print("Exception: {0} {1}".format(type(e), e))
    return None

def get_html(url):
    """
    Get HTML from a URL.
    """
    try:
        fp = urllib.request.urlopen(url)
        html = fp.read().decode("utf8")
        fp.close()
        return html
    except Exception as e:
        print("Exception: {0} {1}".format(type(e), e))
    return None

def output_json(path, json):
    """
    """
    try:
        f = open(path, 'w')
        f.write(json)
        f.close()
    except Exception as e:
        print("Exception: {0} {1}".format(type(e), e))

if __name__ == '__main__':
    result = []
    for url in get_urllist('urls.txt'):
        parser = OGP()
        parser.feed(get_html(url))
        result.append(parser.data)
    output_json('ogp.json', json.dumps(result))