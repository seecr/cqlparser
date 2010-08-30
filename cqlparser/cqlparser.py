# -*- coding: utf-8 -*-
## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
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

DEFAULTCOMPARITORS = ['=', '>', '<', '>=', '<=', '<>', '==', 'any', 'all', 'adj', 'within', 'encloses', 'exact']

class UnsupportedCQL(Exception):
    def __call__(self, *ignoredArgs):
        raise self

class CQLParseException(Exception):
    pass

class RollBack(Exception):
    pass

class CQLAbstractSyntaxNode(object):

    def __init__(self, *args):
        self._children = args

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        #return self.prettyPrint()
        return "%s(%s)" % (str(self.__class__).split('.')[-1][:-2], ", ".join(map(repr, self._children)))

    def prettyPrint(self, offset=0):
        spaces = offset * 4 * ' '
        if len(self._children) == 1 and type(self._children[0] ) == str:
            return spaces + str(self.__class__).split('.')[-1][:-2] + "(" + repr(self._children[0]) + ")"
        result = [spaces + str(self.__class__).split('.')[-1][:-2] + "("]
        result.append(',\n'.join(child.prettyPrint(offset+1) for child in self._children if type(child)!=str))
        result.append(spaces + ")")
        return '\n'.join(result)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._children == other._children

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__class__) ^ hash(self._children)

    def children(self):
        return self._children

    def replaceChildren(self, *args):
        self._children = args

for aClass in ['SCOPED_CLAUSE', 'BOOLEAN', 'SEARCH_CLAUSE', 'SEARCH_TERM', 'INDEX', 'RELATION', 'COMPARITOR', 'MODIFIERLIST', 'MODIFIER', 'TERM', 'IDENTIFIER', 'CQL_QUERY']:
    exec("""class %s(CQLAbstractSyntaxNode):
    def accept(self, visitor):
        return visitor.visit%s(self)
    def name(self):
        return "%s"
""" % (aClass, aClass, aClass))

def findLastScopedClause(aNode):
    if len(aNode._children) == 1 and type(aNode) == SCOPED_CLAUSE:
        return aNode
    return findLastScopedClause(aNode._children[-1])

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
        try:
            result = self._cqlQuery()
        except (RollBack, IndexError):
            result = False
        if self._tokens.hasNext():
            raise CQLParseException('Unexpected token after parsing ([%s], %s).' % (self._tokens.next(), str(result)))
        return result

    def _construct(self, constructor, *termFunctions):
        result = []
        self._tokens.bookmark()
        for termFunction in termFunctions:
            try:
                term = termFunction()
            except (RollBack, IndexError):
                self._tokens.revertToBookmark()
                raise RollBack
            result.append(term)
        self._tokens.dropBookmark()
        return constructor(*result)

    def _term(self):
        token = self._tokens.safeNext()
        if token and (not token[:1] in ['(', ')', '>', '=', '<', '/']):
            if '"' == token[0] == token[-1]:
                token = token[1:-1].replace(r'\"', '"')
            return TERM(token)
        raise RollBack

    def _searchTerm(self):
        return SEARCH_TERM(self._term())

    def _index(self):
        """index ::= term"""
        return INDEX(self._term())

    def _token(self, aToken, caseSensitive = True):
        return Token(self, aToken, caseSensitive)

    def _cqlQuery(self):
        """cqlQuery ::= prefixAssignment cqlQuery | scopedClause"""
        if self._tokens.safePeek() == ">":
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
        head = self._searchClause()
        try:
            self._tokens.bookmark()
            boolGroup = self._booleanGroup()
            scopedClause = self._scopedClause()
            return self.__swapScopedClauses(head, boolGroup, scopedClause)
        except (RollBack, IndexError, StopIteration):
            self._tokens.revertToBookmark()
            return SCOPED_CLAUSE(head)

    def __swapScopedClauses(self, searchClause, booleanGroup, scopedClause):
        if booleanGroup.children()[0] not in ['and', 'not']:
            return SCOPED_CLAUSE(searchClause, booleanGroup, scopedClause)
        if len(scopedClause.children()) == 3:
            childLeft = scopedClause.children()[0]
            childBoolean = scopedClause.children()[1]
            childRight = scopedClause.children()[2]
            nr2 = SCOPED_CLAUSE(searchClause, booleanGroup, childLeft)
            result = SCOPED_CLAUSE(nr2, childBoolean, childRight)
        else:
            result = SCOPED_CLAUSE(searchClause, booleanGroup, scopedClause)
        return result

    def _boolean(self):
        """boolean ::= 'and' | 'or' | 'not' | 'prox'"""
        token = self._tokens.peek()
        if token.lower() in ['and', 'or', 'not']:
            return BOOLEAN(self._tokens.next().lower())
        if token == 'prox':
            raise UnsupportedCQL("booleanGroup: 'prox'")
        raise RollBack

    def _booleanGroup(self):
        """
        booleanGroup ::= boolean [ modifierList ]
        we use:
        booleanGroup ::= boolean modifierList | boolean
        """
        head = self._boolean()
        try:
            self._modifierList()
            raise UnsupportedCQL("modifierLists on booleanGroups not supported")
        except (RollBack, IndexError):
            pass
        return head

    def _searchClause(self):
        """
        searchClause ::=
            '(' cqlQuery ')' |
            index relation searchTerm |
            searchTerm
        """
        if self._tokens.peek() == "(":
            self._tokens.next() # '('
            result = SEARCH_CLAUSE(self._cqlQuery())
            if self._tokens.safeNext() != ')':
                raise RollBack
            return result
        try:
            return self._construct(SEARCH_CLAUSE, self._index, self._relation, self._searchTerm)
        except (RollBack, IndexError):
            return SEARCH_CLAUSE(self._searchTerm())

    def _relation(self):
        """
        relation ::= comparitor [modifierList]
        we use:
        relation ::= comparitor modifierList | comparitor
        """
        comparitor = self._comparitor()
        if self._tokens.peek() == '/':
            return RELATION(comparitor, self._modifierList())
        return RELATION(comparitor)

    def _modifierName(self):
        modifierName = self._tokens.next()
        if modifierName in self._supportedModifierNames:
            return TERM(modifierName)
        raise UnsupportedCQL("Unsupported ModifierName: %s" % modifierName)

    def _comparitor(self):
        """
        comparitor ::= comparitorSymbol | namedComparitor
        comparitorSymbol ::= '=' | '>' | '<' | '>=' | '<=' | '<>'
        we use a shortcut since most of this is not supported
        """
        token = self._tokens.next()
        if token in self._supportedComparitors:
            return COMPARITOR(token)
        if not token in DEFAULTCOMPARITORS:
            raise RollBack
        else:
            raise UnsupportedCQL('Unsupported comparitor: %s' % token)

    def _modifierList(self):
        """
        modifierList ::=  modifierList modifier | modifier
        """
        return MODIFIERLIST(self._modifier())

    def _modifier(self):
        """
        modifier ::= '/' modifierName [comparitorSymbol modifierValue]
        """
        if self._tokens.peek() != '/':
            raise RollBack
        self._tokens.next()
        return self._construct(MODIFIER, self._modifierName, self._comparitor, self._modifierValue)
