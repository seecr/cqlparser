longestline = ''
for line in open('meresco3.queries'):
    if len(line) > len(longestline):
        longestline = line

from urllib.parse import unquote_plus
from urllib.parse import urlparse, parse_qs
print(unquote_plus(parse_qs(urlparse(longestline).query)['query'][0]))
