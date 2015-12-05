#! /usr/bin/python

import argparse
import urlparse
import urllib2
from time import sleep
from HTMLParser import HTMLParser

# Global State variables
results = {}
depth = 0
maxdepth = 0
domains = {}
verbosity = 0
wait = 0

class SpyderHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    
    def handle_starttag(self, tag, attr):
        if tag != 'a':
            return

        for n in attr:
            if n[0] == 'href':
                self.links.append(n[1])

class SpyderCrawlResult(object):
    
    def __init__(self, url, result):
        self.url = url
        self.result = result

def log(res, url, referer):
    print "%d\t%s\t%s" % (res, url, referer)

# Crawl a URL
def crawl(url, referer=''):
    global results, depth

    # Create an absolute URL, based off the referer if we have to.
    u = urlparse.urlparse(url)
    r = urlparse.urlparse(referer)

    if u.netloc == '':
        if referer == None:
            return # TODO: raise exception - relative URL with no referer!
        domain = r._replace(path="").geturl()
        u = urlparse.urlparse(urlparse.urljoin(referer, url))

    # Don't hit the same page twice
    if u.geturl() in results:
        return

    # Only hit allowable domains
    if u.netloc not in domains:
        if verbosity > 2:
            print "%sForeign link: %s, aborting this leaf." % (' '*depth, u.geturl())
        return
    else:
        if domains[u.netloc] == False:
            if verbosity > 2:
                print "Avoiding link: %s" % u.geturl()
            return

    # Don't recurse deeper than maxdepth
    if maxdepth > 0 and depth > maxdepth:
        return
    
    depth = depth + 1
    
    # Put an empty result in result set, so we don't keep recursing into same URL.
    results[u.geturl()] = None

    # wait for delay, if set
    if wait > 0:
        sleep(wait)
    
    try:
        req = urllib2.urlopen(u.geturl())
        code = req.code
    except urllib2.HTTPError as e:
        code = e.code    
    except:
        code = 999
    
    if code == 200:
        parser = SpyderHTMLParser()
        parser.feed(req.read())
        
        for l in parser.links:
            crawl(l, u.geturl())
    
    depth = depth - 1
    
    # Stuff the result into our results list and log
    results[u.geturl()] = SpyderCrawlResult(u.geturl(), code)
    if code != 200 or verbosity > 1:
        log(code, u.geturl(), referer)

# bootstrap
if __name__ == '__main__':
    # Configure argument parser
    parser = argparse.ArgumentParser(description='Traverse websites looking for broken links.')
    parser.add_argument('url', metavar='<url>', nargs='+', help='URLs to start scanning')
    parser.add_argument('--depth', '-d', metavar='N', type=int, default=0, help='Maximum depth to traverse from starting URL.')
    parser.add_argument('--verbose', '-v', action='count', help='Verbosity++')
    parser.add_argument('--wait','-w', type=int, default=0, help='Time to wait between requests in microseconds')
    args = parser.parse_args()

    # set up global state
    maxdepth = args.depth
    verbosity = args.verbose
    wait = args.wait / 1000.0

    # walk through list of head URLs
    for url in args.url:
        u = urlparse.urlparse(url)
        domains[u.netloc] = True
        crawl(url)

    print("Finished.")

    for i in results:
        if results[i] == None:
            print k