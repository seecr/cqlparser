## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and 
#    can convert this into other formats.
#    Copyright (C) 2005-2008 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of CQLParser
#
#    CQLParser is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    CQLParser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CQLParser; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import re

#
# This tokenization is based on the CQL specification at http://loc.gov/cql
#
# charString1 is every token except a " ( ) > = < / and spaces
charString1 = r'[^"()>=<\s/]+'
# charString2 is every token surrounded by quotes "", except \"
charString2 = r'(?s)(?P<quot>\").*?((?<!\\)(?P=quot))'
# tokens are charString1, charString2 or ( ) >= <> <= > < = /
tokens = [ r'\(', r'\)', '>=', '<>', '<=', '>', '<', r'\=', r'\/', charString2, charString1 ]

tokenSplitter = re.compile(r'\s*(%s)' % ('|'.join(tokens)))
TOKEN_GROUPNR = 1 # the one and only group.

def tokenStack(cqlQuery):
    return TokenStack(CQLTokenizer(cqlQuery))

class CQLTokenizerException(Exception):
    pass

class CQLTokenizer:

    def __init__(self, text):
        self._text = text.strip()
        self._pointer = 0

    def __iter__(self):
        return self

    def next(self):
        match = tokenSplitter.match(self._text[self._pointer:])
        if match == None:
            if self._pointer != len(self._text):
                raise CQLTokenizerException("Unrecognized token at EOF: " + self._text[self._pointer:])
            raise StopIteration
        self._pointer += match.end(TOKEN_GROUPNR)
        return match.group(TOKEN_GROUPNR)

class TokenStack:
    def __init__(self, tokenizer):
        self._tokens = list(tokenizer)
        self._pointer = 0
        self._bookmarks = Stack()

    def prev(self):
        if self._pointer <= 0:
            raise ProgrammingError
        self._pointer += -1
        return self._tokens[self._pointer]

    def peek(self):
        if not self.hasNext():
            raise StopIteration
        return self._tokens[self._pointer]

    def safePeek(self):
        if not self.hasNext():
            return None
        return self._tokens[self._pointer]

    def next(self):
        result = self.peek()
        self._pointer += 1
        return result

    def safeNext(self):
        if not self.hasNext():
            return None
        return self.next()

    def hasNext(self):
        return self._pointer < len(self._tokens)

    def bookmark(self):
        self._bookmarks.push(self._pointer)

    def revertToBookmark(self):
        self._pointer = self._bookmarks.pop()

    def dropBookmark(self):
        self._bookmarks.pop()

    def __str__(self):
        return "TokenStack: " + str(self._tokens)

class Stack:
    def __init__(self):
        self._stack = []

    def push(self, elem):
        self._stack.append(elem)

    def pop(self):
        result = self._stack[-1]
        self._stack = self._stack[:-1]
        return result
