longestline = ''
for line in open('meresco3.queries'):
    if len(line) > len(longestline):
        longestline = line

from urllib import unquote_plus
from urlparse import urlparse, parse_qs
print unquote_plus(parse_qs(urlparse(longestline).query)['query'][0])
