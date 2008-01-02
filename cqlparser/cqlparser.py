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

DEFAULTCOMPARITORS = ['=', '>', '<', '>=', '<=', '<>', '==', 'any', 'all', 'adj', 'within', 'encloses', 'exact']

class UnsupportedCQL(Exception):
    def __call__(self, *ignoredArgs):
        raise self

class CQLParseException(Exception):
    pass

class CQLAbstractSyntaxNode(object):

    def __init__(self, *args):
        self._children = args

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s(%s)" % (str(self.__class__).split('.')[-1][:-2], ", ".join(map(repr, self._children)))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._children == other._children

    def children(self):
        return self._children

for aClass in ['CQL_QUERY', 'SCOPED_CLAUSE', 'BOOLEAN', 'SEARCH_CLAUSE', 'SEARCH_TERM', 'INDEX', 'RELATION', 'COMPARITOR', 'MODIFIERLIST', 'MODIFIER', 'TERM', 'IDENTIFIER']:
    exec("""class %s(CQLAbstractSyntaxNode):
    def accept(self, visitor):
        return visitor.visit%s(self)
""" % (aClass, aClass))

def parseString(cqlString, **kwargs):
    from cqltokenizer import tokenStack
    parser = CQLParser(tokenStack(cqlString), **kwargs)
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

class WildCard:
    def __contains__(self, item):
        return True

class CQLParser:
    def __init__(self, tokenstack, supportedModifierNames=WildCard(),
        supportedComparitors = DEFAULTCOMPARITORS):
        self._tokens = tokenstack
        for term in ['_prefix', '_uri', '_modifierValue']:
            setattr(self, term, self._term)
            #(hoewel hier eigenlijk nog een veralgemeniseerde wrap laag omheen zou kunnen)
        self._supportedComparitors = supportedComparitors
        self._supportedModifierNames = supportedModifierNames

    def parse(self):
        if not self._tokens.hasNext():
            raise CQLParseException('No tokens found, at least one token expected.')
        result = self._cqlQuery()
        if self._tokens.hasNext():
            raise CQLParseException('Unexpected token after parsing ([%s], %s).' % (self._tokens.next(), str(result)))
        return result

    def _tryTerms(self, *termFunctions):
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

    def _construct(self, constructor, *termFunctions):
        result = self._tryTerms(*termFunctions)
        if not result:
            return False
        return constructor(*result)

    def _term(self):
        token = self._tokens.safeNext()
        if token and (not token[:1] in ['(', ')', '>', '=', '<', '/']):
            return TERM(token)
        return False

    def _searchTerm(self):
        return self._construct(SEARCH_TERM, self._term)

    def _index(self):
        """index ::= term"""
        return self._construct(INDEX, self._term)

    def _token(self, aToken, caseSensitive = True):
        return Token(self, aToken, caseSensitive)

    def _cqlQuery(self):
        """cqlQuery ::= prefixAssignment cqlQuery | scopedClause"""
        if self._tokens.peek() == ">":
            return \
                self._construct(CQL_QUERY,
                    self._prefixAssignment,
                    self._cqlQuery)
        return \
            self._construct(CQL_QUERY,
                self._scopedClause)

    def _prefixAssignment(self):
        """prefixAssignment ::= '>' prefix '=' uri | '>' uri"""
        return \
            self._construct(UnsupportedCQL("prefixAssignment (>)"),
                self._token('>'),
                self._prefix,
                self._token('='),
                self._uri) or \
            self._construct(UnsupportedCQL("prefixAssignment (>)"),
                self._token('>'),
                self._uri)

    def _scopedClause(self):
        """
        scopedClause ::= scopedClause booleanGroup searchClause | searchClause
        we use:
        scopedClause ::= searchClause booleanGroup scopedClause | searchClause
        """
        #searchClause = self.searchClause()

        head = self._tryTerms(self._searchClause)
        if not head:
            return False
        tail = self._tryTerms(
                self._booleanGroup,
                self._scopedClause)
        if tail:
            return SCOPED_CLAUSE(*(head + tail))
        return SCOPED_CLAUSE(*head)

    def _boolean(self):
        """boolean ::= 'and' | 'or' | 'not' | 'prox'"""
        if not self._tokens.hasNext():
            return False
        token = self._tokens.peek().lower()
        if token == 'prox':
            raise UnsupportedCQL("booleanGroup: 'prox'")
        if token in ['and', 'or', 'not']:
            return BOOLEAN(self._tokens.next().lower())
        return False

    def _booleanGroup(self):
        """
        booleanGroup ::= boolean [ modifierList ]
        we use:
        booleanGroup ::= boolean modifierList | boolean
        """
        #head = self.
        if not self._tokens.hasNext():
            return False
        head = self._tryTerms(self._boolean)
        if not head:
            return False
        tail = self._tryTerms(self._modifierList)
        if tail:
            raise UnsupportedCQL("modifierLists on booleanGroups not supported")
        return head[0]

    def _searchClause(self):
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
                self._construct(SEARCH_CLAUSE,
                    self._token('('),
                    self._cqlQuery,
                    self._token(')'))
        result = self._construct(SEARCH_CLAUSE, self._index, self._relation, self._searchTerm)
        if not result:
            result = self._construct(SEARCH_CLAUSE, self._searchTerm)
        return result

    def _relation(self):
        """
        relation ::= comparitor [modifierList]
        we use:
        relation ::= comparitor modifierList | comparitor
        """
        comparitor = self._comparitor()
        if not comparitor:
            return False
        if self._tokens.safePeek() == '/':
            modifierList = self._modifierList()
            return RELATION(comparitor, modifierList)

        return RELATION(comparitor)

    def _modifierName(self):
        if not self._tokens.hasNext():
            return False

        modifierName = self._tokens.next()
        if modifierName not in self._supportedModifierNames:
            raise UnsupportedCQL("Unsupported ModifierName: %s" % modifierName)
        return TERM(modifierName)

    def _comparitor(self):
        """
        comparitor ::= comparitorSymbol | namedComparitor
        comparitorSymbol ::= '=' | '>' | '<' | '>=' | '<=' | '<>'
        we use a shortcut since most of this is not supported
        """
        if not self._tokens.hasNext():
            return False
        token = self._tokens.peek().lower()
        if not token in DEFAULTCOMPARITORS:
            return False
        if token not in self._supportedComparitors:
            raise UnsupportedCQL('Unsupported comparitor: %s' % token)
        return COMPARITOR(self._tokens.next())

    def _modifierList(self):
        """
        modifierList ::=  modifierList modifier | modifier
        """
        return self._construct(MODIFIERLIST, self._modifier)

    def _modifier(self):
        """
        modifier ::= '/' modifierName [comparitorSymbol modifierValue]
        """
        slashToken = self._tokens.safeNext()
        if not slashToken == '/':
            return False
        return self._construct(MODIFIER, self._modifierName, self._comparitor, self._modifierValue)
