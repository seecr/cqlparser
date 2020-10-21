## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2016, 2018, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2016 Stichting Kennisnet https://www.kennisnet.nl
#
# This file is part of "CQLParser"
#
# "CQLParser" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "CQLParser" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "CQLParser"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import re

from ._cqlexception import CQLTokenizerException

#
# This tokenization is based on the CQL specification at http://loc.gov/cql
#
# charString1 is every token except a " ( ) > = < / and spaces
charString1 = r'[^"()>=<\s/]+'
# charString2 is every token surrounded by quotes "", except \"
charString2 = r'".*?(?:(?<!\\)")'
# tokens are charString1, charString2 or ( ) >= <> <= == > < = /
tokens = [ r'\(', r'\)', '>=', '<>', '<=', '==', '>', '<', r'\=', r'\/', charString2, charString1 ]

tokenSplitter = re.compile(r'(?s)\s*(%s)' % (r'|'.join(tokens)))

def tokenize(text):
    tokens = tokenSplitter.findall(text)
    if len(_withoutWhitespace(text)) != len(_withoutWhitespace(''.join(tokens))):
        raise CQLTokenizerException("Unrecognized token in '%s'" % text.replace("'", r"\'"))
    return tokens


whitespace = re.compile(r"\s+")
def _withoutWhitespace(s):
    return whitespace.sub('', s)

