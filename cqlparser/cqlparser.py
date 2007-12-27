## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
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
#    along with $PROGRAM; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

class UnsupportedCQL(Exception):
    def __call__(self, *ignoredArgs):
        raise self

class CQLParseException(Exception):
    pass

class CQLAbstractSyntaxNode(object):

    def __init__(self, *args):
        self._children = args
        self.__repr__ = self.__str__

    def __str__(self):
        return "%s(%s)" % (self.__class__, ", ".join(map(repr, self._children)))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._children == other._children

    def children(self):
        return self._children

for aClass in ['CQL_QUERY', 'SCOPED_CLAUSE', 'BOOLEAN', 'SEARCH_CLAUSE', 'SEARCH_TERM', 'INDEX', 'RELATION', 'COMPARITOR', 'MODIFIER']:
    exec("""class %s(CQLAbstractSyntaxNode):
    def accept(self, visitor):
        visitor.visit%s(self)
""" % (aClass, aClass))

def parseString(cqlString):
    from cqltokenizer import tokenStack
    parser = CQLParser(tokenStack(cqlString))
    return parser.parse()

class Token:
    def __init__(self, parser, token, caseSensitive = True):
        self._parser = parser
        self._token = token
        self._caseSensitive = caseSensitive

    def __call__(self):
        #TODO refactor
        nextToken = self._parser._tokens.safeNext()
        if not nextToken:
            return False

        if not self._caseSensitive:
            return nextToken.lower() == self._token.lower() and self._token.lower()
        if nextToken == self._token:
            return self._token
        return False

class CQLParser:
    def __init__(self, tokenstack):
        self._tokens = tokenstack
        for term in ['prefix', 'uri', 'modifierName', 'modifierValue']:
            setattr(self, term, self.term)
            #(hoewel hier eigenlijk nog een veralgemeniseerde wrap laag omheen zou kunnen)

    def tryTerms(self, *termFunctions):
        result = []
        self._tokens.bookmark()
        for termFunction in termFunctions:
            term = termFunction()
            if not term:
                self._tokens.revertToBookmark()
                return False
            result.append(term)
        self._tokens.dropBookmark()
        return result

    def construct(self, constructor, *termFunctions):
        result = self.tryTerms(*termFunctions)
        if not result:
            return False
        return constructor(*result)

    def term(self):
        token = self._tokens.safeNext()
        if token and (not token[:1] in ['(', ')', '>', '=', '<', '/']):
            return token
        return False

    def searchTerm(self):
        return self.construct(SEARCH_TERM, self.term)

    def index(self):
        """index ::= term"""
        return self.construct(INDEX, self.term)

    def token(self, aToken, caseSensitive = True):
        return Token(self, aToken, caseSensitive)

    def parse(self):
        result = self.cqlQuery()
        if self._tokens.hasNext():
            raise CQLParseException('Unexpected token after parsing, check parser for greediness ([%s], %s).' % (self._tokens.next(), str(result)))
        return result

    def cqlQuery(self):
        """cqlQuery ::= prefixAssignment cqlQuery | scopedClause"""
        if not self._tokens.hasNext():
            return False
        if self._tokens.peek() == ">":
            return \
                self.construct(CQL_QUERY,
                    self.prefixAssignment,
                    self.cqlQuery)
        return \
            self.construct(CQL_QUERY,
                self.scopedClause)

    def prefixAssignment(self):
        """prefixAssignment ::= '>' prefix '=' uri | '>' uri"""
        return \
            self.construct(UnsupportedCQL("prefixAssignment (>)"),
                self.token('>'),
                self.prefix,
                self.token('='),
                self.uri) or \
            self.construct(UnsupportedCQL("prefixAssignment (>)"),
                self.token('>'),
                self.uri)

    def scopedClause(self):
        """
        scopedClause ::= scopedClause booleanGroup searchClause | searchClause
        we use:
        scopedClause ::= searchClause booleanGroup scopedClause | searchClause
        """
        #searchClause = self.searchClause()

        head = self.tryTerms(self.searchClause)
        if not head:
            return False
        tail = self.tryTerms(
                self.booleanGroup,
                self.scopedClause)
        if tail:
            return SCOPED_CLAUSE(*(head + tail))
        return SCOPED_CLAUSE(*head)

    def boolean(self):
        """boolean ::= 'and' | 'or' | 'not' | 'prox'"""
        if not self._tokens.hasNext():
            return False
        token = self._tokens.peek().lower()
        if token == 'prox':
            raise UnsupportedCQL("booleanGroup: 'prox'")
        if token in ['and', 'or', 'not']:
            return BOOLEAN(self._tokens.next().lower())
        return False

    def booleanGroup(self):
        """
        booleanGroup ::= boolean [ modifierList ]
        we use:
        booleanGroup ::= boolean modifierList | boolean
        """
        #head = self.
        if not self._tokens.hasNext():
            return False
        head = self.tryTerms(self.boolean)
        if not head:
            return False
        tail = self.tryTerms(self.modifierList)
        if tail:
            raise UnsupportedCQL("modifierLists on booleanGroups not supported")
        return head[0]

    def searchClause(self):
        """
        searchClause ::=
            '(' cqlQuery ')' |
            index relation searchTerm |
            searchTerm
        """
        if not self._tokens.hasNext():
            return False
        if self._tokens.peek() == "(":
            return \
                self.construct(SEARCH_CLAUSE,
                    self.token('('),
                    self.cqlQuery,
                    self.token(')'))
        head = self.tryTerms(self.term)
        if not head:
            return False
        tail = self.tryTerms(
                self.relation,
                self.searchTerm)
        if tail:
            return SEARCH_CLAUSE(*([INDEX(term) for term in head] + tail))
        return SEARCH_CLAUSE(*[SEARCH_TERM(term) for term in head])

    def relation(self):
        """
        relation ::= comparitor [modifierList]
        we use:
        relation ::= comparitor modifierList | comparitor
        """
        comparitor = self.comparitor()
        if not comparitor:
            return False
        if self._tokens.safePeek() == '/':
            modifierList = self.modifierList()
            return RELATION(comparitor, modifierList)

        return RELATION(comparitor)



    def comparitor(self):
        """
        comparitor ::= comparitorSymbol | namedComparitor
        comparitorSymbol ::= '=' | '>' | '<' | '>=' | '<=' | '<>'
        we use a shortcut since most of this is not supported
        """
        if not self._tokens.hasNext():
            return False
        token = self._tokens.peek()
        if token == '=':
            return COMPARITOR(self._tokens.next())
        if token.lower() in ['any', 'exact']:
            return COMPARITOR(self._tokens.next())
        if token in ['>', '<', '>=', '<=', '<>']:
            raise UnsupportedCQL("Unsupported ComparitorSymbol: %s" % token)
        #this is a bit of a footnote at the definition of charString1 and defines the term "identifier" (namedComparitor is an identifier)
        return False

    def _isfloat(self, s):
        return s.replace('.', '', 1).isdigit()

    def modifierList(self):
        """
        modifierList ::=  modifierList modifier | modifier
        modifier ::= '/' modifierName [comparitorSymbol modifierValue]
        we disallow modifierLists with more then one modifier.
        """
        token = self._tokens.safeNext()
        if not token == '/':
            return False
        modifierName = self.modifierName() #term
        if not modifierName:
            raise CQLParseException('Invalid CQL')
        if modifierName != "boost":
            raise UnsupportedCQL('Only "boost" allowed as modifier')

        token = self._tokens.safePeek()
        if token == '=':
            comparitorSymbol = self._tokens.next()
        else:
            raise UnsupportedCQL("Unsupported ComparitorSymbol: %s" % token)

        modifierValue = self.modifierValue() #term
        if not modifierValue:
            raise CQLParseException('Invalid CQL')
        if not self._isfloat(modifierValue):
            raise UnsupportedCQL("Modifiervalue should be a number")

        return MODIFIER(modifierName, comparitorSymbol, modifierValue)


"""
relation: modifierList
dc.title any /boost=5   als enige mogelijk
"""