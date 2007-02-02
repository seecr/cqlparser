from cqlparser import parseString, CQL_QUERY, SCOPED_CLAUSE, SEARCH_CLAUSE, BOOLEAN, SEARCH_TERM, INDEX, COMPARITOR, UnsupportedCQL, CQLParseException

class ParseException(Exception):
	pass

def compose(node):
	if node.__class__ in [INDEX]:
		assert len(node.children()) == 1
		return node.children()[0]
	if node.__class__ in [SCOPED_CLAUSE, SEARCH_TERM, CQL_QUERY]:
		return " ".join(map(compose, node.children()))
	if node.__class__ == SEARCH_CLAUSE:
		return "".join(map(compose, node.children()))
	if node.__class__ == COMPARITOR:
		assert len(node.children()) == 1
		assert node.children()[0] == '='
		return ':'
	if node.__class__ == BOOLEAN:
		assert len(node.children()) == 1
		return node.children()[0].upper()
	return str(node)

def fromString(aCQLString):
	if aCQLString.strip() == '':
		return ''
	try:
		abstractSyntaxTree = parseString(aCQLString)
	except UnsupportedCQL, e:
		raise ParseException('Unsupported query')
	except CQLParseException, e:
		raise ParseException('Unsupported query')
		
	return compose(abstractSyntaxTree)
