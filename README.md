# WebSpyder

    usage: webspyder.py [-h] [--depth N] [--verbose] <url> [<url> ...]
    
    positional arguments:
      <url>            URLs to start scanning
    
    optional arguments:
      -h, --help       show this help message and exit
      --depth N, -d N  Maximum depth to traverse from starting URL.
      --verbose, -v    Raise verbosity (use multiple times for more noise)
      --wait N, -w N   Time to wait between requests in microseconds

## Verbosity levels

0. Only show non-200 responses for links once.
1. Show non-200 responses for links multiple times.
2. Show all responses (include 200) for links multiple times.
3. Report foreign links and links in the avoid list.

## Bugs

* We show some url/referer pairs multiple times with verbosity > 0
* No way to exclude certain links. The code is there but the UI isn't.
