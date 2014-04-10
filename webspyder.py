#! /usr/local/bin/python

import argparse
import urllib2
import urlparse
import re
from HTMLParser import HTMLParser

results = {}
depth = 0
maxdepth = 0
domains = {}
verbosity = 0

class SpyderHTMLParser(HTMLParser):
    links = []
    
    def handle_starttag(self, tag, attr):
        if tag != 'a':
            return

        for n in attr:
            if n[0] == 'href':
                self.links.append(n[1])

class SpyderCrawlResult(object):
    url = ''
    result = 0
    
    def __init__(self, url, result):
        self.url = url
        self.result = result

def log(res, url, referer):
    print "%d\t%s\t%s" % (res, url, referer)

def crawl(url, referer=None):
    global results, depth, domains, verbosity

    u = urlparse.urlparse(url)

    # Create absolute URLs
    if u.netloc == '':
        ref = urlparse.urlparse(referer)
        url = urlparse.urljoin(referer, url)
        u = urlparse.urlparse(url)

    # Only hit allowable domains
    if u.netloc not in domains:
        if verbosity > 2:
            print "Foreign link: %s, aborting this leaf." % url
        return
    else:
        if domains[u.netloc] == False:
            if verbosity > 2:
                print "Avoiding link: %s" % url
            return

    # Don't hit the same page twice, but log the result anyway
    if url in results:
        res = results[url]
        if verbosity < 1:
            return
        if res.result != 200 or verbosity > 1:
            log(res.result, url, referer)
        return

    # Don't recurse deeper than maxdepth
    if depth > maxdepth:
        return
    
    depth = depth + 1 
    
    try:
        req = urllib2.urlopen(url)
        code = req.code
    except urllib2.HTTPError as e:
        code = e.code    
    except:
        code = 999
    
    if code == 200:
        parser = SpyderHTMLParser()
        parser.feed(req.read())
        
        for l in parser.links:
            crawl(l, url)
    
    depth = depth - 1
    
    # Stuff the result into our results list and log
    results[url] = SpyderCrawlResult(url, code)
    if code != 200 or verbosity > 0:
        log(code, url, referer)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Traverse websites looking for broken links.')
    parser.add_argument('url', metavar='<url>', nargs='+', help='URLs to start scanning')
    parser.add_argument('--depth', '-d', metavar='N', type=int, default=5, help='Maximum depth to traverse from starting URL.')
    parser.add_argument('--verbose', '-v', action='count', help='Verbosity++')
    
    args = parser.parse_args()

    maxdepth = args.depth
    verbosity = args.verbose
    
    for url in args.url:
        u = urlparse.urlparse(url)
        if u.netloc not in domains or domains[u.netloc] != False:
            domains[u.netloc] = True
            crawl(url)

    print "Finished."
