#! /usr/local/bin/python

import argparse
import urllib2

results = {}
depth = 0

class crawlResult(object):
    url = ''
    result = 0
    
    def __init__(self, url, result):
        self.url = url
        self.result = result

def log(res, url, referer):
    print "%d: %s" % (res, url)
    print "\t%s" % referer

def crawl(url, referer=None):
    global results, depth

    # Don't hit the same page twice, but log the result anyway
    if url in results:
        res = results[url]
        log(res.result, url, referer)
        return
    
    try:
        req = urllib2.urlopen(url)
        code = req.code
    except urllib2.HTTPError as e:
        code = e.code    
    
    # Stuff the result into our results list and log
    results[url] = crawlResult(url, code)
    log(code, url, referer)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Traverse websites looking for broken links.')
    parser.add_argument('url', metavar='<url>', nargs='+', help='URLs to start scanning')
    parser.add_argument('--depth', '-d', metavar='N', type=int, default=5, help='Maximum depth to traverse from starting URL.')
    
    args = parser.parse_args()
    
    for url in args.url:
        crawl(url)
    
    print "Finished."
