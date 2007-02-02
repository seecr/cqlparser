## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and 
#    can convert this into other formats.
#    Copyright (C) 2005, 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
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

class CQLAbstractSyntaxNode:

	def __init__(self, *args):
		self._children = args
		self.__repr__ = self.__str__

	def __str__(self):
		return "%s(%s)" % (self.__class__, ", ".join(map(repr, self._children)))

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self._children == other._children
	
	def children(self):
		return self._children
	
for aClass in ['CQL_QUERY', 'SCOPED_CLAUSE', 'BOOLEAN', 'SEARCH_CLAUSE', 'SEARCH_TERM', 'INDEX', 'COMPARITOR']:
	exec("""class %s(CQLAbstractSyntaxNode):
	pass""" % aClass)

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

	def construct(self, constructor, *termFunctions):
		result = []
		self._tokens.bookmark()
		for termFunction in termFunctions:
			term = termFunction()
			if not term:
				self._tokens.revertToBookmark()
				return False
			result.append(term)
		self._tokens.dropBookmark()
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
			raise CQLParseException('Unexpected token after parsing, check for greediness ([%s], %s).' % (self._tokens.next(), str(result)))
		return result

	def cqlQuery(self):
		"""cqlQuery ::= prefixAssignment cqlQuery | scopedClause"""
		return \
			self.construct(CQL_QUERY,
				self.prefixAssignment,
				self.cqlQuery) or \
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
		return \
			self.construct(SCOPED_CLAUSE,
				self.searchClause,
				self.booleanGroup,
				self.scopedClause) or \
			self.construct(SCOPED_CLAUSE,
				self.searchClause)
	
	def boolean(self):
		"""boolean ::= 'and' | 'or' | 'not' | 'prox'"""
		return \
			self.construct(UnsupportedCQL("booleanGroup: 'prox'"),
				self.token('prox')) or \
			self.construct(BOOLEAN, self.token('and', caseSensitive = False)) or \
			self.construct(BOOLEAN, self.token('or', caseSensitive = False)) or \
			self.construct(BOOLEAN, self.token('not', caseSensitive = False))
	
	def booleanGroup(self):
		"""
		booleanGroup ::= boolean [ modifierList ]
		we use:
		booleanGroup ::= boolean modifierList | boolean
		"""
		return \
			self.construct(UnsupportedCQL("modifierLists are not supported"),
				self.boolean,
				self.modifierList) or \
			self.construct(lambda x: x,
				self.boolean)
	
	def modifierList(self):
		return self.token('/')()

	def searchClause(self):
		"""
		searchClause ::=
			'(' cqlQuery ')' | 
			index relation searchTerm |
			searchTerm
		"""
		return \
			self.construct(SEARCH_CLAUSE,
				self.token('('),
				self.cqlQuery,
				self.token(')')) or \
			self.construct(SEARCH_CLAUSE,
				self.index,
				self.relation,
				self.searchTerm) or \
			self.construct(SEARCH_CLAUSE,
				self.searchTerm)
				
	def relation(self):
		"""
		relation ::= comparitor [modifierList]
		we use:
		relation ::= comparitor modifierList | comparitor
		"""
		return \
			self.construct(UnsupportedCQL("modifierLists are not supported"),
				self.comparitor,
				self.modifierList) or \
			self.construct(lambda x: x,
				self.comparitor)
		
	def comparitor(self):
		"""
		comparitor ::= comparitorSymbol | namedComparitor
		comparitorSymbol ::= '=' | '>' | '<' | '>=' | '<=' | '<>'
		we use a shortcut since most of this is not supported
		"""
		return \
			self.construct(COMPARITOR,
				self.token('=')) or \
			self.construct(UnsupportedCQL("Unsupported Relation: >"),
				self.token('>')) or \
			self.construct(UnsupportedCQL("Unsupported Relation: <"),
				self.token('<')) or \
			self.construct(UnsupportedCQL("Unsupported Relation: >="),
				self.token('>=')) or \
			self.construct(UnsupportedCQL("Unsupported Relation: <="),
				self.token('<=')) or \
			self.construct(UnsupportedCQL("Unsupported Relation: <>"),
				self.token('<>'))
			#this needs to be unparsable, not throw an exception.
			#self.construct(UnsupportedCQL("Unsupported Relation: namedComparitor"),
			#	self.term)
		
